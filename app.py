import streamlit as st
import page_config 
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from automatic_athena_download import traer_df
from lib import *
import base64

page_config.run()


# clientes= traer_df('SELECT * FROM processed_customers')
# order_items= traer_df('SELECT * FROM processed_order_items')
# products= traer_df('SELECT * FROM processed_products')
# vendedores= traer_df('SELECT * FROM processed_sellers')

# if 'datosleidos' not in st.session_state:
#   st.session_state['datosleidos'] = True
#   st.session_state['order_items'] =pd.read_csv('csv normalizados\csv normalizados\Order_itemsNor.csv', infer_datetime_format = True)
#   st.session_state['products'] = pd.read_csv('csv normalizados\csv normalizados\ProductsNor.csv')
#   st.session_state['sellers'] = pd.read_csv(".\csv normalizados\csv normalizados\SellersNor.csv",delimiter = ',',encoding = "utf-8")
#   st.session_state['customers'] = pd.read_csv(".\csv normalizados\csv normalizados\CustomersNor.csv",delimiter = ',',encoding = "utf-8")

#Carga de datos a session si no existen
load_data()


order_items= st.session_state['order_items']
products  = st.session_state['products']
vendedores = st.session_state['sellers']
clientes = st.session_state['customers']



st.title(":bar_chart: Olist Dashboard")
st.markdown("##")
st.markdown("""---""")

st.sidebar.header('User Input Features')
a =["All","2016","2017","2018"]
selected_year = st.sidebar.selectbox('Year', a)

#--------------------------------------------------------------------------------------------------------

order_items['shipping_limit_date'] = order_items['shipping_limit_date'].apply(pd.to_datetime).dt.date
#creo columna mes
order_items['month'] = order_items.shipping_limit_date.apply(lambda x: x.month)
#creo columna año
order_items['Year'] = order_items.shipping_limit_date.apply(lambda x: x.year)
#creo columna mes/año
order_items['month_year'] = order_items['month'].astype(str).apply(lambda x: '0' + x if len(x) == 1 else x)
order_items['month_year'] = order_items['Year'].astype(str) + '-' + order_items['month_year'].astype(str)
#creating year month column
order_items['month_y'] = order_items['shipping_limit_date'].map(lambda date: 100*date.year + date.month)
#ordeno valores
order_items.sort_values('month_y', inplace=True)
#agrego columna total

order_items['total_price'] = order_items['price'] + order_items['freight_value']
order_items_fil = order_items.loc[(order_items['month_year']<'2018-08')]


product_vendidos = order_items_fil.groupby(['month_year','Year']).count()
product_vendidos.reset_index(inplace=True)



order_product = pd.merge(order_items_fil,products, on=["product_id"])


maximo = st.sidebar.slider("Sales greater than ", 10, 8000)
precio= st.sidebar.slider("Price greater than ", 1, 500)

prod_cat=order_product.pivot_table(values=['price', 'order_id'], index=['product_category_name']
                          , aggfunc={'price': 'sum', 'order_id': 'nunique'})
prod_cat["ord_size($R)"]=prod_cat["price"]/prod_cat["order_id"]
prod_cat["price"]=prod_cat["price"]/1000
prod_cat.sort_values(by='price', ascending = False, inplace = True)
prod_cat_top=prod_cat.rename(columns={'order_id':'no_of_order','price':"revenue($R1000)"}).head(30)
prod_cat.reset_index(inplace=True)
prod_cat=prod_cat[prod_cat.order_id>int(maximo)]
prod_cat=prod_cat[prod_cat.price>float(precio)]


order_items['shipping_limit_date'] = order_items['shipping_limit_date'].apply(pd.to_datetime).dt.date
#creo columna mes
order_items['month'] = order_items.shipping_limit_date.apply(lambda x: x.month)
#creo columna año
order_items['Year'] = order_items.shipping_limit_date.apply(lambda x: x.year)
#creo columna mes/año
order_items['month_year'] = order_items['month'].astype(str).apply(lambda x: '0' + x if len(x) == 1 else x)
order_items['month_year'] = order_items['Year'].astype(str) + '-' + order_items['month_year'].astype(str)
#creating year month column
order_items['month_y'] = order_items['shipping_limit_date'].map(lambda date: 100*date.year + date.month)
#ordeno valores
order_items.sort_values('month_y', inplace=True)


