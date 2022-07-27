from cgitb import reset
import streamlit as st
import pandas as pd
import folium
from math import radians, sin, cos, asin, sqrt
import numpy as np
from automatic_athena_download import traer_df



def load_data():
    if 'datosleidos' not in st.session_state:
        st.write("Estoy en el IF!!!!")
        st.session_state['datosleidos'] = True
        st.session_state['order_items'] =traer_df('SELECT * FROM processed_order_items')
        st.session_state['products'] = traer_df('SELECT * FROM processed_products')
        st.session_state['sellers'] = traer_df('SELECT * FROM processed_sellers')
        st.session_state['customers'] = traer_df('SELECT * FROM processed_customers')
        st.session_state['order_payments']= traer_df('SELECT * FROM processed_order_payments')
        st.session_state['order_reviews']  = traer_df('SELECT * FROM processed_order_reviews')
        st.session_state['marketing_q'] =pd.read_csv('csv normalizados\csv normalizados\MarketingNor.csv', infer_datetime_format = True)
        st.session_state['closed_deals']=traer_df('SELECT * FROM processed_closed_deals')
        parse_dates = ['order_purchase_timestamp','order_approved_at', 'order_delivered_carrier_date', 'order_delivered_customer_date', 'order_estimated_delivery_date']
        st.session_state['orders']= traer_df('SELECT * FROM processed_orders')
        st.session_state['orders2']=load_order_with_hours()
        st.session_state['geolocalization']=pd.read_csv('geolocation.csv',delimiter = ',',encoding = "utf-8")
        st.session_state['geo']=traer_df('SELECT * FROM processed_geolocation')
        st.session_state['clientesagrup']=generate_clientes_loc()
        st.session_state['vendedoresagrup']=generate_vendedores_loc()
        st.session_state['juntos']=generate_vend_clien_loc()
        st.session_state['all']=generate_alls()
        st.session_state['customers']=app_map_state_customer(st.session_state['customers'])
        st.session_state['sellers']=app_map_state_seller(st.session_state['sellers'])

def load_order_with_hours():
    orders2= pd.read_csv('olist_orders_dataset.csv')
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

    return orders2


def generate_clientes_loc():
    clientes=st.session_state['customers']
    nuevo=st.session_state['geolocalization']
    clientes=pd.merge(clientes, nuevo, on='customer_state' , how='left')
    clientesagrup = clientes.groupby('customer_state').agg({'geolocation_lat':'mean','geolocation_lng':'mean','customer_state':'count'})
    clientesagrup.rename(columns={'customer_state':'cantidad'}, inplace=True)
    clientesagrup.reset_index(inplace=True)
    return clientesagrup


def generate_vendedores_loc():
    vendedores=st.session_state['sellers']
    nuevo=st.session_state['geolocalization']   
    vendedores=vendedores.rename(columns={'seller_state':'state'})
    nuevo.reset_index(inplace=True)
    nuevo.rename(columns={'customer_state':'state'}, inplace=True)
    vendedores=pd.merge(vendedores, nuevo, on='state' , how='left')
    vendedoresagrup = vendedores.groupby('state').agg({'geolocation_lat':'mean','geolocation_lng':'mean','state':'count'})
    vendedoresagrup.rename(columns={'state':'cantidad'}, inplace=True)
    vendedoresagrup.reset_index(inplace=True)
    return vendedoresagrup


def generate_vend_clien_loc():
    clientesagrup=st.session_state['clientesagrup']
    vendedoresagrup=st.session_state['vendedoresagrup']
    clientesagrup.rename(columns={'customer_state':'state'}, inplace=True)
    juntos=pd.merge(clientesagrup, vendedoresagrup, on='state' , how='inner')
    juntos.rename(columns={'cantidad_x':'clientes', 'cantidad_y':'vendedores'}, inplace=True)
    juntos.drop(columns=['geolocation_lat_x','geolocation_lng_x','geolocation_lat_y','geolocation_lng_y'],inplace=True)
    juntos.sort_values("clientes", inplace=True, ascending=False)
    return juntos


