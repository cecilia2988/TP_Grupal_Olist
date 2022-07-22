import streamlit as st
import page_config 
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
from automatic_athena_download import traer_df

page_config.run()

st.title(":bar_chart: Productos y valoraciones")
st.markdown("##")
st.markdown("""---""")

order_items= traer_df('SELECT * FROM processed_order_items')
products= traer_df('SELECT * FROM processed_products')
order_reviews= traer_df('SELECT * FROM processed_order_reviews')
# order_items  = pd.read_csv('csv normalizados\csv normalizados\Order_itemsNor.csv')
# products  = pd.read_csv('csv normalizados\csv normalizados\ProductsNor.csv')
# order_reviews  = pd.read_csv('csv normalizados\csv normalizados\Order_reviewsNor.csv')

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
top_10_cat_mostrar=top_10_cat[['product_category_name','order_id']]
top_10_cat_mostrar.rename(columns={'order_id':'cantidad'},inplace=True)




figtopcategoria = px.treemap(top_10_cat, path=['product_category_name'],
                 values='order_id')
figtopcategoria.update_layout(
    autosize=False,
    width=600,
    height=500,)

order_product_valoracion = pd.merge(order_product, order_reviews, on = ['order_id'])
score = order_product_valoracion.groupby(['product_category_name', 'review_score']).count()
score.reset_index(inplace=True)

score_fil_mejores = score.loc[(score['review_score']==int(selected_estrella))]
score_fil_mejores.sort_values('product_id', inplace=True, ascending=False)
score_fil_mejores_mostrar=score_fil_mejores.head(10)
score_fil_mejores_mostrar=score_fil_mejores_mostrar[['product_category_name','order_id','review_score']]

figscore, ax = plt.subplots(figsize=(10, 8))
ax = sns.barplot(x=score_fil_mejores_mostrar.product_category_name, y=score_fil_mejores_mostrar.order_id, palette="Blues")
plt.xticks(fontsize=12,rotation=75)


categoria= products.product_category_name.unique()
ccategoria=categoria.shape[0]

col1, col2, col3 = st.columns(3)
col1.metric("Categorias 🎀", str(ccategoria))
col2.metric("Productos 🎁", str(products.product_id.count()))
col3.metric("Score Promedio ⭐", str(round(score.review_score.mean(),2)))
st.markdown("""---""")



left_column, right_column = st.columns(2)
with left_column:
        st.subheader("Top categorias")
        st.plotly_chart(figtopcategoria ,use_container_width=True)
with right_column:
        st.subheader("Datos")
        st.table(top_10_cat_mostrar)


left_column, right_column = st.columns(2)
with left_column:
        st.subheader("Productos por valoracion")
        st.pyplot(figscore)
with right_column:
        st.subheader("Datos")
        st.table(score_fil_mejores_mostrar)



