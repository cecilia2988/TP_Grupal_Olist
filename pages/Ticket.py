import streamlit as st
import page_config 
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
from automatic_athena_download import traer_df


page_config.run()

st.title(":bar_chart: Ticket promedio y medios de pago")
st.markdown("##")
st.markdown("""---""")

st.sidebar.header('User Input Features')
cuotasfiltro = st.sidebar.slider("cantidad de cuotass Mayor a ", 1, 24)
ticketfiltro= st.sidebar.slider("ticket Mayor a ", 1, 150)

order_items= traer_df('SELECT * FROM processed_order_items')
order_payments= traer_df('SELECT * FROM processed_order_payments')
products= traer_df('SELECT * FROM processed_products')
# order_items=pd.read_csv('csv normalizados\csv normalizados\Order_itemsNor.csv', infer_datetime_format = True)
# order_payments = pd.read_csv('csv normalizados\csv normalizados\Order_paymentsNor.csv')
# products = pd.read_csv('csv normalizados\csv normalizados\ProductsNor.csv')


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
precio_cant_mes=order_items_fil.groupby('month_year').agg({'total_price':'sum', 'order_id':'count'})
precio_cant_mes ['promedio'] = precio_cant_mes['total_price'] / precio_cant_mes['order_id']
precio_cant_mes.reset_index(inplace=True)
figticketprom = px.bar(precio_cant_mes, y='promedio', x='month_year', text_auto='.3s',
            color_discrete_sequence=["black", "red","green"])
figticketprom.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)




order_payments_items = pd.merge(order_payments, order_items_fil, on= 'order_id')
order_payments_items_2 = pd.merge(order_payments_items, products, on = 'product_id')

order_payments_items_2=order_payments_items_2[order_payments_items_2.payment_value >= float(ticketfiltro)]
order_payments_items_2=order_payments_items_2[order_payments_items_2.payment_installments >= (cuotasfiltro)]


tipo_pago_elegido =order_payments_items_2.groupby(['payment_type']).count().sort_values('order_id', ascending=False)
tipo_pago_elegido.reset_index(inplace=True)


cant_cuotas = order_payments_items_2.groupby(['payment_installments']).count().sort_values('order_id', ascending=False)
cant_cuotas.reset_index(inplace=True)

figcuotas = px.bar(cant_cuotas, x='payment_installments', y='order_id', color='payment_installments', hover_name='payment_installments', color_discrete_sequence=["orange", "red", "green", "blue", "purple"])



fig2 = px.pie(tipo_pago_elegido, values='order_id', names='payment_type')
fig2.update_layout(
    autosize=False,
    width=600,
    height=600,)

st.subheader("Ticket promedio mensual")
st.plotly_chart(figticketprom ,use_container_width=True)
st.markdown("""---""")
st.subheader("Medio de pago elegido")
st.plotly_chart(fig2,use_container_width=True)
st.markdown("""---""")
st.subheader("cantidad de cuotas")
st.plotly_chart(figcuotas,use_container_width=True)
