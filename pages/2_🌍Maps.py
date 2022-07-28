import streamlit as st
from streamlit_folium import st_folium
import folium
import pandas as pd
from PIL import Image
from automatic_athena_download import traer_df
import page_config 
from lib import *
import plotly.express as px
import base64

page_config.run()
load_data()


# image = Image.open(".\pages\mapa.png")
image = Image.open("mapa.png")
lNorte =[ 'RO','AM','RN','PA','TO']
lCentro=['MT','DF','GO','MS']
lSur=['PR','SC','RS']
lSudeste=['MG','ES','RJ','SP']
lNordeste=['MA','PI','BA','SE','PE','PB','CE']

st.sidebar.header('User Input Features')
selected_region = st.sidebar.selectbox('Region', ["All","North","Center","South","Southeast","Northeast"])

# clientes= traer_df('SELECT * FROM processed_clientes')
# vendedores=traer_df("SELECT * FROM processed_vendedores")
nuevo=st.session_state['geolocalization']
vendedores=st.session_state['sellers']
clientes=st.session_state['customers']
clientesagrup=st.session_state['clientesagrup']
vendedoresagrup=st.session_state['vendedoresagrup']
juntos=st.session_state['juntos']
order_items=st.session_state['order_items']
all=st.session_state['all']





#Mapa clientes
m = folium.Map(location=[10,0], tiles="OpenStreetMap", zoom_start=2)
from pandas.core.arrays import string_
for i in range(0,len(clientesagrup)):
   folium.Circle(
      location=[clientesagrup.iloc[i]['geolocation_lat'], clientesagrup.iloc[i]['geolocation_lng']],
      popup=folium.Popup(clientesagrup.iloc[i]["state"] + ":" + str(clientesagrup.iloc[i]['cantidad'])),
      radius=float(clientesagrup.iloc[i]['cantidad'])*10,
      color='crimson',
      fill=True,
      fill_color='crimson'
   ).add_to(m)




#Mapa Vendedores
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



clientes_state = clientes.groupby(['customer_state_description','customer_state']).count()
clientes_state['porcentaje']=clientes_state['customer_id']*100/clientes['customer_id'].count()
clientes_state.reset_index(inplace=True)
clientes_state.rename(columns={'customer_state':'state'}, inplace=True)
clientes_state.sort_values('customer_id', ascending=False, inplace=True)

if(selected_region=='All'):
    clientes_state_final=clientes_state
    vendedores_final=vendedores
    juntosfinal=juntos
if(selected_region=='North'):
    clientes_state_final=clientes_state[clientes_state.state.isin(lNorte)]
    vendedores_final=vendedores[vendedores.state.isin(lNorte)]
    juntosfinal=juntos[juntos.state.isin(lNorte)]
if(selected_region=='Center'):
    clientes_state_final=clientes_state[clientes_state.state.isin(lCentro)]
    vendedores_final=vendedores[vendedores.state.isin(lCentro)]
    juntosfinal=juntos[juntos.state.isin(lCentro)]
if(selected_region=='South'):
    clientes_state_final=clientes_state[clientes_state.state.isin(lSur)]
    vendedores_final=vendedores[vendedores.state.isin(lSur)]
    juntosfinal=juntos[juntos.state.isin(lSur)]
if(selected_region=='Southeast'):
    clientes_state_final=clientes_state[clientes_state.state.isin(lSudeste)]
    vendedores_final=vendedores[vendedores.state.isin(lSudeste)]
    vendedores_final=vendedores[vendedores.state.isin(lSudeste)]
    juntosfinal=juntos[juntos.state.isin(lSudeste)]
if(selected_region=='Northeast'):
    clientes_state_final=clientes_state[clientes_state.state.isin(lNordeste)]
    vendedores_final=vendedores[vendedores.state.isin(lNordeste)]
    juntosfinal=juntos[juntos.state.isin(lNordeste)]

figclientes = px.bar(clientes_state_final.head(10), y='porcentaje', x='customer_state_description', text_auto='.4s',
             color_discrete_sequence=["cadetblue", "red","green"],labels=dict(porcentaje="percentage % ",customer_state_description='state'))
figclientes.update_traces(textfont_size=15, textangle=0, textposition="outside", cliponaxis=False)
figclientes.update_layout(
    font=dict(
        family="Courier New, monospace",
        size=15  # Set the font size here
        
    ))

vendedores.rename(columns={'seller_state':'state'}, inplace=True)




