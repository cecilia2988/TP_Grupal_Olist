import streamlit as st
import page_config 
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
from automatic_athena_download import traer_df
from lib import *
import plotly.graph_objects as go
import base64

page_config.run()
load_data()

st.title(":bar_chart: Payment methods")
st.markdown("##")
st.markdown("""---""")

st.sidebar.header('User Input Features')
cuotasfiltro = st.sidebar.slider("Number of installments greater than ", 1, 24)
ticketfiltro= st.sidebar.slider("Ticket greater than", 1, 150)



order_items= st.session_state['order_items']
order_payments = st.session_state['order_payments']
products = st.session_state['products']
orders=st.session_state['orders']
customers=st.session_state['customers']


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



order_payments_items = pd.merge(order_payments, order_items_fil, on= 'order_id')
order_payments_items_2 = pd.merge(order_payments_items, products, on = 'product_id')

order_payments_items_2=order_payments_items_2[order_payments_items_2.payment_value >= float(ticketfiltro)]
order_payments_items_2=order_payments_items_2[order_payments_items_2.payment_installments >= (cuotasfiltro)]


Subjects = {"credit_card" : "Credit card",
                     "boleto" : "cash payment",
                     "debit_card" : "debit card",
                     "voucher" : "voucher"}


order_payments_items_2["Tipo_de_Pago"] = order_payments_items_2["payment_type"].map(Subjects)


tipo_pago_elegido =order_payments_items_2.groupby(['payment_type','Tipo_de_Pago']).count().sort_values('order_id', ascending=False)
tipo_pago_elegido.reset_index(inplace=True)



cant_cuotas = order_payments_items_2.groupby(['payment_installments']).count().sort_values('order_id', ascending=False)
cant_cuotas.reset_index(inplace=True)
cant_cuotas['average']=cant_cuotas['order_id']*100/order_payments_items_2['order_id'].count()
cant_cuotas=cant_cuotas[cant_cuotas['payment_installments']<11]




figcuotas = px.bar(cant_cuotas, x='payment_installments', y='average', hover_name='payment_installments',text_auto='.3s',labels=dict(average="percentage % "), color_discrete_sequence=["cadetblue", "red","green"])
figcuotas.update_layout(
    font=dict(
        family="Courier New, monospace",
        size=15 # Set the font size here
        
    ))


fig2 = px.pie(tipo_pago_elegido, values='order_id', names='Tipo_de_Pago')
fig2.update_layout(
    autosize=False,
    width=600,
    height=600,)
fig2.update_layout(
    font=dict(
        family="Courier New, monospace",
        size=18 # Set the font size here
        
    ))

figrelacion = px.scatter(order_payments_items_2, x='payment_installments', y="price",
	         size="price", color="product_category_name",
                  log_x=True, size_max=60)



st.subheader("Payment methods")
st.plotly_chart(fig2,use_container_width=True)
st.markdown("""---""")
st.subheader("Instalments")
st.plotly_chart(figcuotas,use_container_width=True)
lista=order_payments_items_2['product_category_name'].unique()

st.subheader("Instalments by product category")
categoriaelegida=st.selectbox("Category",lista)

cuotasproducto=order_payments_items_2.groupby(['payment_installments','product_category_name']).count().sort_values('order_id', ascending=False)
cuotasproducto.reset_index(inplace=True)
cuotasproducto=cuotasproducto[cuotasproducto['product_category_name'] == categoriaelegida] 
cuotasproducto.sort_values('order_id',ascending=False, inplace=True)
cuotasproducto2=cuotasproducto.head(5)
figcuotascat = go.Figure(data=[go.Pie(labels=cuotasproducto2['payment_installments'], values=cuotasproducto2['order_id'], hole=.3)])
figcuotascat.update_layout(
    autosize=False,
    width=600,
    height=600,
    font=dict(
        family="Courier New, monospace",
        size=20  
        
    ))

st.plotly_chart(figcuotascat,use_container_width=True)

st.markdown("""---""")
st.subheader("Relation between Price and Instalments")
st.plotly_chart(figrelacion,use_container_width=True)


def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="payments.csv">Download CSV File</a>'
    return href

st.markdown(filedownload(order_payments_items_2), unsafe_allow_html=True)

st.markdown("""---""")

customers_order = pd.merge(orders,customers, on=["customer_id"])
order_state=pd.merge(order_payments_items_2,customers_order, on=["order_id"])
lNorte =[ 'RO','AM','RN','PA','TO']
lCentro=['MT','DF','GO','MS']
lSur=['PR','SC','RS']
lSudeste=['MG','ES','RJ','SP']
lNordeste=['MA','PI','BA','SE','PE','PB','CE']
st.subheader("Payment method by region")
selected_region = st.selectbox('Region', ["North","Center","South","Southeast","Northeast"])


order_state=aplicar_region(order_state)


if selected_region=='North':
   order_state2=order_state[order_state.customer_state.isin(lNorte)]
if selected_region=='Center':
   order_state2=order_state[order_state.customer_state.isin(lCentro)]
if selected_region=='South':
   order_state2=order_state[order_state.customer_state.isin(lSur)]
if selected_region=='Southeast':
   order_state2=order_state[order_state.customer_state.isin(lSudeste)]
if selected_region=='Northeast':
   order_state2=order_state[order_state.customer_state.isin(lNordeste)]


order_state2=order_state2.groupby(['payment_type','Tipo_de_Pago'])[['order_id']].count()
order_state2.reset_index(inplace=True)
figestadopagos = go.Figure(data=[go.Pie(labels=order_state2['Tipo_de_Pago'], values=order_state2['order_id'], hole=.3)])
figestadopagos.update_layout(
    autosize=False,
    width=600,
    height=600,
    font=dict(
        family="Courier New, monospace",
        size=20  # Set the font size here
        
    ))

st.plotly_chart(figestadopagos,use_container_width=True)
