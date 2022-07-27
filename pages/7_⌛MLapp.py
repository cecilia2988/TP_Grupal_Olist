from dis import dis
from multimethod import RETURN
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
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
from sklearn.linear_model import Lasso
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeClassifier

page_config.run()
load_data()



st.title(":bar_chart: Shipping value prediction")
st.markdown("##")
st.markdown("""---""")


#--------------------------------------------------------------------------------------


#Cargamos los   dataset
df_ML=st.session_state['all']

#Creamos la funcion de distancia entre dos puntos



st.sidebar.header('User Input Features')
m =["January","February","March","April","May","June","July","August","September","October","November","December"]
d=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
meses = st.sidebar.selectbox('Month', m)
dias= st.sidebar.selectbox('Day', d)


dist = st.sidebar.slider("Distance KM", 0, 8700)
peso= st.sidebar.slider("Weight g", 0, 40500)
vol= st.sidebar.slider("Volume cm3", 0, 300000)
if meses=="January":
    mes=1
if meses=="February":
    mes=2
if meses=="March":
    mes=3
if meses=="April":
    mes=4
if meses=="May":
    mes=5
if meses=="June":
    mes=6
if meses=="July":
    mes=7
if meses=="August":
    mes=8
if meses=="September":
    mes=9
if meses=="October":
    mes=10
if meses=="November":
    mes=11
if meses=="December":
    mes=12

if dias=='Monday':
    dia=1
if dias=='Tuesday':
    dia=2
if dias=='Wednesday':
    dia=3
if dias=='Thursday':
    dia=4
if dias=='Friday':
    dia=5
if dias=='Saturday':
    dia=6
if dias=='Sunday':
    dia=7



#REALIZAMOS LA PREDICCION DEL PRECIO ESTIMADO DEL ENVIO
#Definimos nuestras features(x) y nuestro target(y)

x = df_ML[['purchase_month','purchase_day_of_week','distance','product_volume_cm3','product_weight_g']]
y = df_ML['freight_value']


#Creamos la funcion para predecir
def prediccion(mes,dia,dist,vol,peso):
    #creo un dataframe para retornar
    df_ML_valor = pd.DataFrame({'purchase_month': [mes],'purchase_day_of_week': [dia],'distance': [dist],'product_volume_cm3':[vol],'product_weight_g': [peso]})
    return df_ML_valor
#Ejemplo de ejecucion de la funcion de prediccion
    '''df= prediccion(7,0,776,15444,1200)
        y_cla_valor = adr2.predict(df)
        print(y_cla_valor)'''

#REALIZAMOS LA PREDICCION SI EL PAQUETE VA A TENER DEMORA O NO VA A TENER DEMORA
#Definimos nuestras features(x_cla) y nuestro target(y_cla)
x_cla = df_ML[['purchase_month', 'purchase_day_of_week']]
y_cla = df_ML['est_to_deliver']


#Creamos la funcion para predecir
def delay(mes,dia):
    #creo un dataframe de prueba
    df_delay = pd.DataFrame({'purchase_month': [mes],'purchase_day_of_week': [dia]})
    return df_delay

#Ejemplo de la funcion de prediccion ( 0= "Va a tener delay" o 1= "No va a tener delay")
    '''df= delay(9,4)
    y_cla_prueba = tree.predict(df)
    print(y_cla_prueba)'''


# Creamos un objeto arbol
tree = DecisionTreeClassifier()
#Instanciamos el modelo
adr2= RandomForestRegressor(n_estimators=200, random_state=0)

banderaprecio=False
def entrenar_precio():
    #definimos los conjuntos de entrenamiento y prueba
    X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state = 14)
    #entrenamos el modelo
    adr2.fit(X_train, y_train)
    banderaprecio=True
    return adr2

def entrenar_delay():
    #definimos los conjuntos de entrenamiento y prueba
    X_train, X_test, y_train, y_test = train_test_split(x_cla, y_cla, test_size=0.30, random_state=42)
    #Entrenamos el modelo
    tree.fit(X_train, y_train)
    return tree

left_column, right_column = st.columns(2)
with left_column:
    st.subheader("Shipping price")
    if st.button('RUN'):
        if banderaprecio==False:
            adr2=entrenar_precio()
            tree=entrenar_delay()
        dfpred_Precio=prediccion(mes,dia,dist,vol,peso)
        st.table(dfpred_Precio)
        y_cla_valor = adr2.predict(dfpred_Precio)
        st.subheader("Estimated shipping price")
        st.success(str(round(y_cla_valor[0],2)) + ' R$')
        df= delay(mes,dia)
        y_cla_prueba = tree.predict(df)
        st.subheader("Order on time?")
        if y_cla_prueba[0]==1:
            st.success('On Time')
        else:
            st.error('With Delay')
    
with right_column:
    st.write('.')
        
        

        


