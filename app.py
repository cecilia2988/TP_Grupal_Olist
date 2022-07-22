import streamlit as st
import page_config 
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from automatic_athena_download import traer_df

page_config.run()


clientes= traer_df('SELECT * FROM processed_customers')
order_items= traer_df('SELECT * FROM processed_order_items')
products= traer_df('SELECT * FROM processed_products')
vendedores= traer_df('SELECT * FROM processed_sellers')
# order_items=pd.read_csv('csv normalizados\csv normalizados\Order_itemsNor.csv', infer_datetime_format = True)
# products  = pd.read_csv('csv normalizados\csv normalizados\ProductsNor.csv')
# vendedores = pd.read_csv(".\csv normalizados\csv normalizados\SellersNor.csv",delimiter = ',',encoding = "utf-8")
# clientes = pd.read_csv(".\csv normalizados\csv normalizados\CustomersNor.csv",delimiter = ',',encoding = "utf-8")


st.title(":bar_chart: Olist Dashboard")
st.markdown("##")
st.markdown("""---""")

st.sidebar.header('User Input Features')
a =["All","2016","2017","2018"]
selected_year = st.sidebar.selectbox('Year', a)


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





if selected_year=='All':
    df=product_vendidos
if selected_year=='2016':
    df=product_vendidos[product_vendidos.Year == 2016]
if selected_year=='2017':
    df=product_vendidos[product_vendidos.Year == 2017]
if selected_year=='2018':
    df=product_vendidos[product_vendidos.Year == 2018]        
 






fig = px.bar(df, y='order_id', x='month_year', text_auto='.3s',
            title="Cantidad de productos vendidos por mes" ,color_discrete_sequence=["black", "red","green"])
fig.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
#fig.update_xaxes(tickangle=45, tickfont=dict(family='Rockwell', color='crimson', size=14))



order_product = pd.merge(order_items_fil,products, on=["product_id"])
def format_chart(ax):
    ax.title.set_size(14)
    ax.xaxis.label.set_size(13)
    ax.yaxis.label.set_size(13)
    ax.tick_params(labelsize=11)

maximo = st.sidebar.slider("cantidad de ventas Mayor a ", 10, 8000)
precio= st.sidebar.slider("Precio Mayor a ", 1, 500)

prod_cat=order_product.pivot_table(values=['price', 'order_id'], index=['product_category_name']
                          , aggfunc={'price': 'sum', 'order_id': 'nunique'})
prod_cat["ord_size($R)"]=prod_cat["price"]/prod_cat["order_id"]
prod_cat["price"]=prod_cat["price"]/1000
prod_cat.sort_values(by='price', ascending = False, inplace = True)
prod_cat=prod_cat[prod_cat.order_id>int(maximo)]
prod_cat=prod_cat[prod_cat.price>float(precio)]
prod_cat_top=prod_cat.rename(columns={'order_id':'no_of_order','price':"revenue($R1000)"}).head(30)

#present data to bar plots:
figa, ax = plt.subplots(nrows=1, ncols=3, figsize=(14, 8), sharey=True)
figa.suptitle('Analisis de ganancia por categoria de productos', fontsize=15)

sns.barplot(ax=ax[0], x='revenue($R1000)', y= prod_cat_top.index, data = prod_cat_top)
ax[0].set_title('Ingreso por categoria')
ax[0].set_ylabel('product category')

sns.barplot(ax=ax[1], x='no_of_order', y = prod_cat_top.index, data = prod_cat_top)
ax[1].set_title('Cantidad de venta')

sns.barplot(ax=ax[2], x='ord_size($R)', y = prod_cat_top.index, data = prod_cat_top)
ax[2].set_title('Precio medio')

for i in range(0,3):
    ax[i].set(xlabel=None)

for i in range(1,3):
    ax[i].set(ylabel=None)

#call defined function "format_chart_small" to format charts:
format_chart(ax[0])
format_chart(ax[1])
format_chart(ax[2])

#------------------------------------#


volumen=order_items_fil.groupby(['month_year','Year']).agg({'total_price':'sum', 'order_id':'count'})
volumen.reset_index(inplace=True)
if(selected_year=='All'):
    volumen_fil=volumen
else:
    volumen_fil=volumen[volumen.Year==int(selected_year)]

figvolumen = px.bar(volumen_fil, y='total_price', x='month_year', text_auto='.3s',
            title="Cantidad de productos vendidos por mes", color_discrete_sequence=["black", "red","green"])
figvolumen.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)


#------------------------------------#



col1, col2, col3, col4 = st.columns(4)
col1.metric("Ingresos ", str(round(volumen_fil.total_price.sum(),0)), 'R$')
col2.metric("Productos vendidos", str(round(df.order_id.sum(),0)), "unidades")
col3.metric("Clientes", '98634')
col4.metric("Vendedores", '3095')
st.markdown("""---""")

st.plotly_chart(fig, use_container_width=True)
st.plotly_chart(figvolumen, use_container_width=True)
st.pyplot(figa)

