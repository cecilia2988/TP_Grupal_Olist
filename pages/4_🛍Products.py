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

st.title(":bar_chart: Products and Reviews")
st.markdown("##")
st.markdown("""---""")

# order_items= traer_df('SELECT * FROM processed_order_items')
# products= traer_df('SELECT * FROM processed_products')
# order_reviews= traer_df('SELECT * FROM processed_order_reviews')
order_items= st.session_state['order_items']
products  = st.session_state['products']
order_reviews  = st.session_state['order_reviews']

st.sidebar.header('User Input Features')
selected_estrella = st.sidebar.selectbox('Score', ["5","4","3","2","1"])

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


order_product = pd.merge(order_items_fil,products, on=["product_id"])
categorias=order_product.groupby('product_category_name').count()
categorias.sort_values('product_id', inplace=True, ascending=False)
top_10_cat = categorias.head(10)
top_10_cat.reset_index(inplace=True)
top_10_cat_mostrar=top_10_cat.head(5)
top_10_cat_mostrar=top_10_cat_mostrar[['product_category_name','order_id']]
top_10_cat_mostrar=top_10_cat_mostrar.append({'product_category_name' : 'Others' , 'order_id' : 23868} , ignore_index=True)




figtopcategoria = go.Figure(data=[go.Pie(labels=top_10_cat_mostrar['product_category_name'], values=top_10_cat_mostrar['order_id'], hole=.3)])
figtopcategoria.update_layout(
    autosize=False,
    width=600,
    height=600,
    font=dict(
        family="Courier New, monospace",
        size=20  # Set the font size here
        
    ))
listacategorias=top_10_cat.head(5)['product_category_name'].unique()

order_product_valoracion = pd.merge(order_product, order_reviews, on = ['order_id'])
score = order_product_valoracion.groupby(['product_category_name', 'review_score']).count()
score.reset_index(inplace=True)

Subjects = {1 : "S 1",
            2 : "S 2",
            3 : "S 3",
            4 : "S 4",
            5 : "S 5"}
score["scores"] = score["review_score"].map(Subjects)
score2=score[score.product_category_name.isin(listacategorias)]
figscore = px.bar(score2, x="product_category_name", y='order_id', color="scores", text_auto='.2s')
figscore.update_traces(textfont_size=15, textangle=0, textposition="outside", cliponaxis=False)
figscore.update_layout(
    autosize=False,
    width=600,
    height=600,
    font=dict(
        family="Courier New, monospace",
        size=20  # Set the font size here
        
    ))


vendedoresproductos = order_product_valoracion.groupby('product_category_name').agg({
                                   "seller_id": pd.Series.nunique})
vendedoresproductos.reset_index(inplace=True)
vendedoresproductos.sort_values('seller_id',inplace=True, ascending=False)
figvendedoresproductos = px.bar(vendedoresproductos.head(10), y='seller_id', x='product_category_name', text_auto='.3s',
            color_discrete_sequence=["cadetblue", "red","green"],labels=dict( seller_id="sellers"))
figvendedoresproductos.update_layout(width=600,
        height=600,
    font=dict(
        family="Courier New, monospace",
        size=15 # Set the font size here

        
    ))
figvendedoresproductos.update_xaxes(
        tickangle = 45,
        title_font = {"size": 15})


categoria= products.product_category_name.unique()
ccategoria=categoria.shape[0]

col1, col2, col3 = st.columns(3)
col1.metric("Categories ", str(ccategoria))
col2.metric("Products ", str(products.product_id.count()/1000))
col3.metric("Score average ", str(round(score.review_score.mean(),2)))
st.markdown("""---""")



st.subheader("Top products categories")
st.plotly_chart(figtopcategoria ,use_container_width=True)

st.markdown("""---""")
st.subheader("Products by reviews")
st.plotly_chart(figscore ,use_container_width=True)

def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="ScoreOlist.csv">Download CSV File</a>'
    return href

st.markdown(filedownload(score), unsafe_allow_html=True)
st.markdown("""---""")
st.subheader("Top products with more sellers")
st.plotly_chart(figvendedoresproductos ,use_container_width=True)


