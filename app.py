import streamlit as st
import pandas as pd
# import base64
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from automatic_athena_download import *
import page_config 
#from secretsaws import access_key, secret_access_key

page_config.run()

st.title('Demostracion Olist')


df_all=traer_df('SELECT * FROM processed_customers')
listaestados=df_all.customer_state.unique()
st.sidebar.header('User Input Features')
selected_state = st.sidebar.selectbox('Estado', listaestados)


@st.cache
def load_data(result):
    query="SELECT * FROM processed_customers WHERE customer_state =" +"'"+result+"';"
    tabla=traer_df(query)
    return tabla
tablaolist = load_data(selected_state)



# Sidebar - city selection
sorted_unique_city = sorted(tablaolist.customer_city.unique())
selected_city = st.sidebar.multiselect('city', sorted_unique_city, sorted_unique_city)


# Filtering data
df_selected_city = tablaolist[(tablaolist.customer_city.isin(selected_city))]

st.header('Customers for city')
st.write('Data Dimension: ' + str(df_selected_city.shape[0]) + ' rows and ' + str(df_selected_city.shape[1]) + ' columns.')
st.dataframe(df_selected_city)


# def filedownload(df):
#     csv = df.to_csv(index=False)
#     b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
#     href = f'<a href="data:file/csv;base64,{b64}" download="playerstats.csv">Download CSV File</a>'
#     return href

# st.markdown(filedownload(df_selected_city), unsafe_allow_html=True)

# BARPLOT
if st.button('Ver Barplot'):
    st.header('Barplot')
    

    f, ax = plt.subplots(figsize=(7, 5))
    ax = sns.countplot(x=df_all.customer_state, data=df_all)
    st.set_option('deprecation.showPyplotGlobalUse', False)
    st.pyplot()