import numpy as np
import pandas as pd
import datetime

def normalize(arr,t_min, t_max):
    norm_arr = []
    clip_min = np.percentile(arr, 1)
    clip_max = np.percentile(arr, 99)
    diff = t_max - t_min
    diff_arr = clip_max - clip_min   

    for i in arr:
        temp = (((i - clip_min)*diff)/ diff_arr) + t_min
        temp = min(temp, 1)
        norm_arr.append(temp)
        
    return norm_arr
  

def data_prep(df1):
    orders_col = df1.columns[df1.columns.map(lambda x: x.startswith("Orders Week"))]
    orders_col = sorted(orders_col, key = lambda sub : sub[-1])
    avg_val_col = df1.columns[df1.columns.map(lambda x: x.startswith("Average Order"))]
    avg_val_col = sorted(avg_val_col, key = lambda sub : sub[-1])
    df1['Total_orders'] = df1[orders_col].sum(axis=1) # Total order numbers
    df1['Total_Cancellation'] = df1[df1.columns[df1.columns.map(lambda x: x.startswith("Cancellations"))]].sum(axis=1)
    df1['Total_Missed'] = df1[df1.columns[df1.columns.map(lambda x: x.startswith("Missed Orders"))]].sum(axis=1)
    df1['Total_Printed'] = df1[df1.columns[df1.columns.map(lambda x: x.startswith("Printed Orders"))]].sum(axis=1)
  
    df_total_val = pd.DataFrame([df1[orders_col[i]].multiply(df1[avg_val_col[i]]) for i in range(len(avg_val_col))]).T
    df_total_val.columns = ['Total_Order_Val_Week_{0}'.format(i) for i in range(1,len(orders_col)+1)]
  
    df1['Total_Order_Value'] = df_total_val.sum(axis=1)
    df1['Total_Order_Value_norm'] = normalize(df1['Total_Order_Value'],0,1)
  
  ## Simplified Retention Score based on 'Last Product Usage Date' and 'Activation Date'
  ## Retention Score = (Time Active in Retention Window) / (Total Time Since Activation)
  ## Assume retention window is from the min. of the 'Activation Date' till today

    today_j = int(pd.Timestamp.today().strftime('%y%j'))
    act_min = df1['Activation Date'].min() 
    retention_window = today_j - act_min
  
  # Calculate time since activation and retention score
    df1['Time Active'] = df1['Last Product Usage Date'] - df1['Activation Date']
    df1['Retention Score'] = df1['Time Active'].apply(lambda x: min(x / retention_window, 1.0))
    df1['Normalized Retention Score'] = (df1['Retention Score'] - df1['Retention Score'].min()) / (df1['Retention Score'].max() - df1['Retention Score'].min())

    df1['Loyalty'] = df1['Last Product Usage Date'] - df1['Activation Date'] #longer the better, but not signif

  ## Churn Rate: voluntary + involuntary
  ## Assume invol. churned if not active after Aug 2021; vol churn: payment status = cancelled

    churn_thre = int(pd.Timestamp('08/01/2021').strftime('%y%j'))
    df1['Churned'] = [(1 if ((last_usage < churn_thre) or (payment_status == 'Cancelled')) else 0)
                  for last_usage, payment_status in zip(df1['Last Product Usage Date'], df1['Payment Status'])]

    df1['Normalized Retention Score'] = (df1['Retention Score'] - df1['Retention Score'].min()) / (df1['Retention Score'].max() - df1['Retention Score'].min())
    df1['Loyalty_norm'] = normalize(df1['Loyalty'],0,1)
    df1['Total_Order_Value_norm'] = normalize(df1['Total_Order_Value'],0,1)
    df1['Loyalty_norm'] = normalize(df1['Loyalty'],0,1)
    
    df1[['Orders_Change_Rate_{0}'.format(i) for i in range(2,len(orders_col)+1)]] = df1[orders_col].pct_change(axis='columns', periods = 1).iloc[:,1:]
    
    for i in range(1,len(orders_col)+1):
        df1[f'Orders_Discrepancy_Rate_{i}'] = (df1[f'Orders Week {i}']  - df1[f'Printed Orders Week {i}'])/df1[f'Orders Week {i}']
        df1[f'Cancellation_Rate_{i}'] = (df1[f'Cancellations Week {i}'])/df1[f'Orders Week {i}']
        df1[f'Missed_Rate_{i}'] = (df1[f'Missed Orders Week {i}'])/df1[f'Orders Week {i}']

    return df1



    

def calculate_health_score(row):
    # Define weights for different factors (adjust as per business needs)
    weights = {
        'Order Discrepancy': - 10,
        'Cancellation Rate': - 5,
        'Missed Orders Rate': - 5,
        'Churn Score': -10,
        
        'Payment Status Score': 25,
        'Order Value Score': 25,
        'Loyalty Score' : 20,
        'Retention Score': 20,

#        'Feature Adoption': 10,
        'Delivery Partner Score': 10,
        'Highest Product Score': 20
        
    } # weights in percentage
    

    # order fulfillment and operational efficiency: 
    # significant discrepancy b/w ttl oders and printed orders could be a red flag
    # Cancellation may indicates dissatisfaction, and missed oders may indicates low operational efficiency 
    # It may signify that the restaurant is facing challenges in fulfilling customer orders or managing their operational processes effectively

    
    if row['Total_orders'] != 0:
        order_disc_rate = (row['Total_orders']  - row['Total_Printed'])/row['Total_orders'] 
        cancellation_rate = row['Total_Cancellation'] / row['Total_orders']
        missed_rate = row['Total_Missed']  / row['Total_orders']
    else:
        order_disc_rate = cancellation_rate = missed_rate = 0
    
    
    # Payment Status Score: Higher score for 'Active' status
    payment_status_score = 1 if row['Payment Status'] == 'Active' else 0.5
    
    # Payment Status Score
    order_value_score = row['Total_Order_Value_norm']
    
    # Activation Date Score: early activation date may indicate stable and loyal partnership
    loyalty_score = row['Loyalty_norm'] 

    retention_score = row['Normalized Retention Score']
    if_churn = row['Churned']

    
    # Printer and Tablet Score: Higher score for more devices requested 
    # feature_adoption_score = (row['# Printers']/df1['# Printers'].max() + row['# Tablets']/df1['# Tablets'].max())/2
    
    # More delivery partners may indicate more product nt65eeds 
    del_partner_score = row['Number of online delivery partners']/df1['Number of online delivery partners'].max()
    
    high_product_score = row['Highest Product_num']/df1['Highest Product_num'].max()

    # Calculate the final health score
    health_score = (
        weights['Order Discrepancy'] * order_disc_rate +
        weights['Cancellation Rate'] * cancellation_rate +
        weights['Missed Orders Rate'] * missed_rate + 
        weights['Churn Score'] * if_churn + 
        
        weights['Payment Status Score'] * payment_status_score +
        weights['Order Value Score'] * order_value_score +
        weights['Loyalty Score'] * loyalty_score +
        weights['Retention Score'] * retention_score +

       # weights['Feature Adoption Score'] * feature_adoption_score + 
        weights['Delivery Partner Score'] * del_partner_score +
        weights['Highest Product Score'] * high_product_score
        
    )
    
    
    #print([order_disc_rate,cancellation_rate,missed_rate,payment_status_score,order_value_score,activation_date_score,printer_tablet_score,del_partner_score,high_product_score])

    return health_score



    
