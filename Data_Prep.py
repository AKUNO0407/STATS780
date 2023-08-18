import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.animation import FuncAnimation
from matplotlib.offsetbox import AnchoredText
from matplotlib.ticker import PercentFormatter
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
  retention_window = today_j - df['Activation Date'].min()
  
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


  df_orders_change_rate = df1[orders_col].pct_change(axis='columns', periods = 1).iloc[:,1:]
  df_orders_change_rate.columns = ['Orders_Change_Rate_{0}'.format(i) for i in range(2,len(orders_col)+1)]

  for i in range(1,len(orders_col)+1):
    df1[ = pd.DataFrame([(df_score[f'Orders Week {i}']  - df_score[f'Printed Orders Week {i}'])/
                        df_score[f'Orders Week {i}'] for i in range(1,len(orders_col)+1) ]).T
