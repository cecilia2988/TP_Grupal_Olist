import streamlit as st
import page_config 
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
from automatic_athena_download import traer_df


page_config.run()

st.title(":bar_chart: Estrategias de Marketing")
st.markdown("##")
st.markdown("""---""")

order_items= traer_df('SELECT * FROM processed_order_items')
sellers= traer_df('SELECT * FROM processed_sellers')
marketing_q= traer_df('SELECT * FROM processed_marketing')
closed_deals= traer_df('SELECT * FROM processed_closed_deals')
# order_items=pd.read_csv('csv normalizados\csv normalizados\Order_itemsNor.csv', infer_datetime_format = True)
# sellers=pd.read_csv('csv normalizados\csv normalizados\SellersNor.csv', infer_datetime_format = True)
# marketing_q=pd.read_csv('csv normalizados\csv normalizados\MarketingNor.csv', infer_datetime_format = True)
# closed_deals=pd.read_csv('csv normalizados\csv normalizados\Closed_dealsNor.csv', infer_datetime_format = True)
orders2= pd.read_csv('olist_orders_dataset.csv')


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



orders2[['order_purchase_timestamp','order_approved_at','order_delivered_customer_date','order_estimated_delivery_date',]]=orders2[['order_purchase_timestamp',
       'order_approved_at','order_delivered_customer_date','order_estimated_delivery_date']].apply(pd.to_datetime)
orders2['order_purchase_year'] = orders2['order_purchase_timestamp'].apply(lambda x: x.year) #gives year Example :2016-10-04 09:43:32 ---->2016
orders2['order_purchase_month'] = orders2['order_purchase_timestamp'].apply(lambda x: x.month) #gives month Example :2016-10-04 09:43:32 ---->10
orders2['order_purchase_month_name'] = orders2['order_purchase_timestamp'].apply(lambda x: x.strftime('%b'))#gives month in short form Example :2016-10-04 09:43:32 ---->10--> Oct
orders2['order_purchase_year_month'] = orders2['order_purchase_timestamp'].apply(lambda x: x.strftime('%Y%m'))#gives month&year Example :2016-10-04 09:43:32 ---->201610
orders2['order_purchase_date'] = orders2['order_purchase_timestamp'].apply(lambda x: x.strftime('%Y%m%d'))#gives month,yr and date  Example :2016-10-04 09:43:32 ---->20161004
orders2['order_purchase_month_yr'] = orders2['order_purchase_timestamp'].apply(lambda x: x.strftime("%b-%y"))

# Extracting attributes for purchase date - Day and Day of Week
orders2['order_purchase_day'] = orders2['order_purchase_timestamp'].apply(lambda x: x.day)
orders2['order_purchase_dayofweek'] = orders2['order_purchase_timestamp'].apply(lambda x: x.dayofweek)
orders2['order_purchase_dayofweek_name'] = orders2['order_purchase_timestamp'].apply(lambda x: x.strftime('%a'))

# Extracting attributes for purchase date - Hour and Time of the Day
orders2['order_purchase_hour'] = orders2['order_purchase_timestamp'].apply(lambda x: x.hour)
hours_bins = [-0.1, 6, 12, 18, 23]
hours_labels = ['Dawn', 'Morning', 'Afternoon', 'Night']
orders2['order_purchase_time_day'] = pd.cut(orders2['order_purchase_hour'], hours_bins, labels=hours_labels)


figdias, ax = plt.subplots(figsize=(3, 3))
ax = sns.countplot(x ='order_purchase_dayofweek_name', data = orders2, palette="mako")
plt.xticks(fontsize=7,rotation=75)
plt.xlabel('Dias de la Semana', size=7, family='monospace', weight=900)
plt.ylabel('Cantidad de ventas', size=7, family='monospace')


if(selected_day=='All'):
    order3=orders2
else:
    order3=orders2[orders2.order_purchase_dayofweek_name==selected_day]

fighorarios, ax = plt.subplots(figsize=(3,3))
ax= sns.countplot(x ='order_purchase_time_day', data = order3, palette="mako")
plt.xticks(fontsize=7,rotation=75)
plt.xlabel('Horario', size=7, family='monospace', weight=900)
plt.ylabel('Cantidad de ventas', size=7, family='monospace')

# figjuntos, ax = plt.subplots(figsize=(2, 2))
# ax= sns.countplot(x ='order_purchase_dayofweek_name', data = orders2, hue='order_purchase_time_day', palette="mako")
# plt.xticks(fontsize=6,rotation=75)
# plt.yticks(fontsize=6,rotation=0)
# plt.legend(bbox_to_anchor=(1.05,1), loc=2, borderaxespad=0., fontsize='7')
# plt.xlabel('Dias de la Semana', size=7, family='monospace', weight=900)
# plt.ylabel('Cantidad de ventas', size=7, family='monospace')

fig = px.funnel(seller_origin_agrupado, x='seller_id', y='origin', color_discrete_sequence=["black", "red","green"])
fig.update_traces(textfont_size=14, textangle=0, cliponaxis=False)
fig.update_layout(
    autosize=False,
    width=600,
    height=800,)

st.subheader("Medio de contacto con los vendedores")
st.plotly_chart(fig,use_container_width=True)


left_column, right_column = st.columns(2)
with left_column:
        st.subheader("Ventas por Dias de la semana")
        st.pyplot(figdias)
with right_column:
        st.subheader("Ventas por franja horaria")
        st.pyplot(fighorarios)


# st.pyplot(figjuntos)