#agrego columna total
order_items['total_price'] = order_items['price'] + order_items['freight_value']
order_items_fil = order_items.loc[(order_items["month_year"] >= '2017-01') & (order_items['month_year']<'2018-08')]
precio_cant_mes=order_items_fil.groupby(['month_year','Year']).agg({'total_price':'sum', 'order_id':'count'})
precio_cant_mes ['promedio'] = precio_cant_mes['total_price'] / precio_cant_mes['order_id']
precio_cant_mes.reset_index(inplace=True)

#----------------------------------------------------------------------------------------
if(selected_year=='All'):
    precio_cant_mes2=precio_cant_mes
else:
    precio_cant_mes2=precio_cant_mes[precio_cant_mes.Year==int(selected_year)]
figticketprom = px.bar(precio_cant_mes2, y='promedio', x='month_year', text_auto='.3s',
            color_discrete_sequence=["cadetblue", "red","green"],labels=dict(month_year="month-year", promedio="average R$"))
figticketprom.update_traces(textfont_size=15, textangle=0, textposition="outside", cliponaxis=False)
figticketprom.add_shape(type="line",
    x0='2017-01', y0=140,
    x1='2018-08', y1=140,
    line=dict(
        color="blue",
        width=3,
        dash="dashdot"))
figticketprom.update_layout(
    font=dict(
        family="Courier New, monospace",
        size=15 # Set the font size here
        
    ))

prod_cat=prod_cat.rename(columns={'ord_size($R)':'Price'})
figbubble = px.scatter(prod_cat, x='Price', y="order_id",
	         size="order_id", color="product_category_name",
                  log_x=True, size_max=60, labels=dict(order_id="products sold"))
figbubble.update_layout(
    font=dict(
        family="Courier New, monospace",
        size=15 # Set the font size here
        
    ))

volumen=order_items_fil.groupby(['month_year','Year']).agg({'total_price':'sum', 'order_id':'count'})
volumen.reset_index(inplace=True)
if(selected_year=='All'):
    volumen_fil=volumen
else:
    volumen_fil=volumen[volumen.Year==int(selected_year)]

figvolumen = px.bar(volumen_fil, y='total_price', x='month_year', text_auto='.3s',
            color_discrete_sequence=["cadetblue", "red","green"])
figvolumen.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
figvolumen.update_layout(
    font=dict(
        family="Courier New, monospace",
        size=15 # Set the font size here
        
    ))


if selected_year=='All':
    df=product_vendidos
if selected_year=='2016':
    df=product_vendidos[product_vendidos.Year == 2016]
if selected_year=='2017':
    df=product_vendidos[product_vendidos.Year == 2017]
if selected_year=='2018':
    df=product_vendidos[product_vendidos.Year == 2018]        
 


fig = px.bar(df, y='order_id', x='month_year', text_auto='.3s',
             color_discrete_sequence=['cadetblue', "red"])
fig.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
fig.update_layout(
    font=dict(
        family="Courier New, monospace",
        size=15 # Set the font size here
        
    ))
#-----------------------------------------------------------------------------------------

col1, col2, col3, col4 = st.columns(4)
col1.metric("Income ", str(round(volumen_fil.total_price.sum()/1000000,2)), 'Mill R$')
col2.metric("Products sold", str(round(df.order_id.sum()/1000,2)), "K units")
col3.metric("Customers", 98634/1000)
col4.metric("Sellers", 3095/1000)
st.markdown("""---""")

st.subheader("Products sold by month")
st.plotly_chart(fig, use_container_width=True)
st.markdown("""---""")
st.subheader("Total purchase by month")
st.plotly_chart(figvolumen, use_container_width=True)


def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="salesOlist.csv">Download CSV File</a>'
    return href

st.markdown(filedownload(volumen_fil), unsafe_allow_html=True)



st.markdown("""---""")
st.subheader("Average ticket per month")
st.plotly_chart(figticketprom ,use_container_width=True)
st.write('The average ticket is R$140')
st.write('.')
st.markdown("""---""")
st.subheader("Relation between price and sales")
st.plotly_chart(figbubble ,use_container_width=True)
st.write('The sales volume is concentrated in the average price')

