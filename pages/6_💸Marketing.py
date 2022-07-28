import streamlit as st
import page_config 
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
from automatic_athena_download import traer_df
from lib import *
import base64

page_config.run()
load_data()

st.title(":bar_chart: Marketing Recommendations")
st.markdown("##")
st.markdown("""---""")

# order_items= traer_df('SELECT * FROM processed_order_items')
# sellers= traer_df('SELECT * FROM processed_sellers')
# marketing_q= traer_df('SELECT * FROM processed_marketing')
# closed_deals= traer_df('SELECT * FROM processed_closed_deals')
order_items=st.session_state['order_items']
sellers=st.session_state['sellers']
marketing_q=st.session_state['marketing_q']
closed_deals=st.session_state['closed_deals']
orders2= st.session_state['orders2']


st.sidebar.header('User Input Features')
a =["All","Mon","Tues","Wed", 'Thu', 'Fri',"Sat","Sun"]
selected_day = st.sidebar.selectbox('Day', a)

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
sellers_order = pd.merge(order_items_fil,sellers, on=["seller_id"])
seller_ventas = sellers_order.groupby(['seller_id']).count()
seller_ventas.sort_values('order_id', ascending=False, inplace =True)
seller_ventas.reset_index(inplace=True)
marketing_sellers = pd.merge(closed_deals,marketing_q, on=["mql_id"])
seller_origin = pd.merge(marketing_sellers, seller_ventas, on = ['seller_id'])
seller_origin.drop(columns= ['mql_id', 'sdr_id', 'sr_id', 'declared_monthly_revenue', 'freight_value', 'month','Year',	'month_year', 'month_y', 'total_price','order_item_id', 'shipping_limit_date'], inplace =True)
seller_origin.sort_values('order_id', ascending=False, inplace =True)
seller_origin_agrupado = seller_origin.groupby(['origin']).count().sort_values('seller_id', ascending=False)
seller_origin_agrupado.reset_index(inplace = True)


dias=orders2.groupby(['order_purchase_dayofweek_name','order_purchase_dayofweek'])[['order_id']].count()
dias['porcentaje']=dias['order_id']*100 /orders2['order_id'].count()
dias.sort_values('order_purchase_dayofweek', inplace=True)
dias.reset_index(inplace=True)

figdias=px.bar(dias,x='order_purchase_dayofweek_name', y='porcentaje',height=600, text_auto='.2s', color_discrete_sequence=["cadetblue", "red","green"],labels=dict(oorder_purchase_dayofweek_name="day of week", porcentaje="percentage %"))
figdias.update_layout(
    font=dict(
        family="Courier New, monospace",
        size=18,  # Set the font size here
        color="black"
    ))



@st.cache
def filterorderbydate(selectd,orders2):
    if(selectd=='All'):
        order3=orders2
    else:
        order3=orders2[orders2.order_purchase_dayofweek_name==selectd]
    return order3

order3=filterorderbydate(selected_day,orders2)


horario=order3.groupby(['order_purchase_time_day'])[['order_id']].count()
horario['porcentaje']=horario['order_id']*100 /order3['order_id'].count()
horario.reset_index(inplace=True)
fighorarios = px.bar(horario, x='order_purchase_time_day',y='porcentaje', height=600, width=500, text_auto='.2s', color_discrete_sequence=["cadetblue", "red","green"],labels=dict(order_purchase_time_day="time_day", porcentaje="percentage %"))
fighorarios.update_layout(
    font=dict(
        family="Courier New, monospace",
        size=18,  # Set the font size here
        color="black"
    ))




fig = px.pie(seller_origin_agrupado.head(5), values='seller_id', names='origin')
fig.update_layout(
    autosize=False,
    width=500,
    height=500,
    font=dict(
        family="Courier New, monospace",
        size=20,  # Set the font size here
        color="RebeccaPurple"
    ))

st.subheader("Seller contact method")
st.plotly_chart(fig,use_container_width=True)


left_column, right_column = st.columns(2)
with left_column:
        st.subheader("Sales by days of the week")
        st.plotly_chart(figdias,use_container_width=True)
with right_column:
        st.subheader("Sales by hours")
        st.plotly_chart(fighorarios,use_container_width=True)


def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="DayandHours.csv">Download CSV File</a>'
    return href

st.markdown(filedownload(orders2), unsafe_allow_html=True)

# st.pyplot(figjuntos)