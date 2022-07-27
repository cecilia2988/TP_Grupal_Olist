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
load_data()


st.title(":bar_chart: Delay analysis in deliveries")
st.markdown("##")
st.markdown("""---""")


# orders= traer_df('SELECT * FROM processed_orders')
# customers= traer_df('SELECT * FROM processed_customers')
# order_items=traer_df('SELECT * FROM processed_order_items')
orders = st.session_state['orders']
customers = st.session_state['customers']
order_items   = st.session_state['order_items']
all= st.session_state['all']

orders[['order_purchase_timestamp','order_approved_at','order_delivered_customer_date','order_estimated_delivery_date',]]=orders[['order_purchase_timestamp',
       'order_approved_at','order_delivered_customer_date','order_estimated_delivery_date']].apply(pd.to_datetime)

orders['order_purchase_timestamp'] = orders['order_purchase_timestamp'].dt.date
orders['order_approved_at'] = orders['order_approved_at'].dt.date
orders['order_delivered_carrier_date'] = orders['order_delivered_carrier_date'].dt.date
orders['order_delivered_customer_date'] = orders['order_delivered_customer_date'].dt.date
orders['order_estimated_delivery_date'] = orders['order_estimated_delivery_date'].dt.date

orders['order_purchase_timestamp'] = pd.to_datetime(orders['order_purchase_timestamp'])
orders['order_approved_at'] = pd.to_datetime(orders['order_approved_at'])
orders['order_delivered_carrier_date'] = pd.to_datetime(orders['order_delivered_carrier_date'])
orders['order_delivered_customer_date'] = pd.to_datetime(orders['order_delivered_customer_date'])
orders['order_estimated_delivery_date'] = pd.to_datetime(orders['order_estimated_delivery_date'])

customers_order = pd.merge(orders,customers, on=["customer_id"])
customers_order['time_delay'] = (customers_order['order_delivered_customer_date'] - customers_order['order_estimated_delivery_date'])
oneday = pd.Timedelta(days=1)

customers_order['time_delay'] = (customers_order['order_delivered_customer_date'] - customers_order['order_estimated_delivery_date']) / oneday
customers_order['est_to_deliver'] = np.where(customers_order['time_delay']<0, 1, 0)
dlv_df=customers_order[['order_id','est_to_deliver']]
dlv=dlv_df.pivot_table(values='order_id',index='est_to_deliver', aggfunc='nunique')
dlv.sort_values(by='order_id', ascending=False, inplace=True)
dlv.reset_index(inplace=True)
dlv['Delay']=["On Time", "With Delay"]

figdemora = px.pie(dlv, values='order_id', names='Delay', color_discrete_sequence=px.colors.qualitative.G10)
figdemora.update_layout(
    autosize=False,
    width=500,
    height=500,
    font=dict(
        family="Courier New, monospace",
        size=20,  # Set the font size here
        color="RebeccaPurple"
    ))



customers_order["estado"]=np.where(customers_order['est_to_deliver']==0, 'with delay', 'on time')
ac= customers_order.groupby(['customer_state','estado'])[['order_id']].count()
ac.sort_values('order_id', ascending=False, inplace=True)
ac.reset_index(inplace=True)
acc=ac.head(15)
fig = px.bar(acc, x="customer_state", y='order_id', color="estado", text_auto='.2s')
fig.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
fig.update_layout(
    autosize=False,
    width=500,
    height=500,
    font=dict(
        family="Courier New, monospace",
        size=20  # Set the font size here
        
    ))


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




fig2 = px.line(reviews_timeseries, x=reviews_timeseries.index.to_timestamp(), y="count", color_discrete_sequence=["cadetblue", "red"],labels=dict(x="Date",count='Number of delayed orders'))
fig2.update_traces(line=dict(width=12))
fig2.add_annotation(x='2018-03', y=1641,
            text="Max amount of delayed orders",
            showarrow=True,
            arrowhead=1,font=dict(
                color="black",
                size=15,
                family="Arial Black"
            ))
fig2.add_annotation(x='2017-03', y=163,
            text="Few delayed orders",
            showarrow=True,
            arrowhead=1,font=dict(
                color="black",
                size=15,
                family="Arial Black"
            ))
fig2.update_layout(
    font=dict(
        family="Courier New, monospace",
        size=15 # Set the font size here
        
    ))


fig3 = px.line(reviews_timeseries, x=reviews_timeseries.index.to_timestamp(), y="mean", color_discrete_sequence=["cadetblue", "red"],labels=dict(x="Date",mean='Days of delay'))
fig3.update_traces(line=dict(width=12))
fig3.add_annotation(x='2017-03', y=20,
            text="Max days of delay",
            showarrow=True,
            arrowhead=1,font=dict(
                color="black",
                size=15,
                family="Arial Black"
            ))
fig3.add_annotation(x='2018-03', y=9,
            text="Few days of delay",
            showarrow=True,
            arrowhead=1,font=dict(
                color="black",
                size=15,
                family="Arial Black"
            ))
fig3.update_layout(
    font=dict(
        family="Courier New, monospace",
        size=15 # Set the font size here
        
    ))


all2=all.groupby(['estimated_delivery_time','customer_state','customer_state_description'])[['distance']].mean()
all2.reset_index(inplace=True)
all2.sort_values('distance',ascending=False,inplace=True)

figbubble = px.scatter(all2.head(30), x='distance', y="estimated_delivery_time",
	         size="estimated_delivery_time",color='customer_state_description',
                  log_x=True, size_max=60, labels=dict(estimated_delivery_time='estimated days',distance="distance KM"))
figbubble.update_layout(
    font=dict(
        family="Courier New, monospace",
        size=15 # Set the font size here
        
    ))


agrup=all[all.time_delay>0].groupby(['customer_state','customer_state_description'])[['time_delay']].mean()
agrup.reset_index(inplace=True)
agrup.sort_values('time_delay', ascending=False,inplace=True)

figdemora2 = px.bar(agrup.head(10), y='time_delay', x='customer_state_description', text_auto='.0s',
            color_discrete_sequence=["cadetblue", "red","green"],labels=dict(time_delay='days of delay',customer_state_description="state"))
figdemora2.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
figdemora2.update_layout(
    font=dict(
        family="Courier New, monospace",
        size=15 # Set the font size here
        
    ))

st.markdown("""---""")
left_column, right_column = st.columns(2)
with left_column:
        st.subheader('Delayed orders')
        st.plotly_chart(figdemora,use_container_width=True)
with right_column:
        st.subheader('Delay by state')
        # st.pyplot(fig)
        st.plotly_chart(fig,use_container_width=True)
st.markdown("""---""")
st.subheader("orders with delays")
st.plotly_chart(fig2,use_container_width=True)
st.subheader("Days of delay")
st.plotly_chart(fig3,use_container_width=True)

def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="delay_olist.csv">Download CSV File</a>'
    return href

st.markdown(filedownload(reviews_timeseries), unsafe_allow_html=True)

st.markdown("""---""")
st.subheader("Relation between shipping time and distance")
st.plotly_chart(figbubble,use_container_width=True)

st.subheader("States with more delay")
st.plotly_chart(figdemora2,use_container_width=True)