def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Compute distance between two pairs of (lat, lng)
    """
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return 2 * 6371 * asin(sqrt(a))

def generate_alls():
    orders=st.session_state['orders']
    geolocation=st.session_state['geo']
    sellers=st.session_state['sellers']
    customers=st.session_state['customers']
    customers=app_map_state_customer(customers)
    products=st.session_state['products']
    order_items=st.session_state['order_items']
    orders[['order_purchase_timestamp','order_approved_at','order_delivered_customer_date','order_estimated_delivery_date',]]=orders[['order_purchase_timestamp',
        'order_approved_at','order_delivered_customer_date','order_estimated_delivery_date']].apply(pd.to_datetime)
    oneday = pd.Timedelta(days=1)

    orders['time_delay'] = (orders['order_delivered_customer_date'] - orders['order_estimated_delivery_date']) / oneday
    orders['est_to_deliver'] = np.where(orders['time_delay']<0, 1, 0)
    order_items = pd.merge(order_items, sellers[['seller_id', 'seller_zip_code_prefix']], left_on='seller_id', right_on='seller_id').drop(['order_item_id','shipping_limit_date'], axis=1)
    merge_df = pd.merge(order_items, orders, left_on='order_id', right_on='order_id', how='left')
    merge_df = pd.merge(merge_df, customers[['customer_id', 'customer_zip_code_prefix','customer_state','customer_state_description']], how='left',left_on='customer_id',right_on='customer_id')
    geo = geolocation.groupby('geolocation_zip_code_prefix').mean().reset_index()
    merge_df = pd.merge(merge_df, geo[['geolocation_zip_code_prefix', 'geolocation_lat', 'geolocation_lng']], how='left', 
                        left_on='seller_zip_code_prefix', right_on='geolocation_zip_code_prefix').rename(columns={'geolocation_lat': 'seller_lat', 
                                                                                                                'geolocation_lng': 'seller_lon'})
    merge_df = pd.merge(merge_df, geo[['geolocation_zip_code_prefix', 'geolocation_lat', 'geolocation_lng']], how='inner', 
                        left_on='customer_zip_code_prefix', right_on='geolocation_zip_code_prefix').rename(columns={'geolocation_lat': 'customer_lat', 
                                                                                                                'geolocation_lng': 'customer_lon'})
    merge_df = pd.merge(merge_df, products[['product_id','product_category_name','product_photos_qty','product_weight_g','product_length_cm','product_height_cm','product_width_cm']], 
                    left_on='product_id', right_on='product_id', how='left')
    merge_df['product_volume_cm3']=merge_df.product_length_cm * merge_df.product_height_cm * merge_df.product_width_cm
    merge_df.order_delivered_customer_date = pd.to_datetime(merge_df.order_delivered_customer_date)
    merge_df.order_delivered_carrier_date = pd.to_datetime(merge_df.order_delivered_carrier_date)
    merge_df.order_purchase_timestamp = pd.to_datetime(merge_df.order_purchase_timestamp)
    merge_df.order_estimated_delivery_date = pd.to_datetime(merge_df.order_estimated_delivery_date)
    merge_df['purchase_month']=merge_df.order_purchase_timestamp.dt.month
    merge_df['purchase_day_of_week']=merge_df.order_purchase_timestamp.dt.day_of_week
    merge_df['actual_delivery_time']=(merge_df.order_delivered_customer_date-merge_df.order_purchase_timestamp).dt.days
    merge_df['carrier_delivery_time']=(merge_df.order_delivered_carrier_date-merge_df.order_purchase_timestamp).dt.days
    merge_df['estimated_delivery_time']=(merge_df.order_estimated_delivery_date-merge_df.order_purchase_timestamp).dt.days

    merge_df['distance'] = merge_df.apply(
        lambda row: haversine_distance(
            row['seller_lat'],
            row['seller_lon'],
            row['customer_lat'],
            row['customer_lon'],
        ),
        axis=1,
    )

    merge_df=merge_df.drop(['order_status','product_length_cm','product_height_cm', 'order_delivered_carrier_date', 
                            'product_width_cm', 'order_id', 'product_id', 'order_purchase_timestamp', 'order_delivered_customer_date', 
                            'product_category_name', 'seller_id', 'customer_zip_code_prefix', 'seller_zip_code_prefix', 'customer_id', 'order_estimated_delivery_date', 
                            'geolocation_zip_code_prefix_x', 'geolocation_zip_code_prefix_y', 'order_approved_at', 'product_photos_qty', 'seller_lat', 
                            'seller_lon', 'customer_lat', 'customer_lon'], axis=1, errors='ignore')
    merge_df = merge_df.dropna()

    return merge_df

def aplicar_region(df):
    lNorte =[ 'RO','AM','RN','PA','TO']
    lCentro=['MT','DF','GO','MS']
    lSur=['PR','SC','RS']
    lSudeste=['MG','ES','RJ','SP']
    lNordeste=['MA','PI','BA','SE','PE','PB','CE']
    df['region']='Sin dato'
    df["region"]=df.apply(lambda x: 'Center'if x["customer_state"] in lCentro else x["region"], axis=1)
    df["region"]=df.apply(lambda x: 'South'if x["customer_state"] in lSur else x["region"], axis=1)
    df["region"]=df.apply(lambda x: 'Southeast'if x["customer_state"] in lSudeste else x["region"], axis=1)
    df["region"]=df.apply(lambda x: 'North'if x["customer_state"] in lNorte else x["region"], axis=1)
    df["region"]=df.apply(lambda x: 'Northeast'if x["customer_state"] in lNordeste else x["region"], axis=1)

    return df

def app_map_state_customer(df):
    Subjects = {'RO':'Romaima',
    'AM': 'Amazonas',
    'RN': 'Rondonia',
    'PA': 'Para',
    'MS': 'Mato Grosso do Sul',
    'DF': 'Distrito Federal',
    'MT': 'Mato Grosso',
    'GO': 'Goiras',
    'PR': 'Parana',
    'SC': 'Santa Catarina',
    'RS': 'Rio Grande do Sul',
    'MG': 'Minas Gerais',
    'RJ': 'Rio de Janeiro',
    'SP': 'Sao Paulo',
    'MA': 'Maranhao',
    'PI': 'Piaui',
    'BA': 'Bahia',
    'SE': 'Sergipe',
    'PE': 'Permambuco',
    'PB': 'Paraiba',
    'CE': 'Ceara',
    'TO': 'Tocantins',
    'ES': 'Espiritu Santo',
    'AP': 'Amapa'}
    df["customer_state_description"] = df["customer_state"].map(Subjects)
    
    return df

def app_map_state_seller(df):
    Subjects = {'RO':'Romaima',
    'AM': 'Amazonas',
    'RN': 'Rondonia',
    'PA': 'Para',
    'MS': 'Mato Grosso do Sul',
    'DF': 'Distrito Federal',
    'MT': 'Mato Grosso',
    'GO': 'Goiras',
    'PR': 'Parana',
    'SC': 'Santa Catarina',
    'RS': 'Rio Grande do Sul',
    'MG': 'Minas Gerais',
    'RJ': 'Rio de Janeiro',
    'SP': 'Sao Paulo',
    'MA': 'Maranhao',
    'PI': 'Piaui',
    'BA': 'Bahia',
    'SE': 'Sergipe',
    'PE': 'Permambuco',
    'PB': 'Paraiba',
    'CE': 'Ceara',
    'TO': 'Tocantins',
    'ES': 'Espiritu Santo',
    'AP': 'Amapa'}
    df["seller_state_description"] = df["seller_state"].map(Subjects)
    
    return df


