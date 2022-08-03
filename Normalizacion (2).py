import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

customers = pd.read_csv('C:/Users/notebook/OneDrive/Escritorio/Henry clase/Proyecto grupal OLIST/e-comerce_Olist_dataset/olist_customers_dataset.csv')
geolocation  = pd.read_csv('C:/Users/notebook/OneDrive/Escritorio/Henry clase/Proyecto grupal OLIST/e-comerce_Olist_dataset/olist_geolocation_dataset.csv')
parse_dates = ["shipping_limit_date"]
order_items  = pd.read_csv('C:/Users/notebook/OneDrive/Escritorio/Henry clase/Proyecto grupal OLIST/e-comerce_Olist_dataset/olist_order_items_dataset.csv',\
                              infer_datetime_format = True, parse_dates = parse_dates)
parse_dates = ['review_creation_date','review_answer_timestamp']
order_reviews = pd.read_csv('C:/Users/notebook/OneDrive/Escritorio/Henry clase/Proyecto grupal OLIST/e-comerce_Olist_dataset/olist_order_reviews_dataset.csv',\
                              infer_datetime_format = True, parse_dates = parse_dates)
order_payments = pd.read_csv('C:/Users/notebook/OneDrive/Escritorio/Henry clase/Proyecto grupal OLIST/e-comerce_Olist_dataset/olist_order_payments_dataset.csv')
parse_dates = ['order_purchase_timestamp','order_approved_at', 'order_delivered_carrier_date', 'order_delivered_customer_date', 'order_estimated_delivery_date']
orders = pd.read_csv('C:/Users/notebook/OneDrive/Escritorio/Henry clase/Proyecto grupal OLIST/e-comerce_Olist_dataset/olist_orders_dataset.csv',\
                              infer_datetime_format = True, parse_dates = parse_dates)
products = pd.read_csv('C:/Users/notebook/OneDrive/Escritorio\Henry clase/Proyecto grupal OLIST/e-comerce_Olist_dataset/olist_products_dataset.csv')
sellers = pd.read_csv('C:/Users/notebook/OneDrive/Escritorio/Henry clase/Proyecto grupal OLIST/e-comerce_Olist_dataset/olist_sellers_dataset.csv')
product_category = pd.read_csv('C:/Users/notebook/OneDrive/Escritorio/Henry clase/Proyecto grupal OLIST/e-comerce_Olist_dataset/product_category_name_translation.csv')
parse_dates = ['won_date']
closed_deals = pd.read_csv('C:/Users/notebook/OneDrive/Escritorio/Henry clase/Proyecto grupal OLIST/Olist_Funnel_marketing/olist_closed_deals_dataset.csv',\
                              infer_datetime_format = True, parse_dates = parse_dates)
parse_dates = ['first_contact_date']
marketing_q = pd.read_csv('C:/Users/notebook/OneDrive/Escritorio/Henry clase/Proyecto grupal OLIST/Olist_Funnel_marketing/olist_marketing_qualified_leads_dataset.csv',\
                              infer_datetime_format = True, parse_dates = parse_dates)

customers['customer_city'] = customers.customer_city.str.title()
customers.to_csv(r'C:/Users/notebook/OneDrive/Escritorio/Henry clase/Proyecto grupal OLIST/csv normalizados/CustomersNor.csv', index =False, header=True)

geolocation["geolocation_city"]=[x.replace('á',"a") for x in geolocation["geolocation_city"]]
geolocation["geolocation_city"]=[x.replace('é',"e") for x in geolocation["geolocation_city"]]
geolocation["geolocation_city"]=[x.replace('í',"i") for x in geolocation["geolocation_city"]]
geolocation["geolocation_city"]=[x.replace('ó',"o") for x in geolocation["geolocation_city"]]
geolocation["geolocation_city"]=[x.replace('ú',"u") for x in geolocation["geolocation_city"]]
geolocation["geolocation_city"]=[x.replace('ã',"a") for x in geolocation["geolocation_city"]]
geolocation["geolocation_city"]=[x.replace('â',"a") for x in geolocation["geolocation_city"]]
geolocation["geolocation_city"]=[x.replace('à',"a") for x in geolocation["geolocation_city"]]
geolocation["geolocation_city"]=[x.replace('ç',"c") for x in geolocation["geolocation_city"]]
geolocation["geolocation_city"]=[x.replace('ê',"e") for x in geolocation["geolocation_city"]]
geolocation["geolocation_city"]=[x.replace('õ',"o") for x in geolocation["geolocation_city"]]
geolocation["geolocation_city"]=[x.replace('ô',"o") for x in geolocation["geolocation_city"]]
geolocation["geolocation_city"]=[x.replace('ü',"u") for x in geolocation["geolocation_city"]]

geolocation['geolocation_city'] = geolocation.geolocation_city.str.title()

geolocation.to_csv(r'C:/Users/notebook/OneDrive/Escritorio/Henry clase/Proyecto grupal OLIST/csv normalizados/GeolocationNor.csv', index =False, header=True)

order_items['shipping_limit_date'] = order_items['shipping_limit_date'].dt.date

order_items['shipping_limit_date'] = pd.to_datetime(order_items['shipping_limit_date'])

