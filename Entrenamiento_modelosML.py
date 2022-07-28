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


df_ML=st.session_state['all']
#REALIZAMOS LA PREDICCION DEL PRECIO ESTIMADO DEL ENVIO
#Definimos nuestras features(x) y nuestro target(y)

x = df_ML[['purchase_month','purchase_day_of_week','distance','product_volume_cm3','product_weight_g']]
y = df_ML['freight_value']



#Ejemplo de ejecucion de la funcion de prediccion
    # '''df= prediccion(7,0,776,15444,1200)
    #     y_cla_valor = adr2.predict(df)
    #     print(y_cla_valor)'''

#REALIZAMOS LA PREDICCION SI EL PAQUETE VA A TENER DEMORA O NO VA A TENER DEMORA
#Definimos nuestras features(x_cla) y nuestro target(y_cla)
x_cla = df_ML[['purchase_month', 'purchase_day_of_week']]
y_cla = df_ML['est_to_deliver']



#Ejemplo de la funcion de prediccion ( 0= "Va a tener delay" o 1= "No va a tener delay")
    # '''df= delay(9,4)
    # y_cla_prueba = tree.predict(df)
    # print(y_cla_prueba)'''


# Creamos un objeto arbol
tree1 = DecisionTreeClassifier()
#Instanciamos el modelo
adr2= RandomForestRegressor(n_estimators=200, random_state=0)


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
    tree1.fit(X_train, y_train)
    return tree1



adr2=entrenar_precio()
tree1=entrenar_delay()
filenameAdr = 'adr2'
outfileAdr = open(filenameAdr,'wb')
filenameTree = 'tree1'
outfileTree = open(filenameTree,'wb')
pickle.dump(adr2, outfileAdr)
outfileAdr.close()
pickle.dump(tree1, outfileTree)
outfileTree.close()

