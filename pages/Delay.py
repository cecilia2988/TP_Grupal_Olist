import streamlit as st
import page_config 
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from automatic_athena_download import traer_df


page_config.run()

st.title(":bar_chart: Analisis Delay en las entregas")
st.markdown("##")
st.markdown("""---""")


orders= traer_df('SELECT * FROM processed_orders')
customers= traer_df('SELECT * FROM processed_customers')
order_items=traer_df('SELECT * FROM processed_order_items')
# parse_dates = ['order_purchase_timestamp','order_approved_at', 'order_delivered_carrier_date', 'order_delivered_customer_date', 'order_estimated_delivery_date']
# orders = pd.read_csv('csv normalizados\csv normalizados\OrdersNor.csv',infer_datetime_format = True, parse_dates = parse_dates)
# customers  = pd.read_csv('csv normalizados\csv normalizados\CustomersNor.csv')
# order_items  = pd.read_csv('csv normalizados\csv normalizados\Order_itemsNor.csv')

orders[['order_purchase_timestamp','order_approved_at','order_delivered_customer_date','order_estimated_delivery_date',]]=orders[['order_purchase_timestamp',
       'order_approved_at','order_delivered_customer_date','order_estimated_delivery_date']].apply(pd.to_datetime)

# orders['order_purchase_timestamp'] = orders['order_purchase_timestamp'].dt.date
# orders['order_approved_at'] = orders['order_approved_at'].dt.date
# orders['order_delivered_carrier_date'] = orders['order_delivered_carrier_date'].dt.date
# orders['order_delivered_customer_date'] = orders['order_delivered_customer_date'].dt.date
# orders['order_estimated_delivery_date'] = orders['order_estimated_delivery_date'].dt.date

# orders['order_purchase_timestamp'] = pd.to_datetime(orders['order_purchase_timestamp'])
# orders['order_approved_at'] = pd.to_datetime(orders['order_approved_at'])
# orders['order_delivered_carrier_date'] = pd.to_datetime(orders['order_delivered_carrier_date'])
# orders['order_delivered_customer_date'] = pd.to_datetime(orders['order_delivered_customer_date'])
# orders['order_estimated_delivery_date'] = pd.to_datetime(orders['order_estimated_delivery_date'])

customers_order = pd.merge(orders,customers, on=["customer_id"])
customers_order['time_delay'] = (customers_order['order_delivered_customer_date'] - customers_order['order_estimated_delivery_date'])
oneday = pd.Timedelta(days=1)

customers_order['time_delay'] = (customers_order['order_delivered_customer_date'] - customers_order['order_estimated_delivery_date']) / oneday
customers_order['est_to_deliver'] = np.where(customers_order['time_delay']<0, 1, 0)
dlv_df=customers_order[['order_id','est_to_deliver']]
dlv=dlv_df.pivot_table(values='order_id',index='est_to_deliver', aggfunc='nunique')
dlv.sort_values(by='order_id', ascending=False, inplace=True)
dlv.reset_index(inplace=True)
dlv['Delay']=["Sin demora", "Con demora"]

figdemora = px.pie(dlv, values='order_id', names='Delay', color_discrete_sequence=px.colors.sequential.RdBu)
figdemora.update_layout(
    autosize=False,
    width=700,
    height=700)


agg_tips = customers_order.groupby(['customer_state', 'est_to_deliver'])['order_id'].count().unstack()
agg_tips.sort_values(1,inplace=True, ascending=False)
fig, ax = plt.subplots(figsize=(12, 10))
ax.bar(agg_tips.index, agg_tips[1], label='Entrega sin demora')
ax.bar(agg_tips.index, agg_tips[0], bottom=agg_tips[1],
       label='Entrega con demora')
ax.legend()


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
custmer_order_items = pd.merge(customers_order,order_items_fil, on =['order_id'])
custmer_order_items['M'] = custmer_order_items['order_purchase_timestamp'].dt.to_period('M')
resize_plot = lambda: plt.gcf().set_size_inches(12, 5)
custmer_order_items['Mes'] = custmer_order_items['order_purchase_timestamp'].dt.to_period('M')
reviews_timeseries = custmer_order_items[custmer_order_items['est_to_deliver'] == 0].groupby('Mes')['time_delay'].agg(['count', 'mean'])




fig2 = px.line(reviews_timeseries, x=reviews_timeseries.index.to_timestamp(), y="count", color_discrete_sequence=["black", "red"])


fig3 = px.line(reviews_timeseries, x=reviews_timeseries.index.to_timestamp(), y="mean", color_discrete_sequence=["black", "red"])



left_column, right_column = st.columns(2)
with left_column:
        st.subheader('Pedidos con demora')
        st.plotly_chart(figdemora,use_container_width=True)
with right_column:
        st.subheader('Tiempo de entrega por estado')
        st.pyplot(fig)

st.subheader("Cantidad de pedidos con demora")
st.plotly_chart(fig2,use_container_width=True)
st.subheader("Cantidad de dias de demora")
st.plotly_chart(fig3,use_container_width=True)