seller_state = vendedores_final.groupby(['seller_state_description']).count()
seller_state['porcentaje']=seller_state['seller_id']*100/vendedores['seller_id'].count()
seller_state.reset_index(inplace=True)
seller_state.sort_values('seller_id', ascending=False, inplace=True)




figvendedores = px.bar(seller_state.head(10), y='porcentaje', x='seller_state_description', text_auto='.3s',
             color_discrete_sequence=["cadetblue", "red","green"],labels=dict(porcentaje="percentage % ",seller_state_description='state'))
figvendedores.update_traces(textfont_size=15, textangle=0, textposition="outside", cliponaxis=False)
figvendedores.update_layout(
    font=dict(
        family="Courier New, monospace",
        size=15  # Set the font size here
        
    ))



totalclientes= juntos.clientes.sum()
porcentajevendedores =round(juntosfinal.vendedores.sum() *100 / juntos.vendedores.sum(),2)
porcentajeclientes=round(juntosfinal.clientes.sum()*100 /totalclientes,2)



all2=aplicar_region(all)
all2=all2[all2.region != 'Sin dato']
figcostoenvio = px.box(all2, x="region", y="freight_value", color="region", color_discrete_sequence=['blue','lightblue','red','green','yellow'],points=False)
figcostoenvio.add_annotation(x='South', y=17.67,
            text="Median 17.67",
            showarrow=True,
            arrowhead=1,font=dict(
                color="black",
                size=15,
                family="Arial Black"
            ))
figcostoenvio.add_annotation(x='Southeast', y=15.1,
            text="Median 15.1",
            showarrow=True,
            arrowhead=1,font=dict(
                color="black",
                size=15,
                family="Arial Black"
            ))
figcostoenvio.add_annotation(x='Center', y=18.23,
            text="Median 15.23",
            showarrow=True,
            arrowhead=1,font=dict(
                color="black",
                size=15,
                family="Arial Black"
            ))
figcostoenvio.add_annotation(x='North', y=29.15,
            text="Median 29.15",
            showarrow=True,
            arrowhead=1,font=dict(
                color="black",
                size=15,
                family="Arial Black"
            ))
figcostoenvio.add_annotation(x='Northeast', y=25.38,
            text="Median 25.38",
            showarrow=True,
            arrowhead=1,font=dict(
                color="black",
                size=15,
                family="Arial Black"
            ))

df_regiones= all2.groupby(['region'])[['price']].sum()
df_regiones.reset_index(inplace=True)
figregiovolumen = px.pie(df_regiones, values='price', names='region', color_discrete_sequence=['blue','lightblue','green','red','yellow'])



all2=all2.groupby(['customer_state','region'])[["distance","freight_value"]].mean()
all2.reset_index(inplace=True)
all2.sort_values("freight_value", ascending=False, inplace=True)

figbubble = px.scatter(all2.head(50), x='distance', y="freight_value",
	         size="freight_value",color='region', color_discrete_sequence=['green','yellow','red','blue','lightblue'],
                  log_x=True, size_max=60, labels=dict(order_id="products sold"))
figbubble.update_layout(
    font=dict(
        family="Courier New, monospace",
        size=15 # Set the font size here
        
    ))


st.title("Locating customers and sellers")
st.markdown("##")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Sellers ", str((juntosfinal.vendedores.sum()/1000)))
col2.metric("Perc of total", float(porcentajevendedores), "%")
col3.metric("Customers", str((juntosfinal.clientes.sum()/1000)))
col4.metric("Perc of total", float(porcentajeclientes), "%")
st.markdown("""---""")


left_column, right_column = st.columns(2)
with left_column:
        st.subheader("Map of regions")
        st.write('.')
        st.write('.')
        st.image(image, caption='Regiones Brasil',width=700) 
with right_column:
        st.subheader("Sellers by state")
        st.plotly_chart(figvendedores, use_container_width=True)
        st.subheader("Customers by state")
        st.plotly_chart(figclientes, use_container_width=True)

left_column, right_column = st.columns(2)
with left_column:
        st.subheader("Customers")
        st_data = st_folium(m, width=900)
with right_column:
        st.subheader("Sellers")
        st_data = st_folium(mv, width=900)


st.subheader("Sales volume by region")
st.plotly_chart(figregiovolumen, use_container_width=True)


st.subheader("Shipping Cost")
st.plotly_chart(figcostoenvio, use_container_width=True)
def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="ShippingCost.csv">Download CSV File</a>'
    return href

st.markdown(filedownload(all2), unsafe_allow_html=True)

st.markdown("""---""")

st.subheader("Relation between state distance and shipping cost")
st.plotly_chart(figbubble, use_container_width=True)