import streamlit as st
from streamlit_folium import st_folium
import folium
import pandas as pd
from PIL import Image
from automatic_athena_download import traer_df
import page_config 


page_config.run()


# image = Image.open(".\pages\mapa.png")
image = Image.open("mapa.png")
lNorte =[ 'RO','AM','RN','PA','TO']
lCentro=['MT','DF','GO','MS']
lSur=['PR','SC','RS']
lSudeste=['MG','ES','RJ','SP']
lNordeste=['MA','PI','BA','SE','PE','PB','CE']

st.sidebar.header('User Input Features')
selected_region = st.sidebar.selectbox('Region', ["Todas","Norte","Centro","Sur","Sudeste","Nordeste"])

clientes= traer_df('SELECT * FROM processed_customers')
geolocalizacion= traer_df('SELECT * FROM processed_geolocation')
vendedores=traer_df("SELECT * FROM processed_sellers")
# clientes = pd.read_csv(".\csv normalizados\csv normalizados\CustomersNor.csv",delimiter = ',',encoding = "utf-8")
# geolocalizacion =pd.read_csv(".\csv normalizados\csv normalizados\GeolocationNor.csv",delimiter = ',',encoding = "utf-8")
# vendedores = pd.read_csv(".\csv normalizados\csv normalizados\SellersNor.csv",delimiter = ',',encoding = "utf-8")


geolocalizacion.rename(columns={'geolocation_state':'customer_state'}, inplace=True)
nuevo= geolocalizacion.groupby('customer_state').agg({'geolocation_lat':'mean','geolocation_lng':'mean'})
clientes=pd.merge(clientes, nuevo, on='customer_state' , how='left')
clientesagrup = clientes.groupby('customer_state').agg({'geolocation_lat':'mean','geolocation_lng':'mean','customer_state':'count'})
clientesagrup.rename(columns={'customer_state':'cantidad'}, inplace=True)
clientesagrup.reset_index(inplace=True)
m = folium.Map(location=[10,0], tiles="OpenStreetMap", zoom_start=2)
from pandas.core.arrays import string_
for i in range(0,len(clientesagrup)):
   folium.Circle(
      location=[clientesagrup.iloc[i]['geolocation_lat'], clientesagrup.iloc[i]['geolocation_lng']],
      popup=folium.Popup(clientesagrup.iloc[i]["customer_state"] + ":" + str(clientesagrup.iloc[i]['cantidad'])),
      radius=float(clientesagrup.iloc[i]['cantidad'])*10,
      color='crimson',
      fill=True,
      fill_color='crimson'
   ).add_to(m)




vendedores.rename(columns={'seller_state':'state'}, inplace=True)
nuevo.reset_index(inplace=True)
nuevo.rename(columns={'customer_state':'state'}, inplace=True)
vendedores=pd.merge(vendedores, nuevo, on='state' , how='left')
vendedoresagrup = vendedores.groupby('state').agg({'geolocation_lat':'mean','geolocation_lng':'mean','state':'count'})
vendedoresagrup.rename(columns={'state':'cantidad'}, inplace=True)
vendedoresagrup.reset_index(inplace=True)
mv = folium.Map(location=[10,0], tiles="OpenStreetMap", zoom_start=2)
from pandas.core.arrays import string_
for i in range(0,len(vendedoresagrup)):
   folium.Circle(
      location=[vendedoresagrup.iloc[i]['geolocation_lat'], vendedoresagrup.iloc[i]['geolocation_lng']],
      popup=folium.Popup(vendedoresagrup.iloc[i]["state"] + ":" + str(vendedoresagrup.iloc[i]['cantidad'])),
      radius=float(vendedoresagrup.iloc[i]['cantidad'])*100,
      color='blue',
      fill=True,
      fill_color='blue'
   ).add_to(mv)




clientesagrup.rename(columns={'customer_state':'state'}, inplace=True)
juntos=pd.merge(clientesagrup, vendedoresagrup, on='state' , how='inner')
juntos.rename(columns={'cantidad_x':'clientes', 'cantidad_y':'vendedores'}, inplace=True)
juntos.drop(columns=['geolocation_lat_x','geolocation_lng_x','geolocation_lat_y','geolocation_lng_y'],inplace=True)
juntos.sort_values("clientes", inplace=True, ascending=False)

if selected_region=="Todas":
   juntosfinal=juntos
if selected_region=='Norte':
   juntosfinal=juntos[juntos.state.isin(lNorte)]
if selected_region=='Centro':
   juntosfinal=juntos[juntos.state.isin(lCentro)]
if selected_region=='Sur':
   juntosfinal=juntos[juntos.state.isin(lSur)]
if selected_region=='Sudeste':
   juntosfinal=juntos[juntos.state.isin(lSudeste)]
if selected_region=='Nordeste':
   juntosfinal=juntos[juntos.state.isin(lNordeste)]

totalclientes= juntos.clientes.sum()
porcentajevendedores =round(juntosfinal.vendedores.sum() *100 / juntos.vendedores.sum(),2)
porcentajeclientes=round(juntosfinal.clientes.sum()*100 /totalclientes,2)

st.title("Localizacion clientes y vendedores")
st.markdown("##")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Vendedores ", str(round(juntosfinal.vendedores.sum(),0)))
col2.metric("Porc del total", float(porcentajevendedores), "%")
col3.metric("Clientes", str(round(juntosfinal.clientes.sum(),0)))
col4.metric("Porc del total", float(porcentajeclientes), "%")
st.markdown("""---""")

left_column, right_column = st.columns(2)
with left_column:
        st.subheader("Mapa Regiones")
        st.image(image, caption='Regiones Brasil',width=500)
with right_column:
        st.table(juntosfinal)

left_column, right_column = st.columns(2)
with left_column:
        st.subheader("Compradores")
        st_data = st_folium(m, width=900)
with right_column:
        st.subheader("Vendedores")
        st_data = st_folium(mv, width=900)