order_items.to_csv(r'C:/Users/notebook/OneDrive/Escritorio/Henry clase/Proyecto grupal OLIST/csv normalizados/Order_itemsNor.csv', index =False, header=True)

order_payments.drop(order_payments[order_payments.payment_value < 10].index, inplace=True)
order_payments.drop(order_payments[order_payments.payment_value == 13664.08].index, inplace=True)
order_payments.to_csv(r'C:/Users/notebook/OneDrive/Escritorio/Henry clase/Proyecto grupal OLIST/csv normalizados/Order_paymentsNor.csv', index =False, header=True)

order_reviews['review_answer_timestamp'] = order_reviews['review_answer_timestamp'].dt.date

order_reviews['review_answer_timestamp'] = pd.to_datetime(order_reviews['review_answer_timestamp'])

order_reviews['review_comment_title'].fillna('Sin Dato', inplace = True)
order_reviews['review_comment_message'].fillna('Sin Dato', inplace = True)

order_reviews.drop_duplicates(['review_id'], inplace=True)
order_reviews.to_csv(r'C:/Users/notebook/OneDrive/Escritorio/Henry clase/Proyecto grupal OLIST/csv normalizados/Order_reviewsNor.csv', index =False, header=True)

orders['order_purchase_timestamp'] = orders['order_purchase_timestamp'].dt.date
orders['order_approved_at'] = orders['order_approved_at'].dt.date
orders['order_delivered_carrier_date'] = orders['order_delivered_carrier_date'].dt.date
orders['order_delivered_customer_date'] = orders['order_delivered_customer_date'].dt.date
orders['order_estimated_delivery_date'] = orders['order_estimated_delivery_date'].dt.date

orders['order_purchase_timestamp'] = pd.to_datetime(orders['order_purchase_timestamp'])
orders['order_approved_at'] = pd.to_datetime(orders['order_approved_at'])
orders['order_delivered_carrier_date'] = pd.to_datetime(orders['order_delivered_carrier_date'])
orders['order_delivered_customer_date'] = pd.to_datetime(orders['order_delivered_customer_date'])
orders['order_estimated_delivery_date'] = pd.to_datetime(orders['order_estimated_delivery_date'])

orders.to_csv(r'C:/Users/notebook/OneDrive/Escritorio/Henry clase/Proyecto grupal OLIST/csv normalizados/OrdersNor.csv', index =False, header=True)

products['product_category_name'].fillna('Sin Dato', inplace = True)
products['product_name_lenght'].fillna(0.0, inplace = True)
products['product_description_lenght'].fillna(0.0, inplace = True)
products['product_photos_qty'].fillna(0.0, inplace = True)
products['product_weight_g'].fillna(0.0, inplace = True)
products['product_length_cm'].fillna(0.0, inplace = True)
products['product_height_cm'].fillna(0.0, inplace = True)
products['product_width_cm'].fillna(0.0, inplace = True)

products['product_category_name'] = products.product_category_name.str.title()

products[['product_name_lenght', 'product_description_lenght', 'product_photos_qty', 'product_weight_g', 'product_length_cm', 'product_height_cm', 'product_width_cm']].astype(float)

products.to_csv(r'C:/Users/notebook/OneDrive/Escritorio/Henry clase/Proyecto grupal OLIST/csv normalizados/ProductsNor.csv', index =False, header=True)

sellers['seller_city'] = sellers.seller_city.str.title()
sellers.to_csv(r'C:/Users/notebook/OneDrive/Escritorio/Henry clase/Proyecto grupal OLIST/csv normalizados/SellersNor.csv', index =False, header=True)

product_category['product_category_name'] = product_category.product_category_name.str.title()
product_category['product_category_name_english'] = product_category.product_category_name_english.str.title()

product_category.to_csv(r'C:/Users/notebook/OneDrive/Escritorio/Henry clase/Proyecto grupal OLIST/csv normalizados/Product_categoryNor.csv', index =False, header=True)

closed_deals['won_date'] = closed_deals['won_date'].dt.date

closed_deals['won_date'] = pd.to_datetime(closed_deals['won_date'])

closed_deals.drop(columns='has_company',inplace=True)
closed_deals.drop(columns='has_gtin',inplace=True)
closed_deals.drop(columns='average_stock',inplace=True)
closed_deals.drop(columns='declared_product_catalog_size',inplace=True)

closed_deals["business_segment"].fillna("Sin Dato", inplace=True)
closed_deals["lead_type"].fillna("Sin Dato", inplace=True)
closed_deals["lead_behaviour_profile"].fillna("Sin Dato", inplace=True)
closed_deals["business_type"].fillna("Sin Dato", inplace=True)

closed_deals.to_csv(r'C:/Users/notebook/OneDrive/Escritorio/Henry clase/Proyecto grupal OLIST/csv normalizados/Closed_dealsNor.csv', index =False, header=True)

marketing_q['origin'] = marketing_q.origin.str.title()

marketing_q["origin"].fillna("Sin Dato", inplace=True)

marketing_q.to_csv(r'C:/Users/notebook/OneDrive/Escritorio/Henry clase/Proyecto grupal OLIST/csv normalizados/MarketingNor.csv', index =False, header=True)
