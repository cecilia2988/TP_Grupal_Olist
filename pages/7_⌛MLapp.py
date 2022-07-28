from dis import dis
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
import pickle

page_config.run()
load_data()


st.title(":bar_chart: Shipping value prediction")
st.markdown("##")
st.markdown("""---""")

#--------------------------------------------------------------------------------------



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



#Creamos la funcion para predecir
def prediccion(mes,dia,dist,vol,peso):
    #creo un dataframe para retornar
    df_ML_valor = pd.DataFrame({'purchase_month': [mes],'purchase_day_of_week': [dia],'distance': [dist],'product_volume_cm3':[vol],'product_weight_g': [peso]})
    return df_ML_valor


#Creamos la funcion para predecir
def delay(mes,dia):
    #creo un dataframe de prueba
    df_delay = pd.DataFrame({'purchase_month': [mes],'purchase_day_of_week': [dia]})
    return df_delay

#Ejemplo de la funcion de prediccion ( 0= "Va a tener delay" o 1= "No va a tener delay")
    '''df= delay(9,4)
    y_cla_prueba = tree.predict(df)
    print(y_cla_prueba)'''



left_column, right_column = st.columns(2)
with left_column:
    st.subheader("Shipping price")
    if st.button('RUN'):

        infile = open('adr2','rb')
        adr2file = pickle.load(infile)
        infile.close()
        infile2 = open('tree1','rb')
        treefile = pickle.load(infile2)
        infile2.close()
        
        dfpred_Precio=prediccion(mes,dia,dist,vol,peso)
        st.table(dfpred_Precio)
        y_cla_valor = adr2file.predict(dfpred_Precio)
        st.subheader("Estimated shipping price")
        st.success(str(round(y_cla_valor[0],2)) + ' R$')
        df= delay(mes,dia)
        y_cla_prueba = treefile.predict(df)
        st.subheader("Order on time?")
        if y_cla_prueba[0]==1:
            st.success('On Time')
        else:
            st.error('With Delay')
    
with right_column:
    st.write('.')
        
        

        


