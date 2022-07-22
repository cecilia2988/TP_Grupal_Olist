import streamlit as st
import page_config 
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
from automatic_athena_download import traer_df


page_config.run()

st.title(":bar_chart: Analisis por Estado")
st.markdown("##")
st.markdown("""---""")


lNorte =[ 'RO','AM','RN','PA','TO']
lCentro=['MT','DF','GO','MS']
lSur=['PR','SC','RS']
lSudeste=['MG','ES','RJ','SP']
lNordeste=['MA','PI','BA','SE','PE','PB','CE']

st.sidebar.header('User Input Features')
selected_region = st.sidebar.selectbox('Region', ["All","Norte","Centro","Sur","Sudeste","Nordeste"])


customers= traer_df('SELECT * FROM processed_customers')
sellers= traer_df('SELECT * FROM processed_sellers')
order_items= traer_df('SELECT * FROM processed_order_items')
# customers  = pd.read_csv('csv normalizados\csv normalizados\CustomersNor.csv')
# sellers  = pd.read_csv('csv normalizados\csv normalizados\SellersNor.csv')
# order_items  = pd.read_csv('csv normalizados\csv normalizados\Order_itemsNor.csv')


customers_state = customers.groupby(['customer_state']).count()
customers_state.reset_index(inplace=True)
customers_state.rename(columns={'customer_state':'state'}, inplace=True)
customers_state.sort_values('customer_id', ascending=False, inplace=True)

if(selected_region=='All'):
    customers_state_final=customers_state
if(selected_region=='Norte'):
    customers_state_final=customers_state[customers_state.state.isin(lNorte)]
if(selected_region=='Centro'):
    customers_state_final=customers_state[customers_state.state.isin(lCentro)]
if(selected_region=='Sur'):
    customers_state_final=customers_state[customers_state.state.isin(lSur)]
if(selected_region=='Sudeste'):
    customers_state_final=customers_state[customers_state.state.isin(lSudeste)]
if(selected_region=='Nordeste'):
    customers_state_final=customers_state[customers_state.state.isin(lNordeste)]


figclientes = px.bar(customers_state_final, y='customer_id', x='state', text_auto='.2s',
             color_discrete_sequence=["black", "red","green"])
figclientes.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)

sellers.rename(columns={'seller_state':'state'}, inplace=True)

if(selected_region=='All'):
    sellers_final=sellers
if(selected_region=='Norte'):
    sellers_final=sellers[sellers.state.isin(lNorte)]
if(selected_region=='Centro'):
    sellers_final=sellers[sellers.state.isin(lCentro)]
if(selected_region=='Sur'):
    sellers_final=sellers[sellers.state.isin(lSur)]
if(selected_region=='Sudeste'):
    sellers_final=sellers[sellers.state.isin(lSudeste)]
if(selected_region=='Nordeste'):
    sellers_final=sellers[sellers.isin(lNordeste)]


seller_state = sellers_final.groupby(['state']).count()
seller_state.reset_index(inplace=True)
seller_state.sort_values('seller_id', ascending=False, inplace=True)



figvendedores = px.bar(seller_state, y='seller_id', x='state', text_auto='.2s',
             color_discrete_sequence=["black", "red","green"])
figvendedores.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)



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
sellers_order = pd.merge(order_items_fil,sellers_final, on=["seller_id"])
costo_promedio = sellers_order.groupby(['state']).agg({'freight_value':'mean'})
costo_promedio.reset_index(inplace=True)
costo_promedio.sort_values('freight_value',inplace=True)


figcostoenvio = px.bar(costo_promedio, y='state', x='freight_value', text_auto='.2s',
              color_discrete_sequence=["black","yellow"])
figcostoenvio.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
figcostoenvio.update_layout(
    autosize=False,
    width=500,
    height=800,)



left_column, right_column = st.columns(2)
with left_column:
        st.subheader("Clientes por estado")
        st.plotly_chart(figclientes, use_container_width=True)
with right_column:
        st.subheader("Vendedores por estado")
        st.plotly_chart(figvendedores, use_container_width=True)

st.subheader("costo de envio por estado")
st.plotly_chart(figcostoenvio, use_container_width=True)


