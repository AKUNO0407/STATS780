import yaml
import scipy
import streamlit as st
from yaml.loader import SafeLoader
import streamlit.components.v1 as components
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff 
from natsort import natsorted
import matplotlib.pyplot as plt
import numpy as np

from Data_Prep import normalize, data_prep, calculate_health_score

#credentials = pd.read_csv('user_credentials.csv')
data_raw = pd.read_excel('Input_Data_File.xlsx').iloc[:,1:]

data_pre = data_prep(data_raw)

data = calculate_health_score(data_pre)

data['Customer Success Associate'] = data['Customer Success Associate'].astype(str)
data['Parent Restaurant name'] = data['Parent Restaurant name'].astype(str)
data['Unique Location ID'] = data['Unique Location ID'].astype(str)

data1 = data.fillna(0)

comp = ['Order Discrepancy', 'Cancellation Rate', 'Missed Orders Rate', 'Churned','Total_Order_Value_norm',
        'Payment Status Score', 'Loyalty_norm','Normalized Retention Score', 'Delivery Partner Score', 'Highest Product Score']


feat_num = []
feat_obj = []

for iclm in data.columns.to_list():
    try:
        pd.to_numeric(data[iclm])
        feat_num.append(iclm)
    except (ValueError, TypeError):
        feat_obj.append(iclm)
        
data[feat_num] = data[feat_num].astype(float)  
num_lis = ['# Printers', '# Tablets', 'Number of online delivery partners', 'Highest Product_num','Total_Orders',
          'Retention Score','Churned','Total_Order_Value','Total_Cancellation','Total_Missed', 'Total_Printed', 'Health_Score']


orders_col = data.columns[data.columns.map(lambda x: x.startswith("Orders Week"))]
orders_col = natsorted(orders_col)
avg_val_col = data.columns[data.columns.map(lambda x: x.startswith("Average Order"))]
avg_val_col = natsorted(avg_val_col)
missed_rate = data.columns[data.columns.map(lambda x: x.startswith("Missed_Rate"))]
missed_rate = natsorted(missed_rate)
orders_change_rate = data.columns[data.columns.map(lambda x: x.startswith("Orders_Change"))]
orders_change_rate = natsorted(orders_change_rate)
orders_discrepancy_rate = data.columns[data.columns.map(lambda x: x.startswith("Orders_Discrepancy"))]
orders_discrepancy_rate = natsorted(orders_discrepancy_rate)
cancellation_rate = data.columns[data.columns.map(lambda x: x.startswith("Cancellation_Rate"))]
cancellation_rate = natsorted(cancellation_rate)


trends_dic = {
            "Total Orders":orders_col,
            "Average Order Value": avg_val_col,
            "Missed Orders": missed_rate,
            "Order Number Change Rate":orders_change_rate,
            "Order Discrepancy": orders_discrepancy_rate,
            "Cancellation Rates": cancellation_rate
}   


class SessionState:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
    

def authenticate(username, password):
    user = credentials[(credentials['username'] == username) & (credentials['password'] == password)]
    if user.empty:
        return None
    return user.iloc[0]['role']



    


def customer_accounts_view(data1):
        
    st.subheader("Metrics by CSA/Restaurant")
    

    def color_coding(row):
        if row['Health_Score'] <= 45:
            return ['background-color: red'] * len(row)
        elif row['Health_Score'] >= 70:
            return ['background-color: green'] * len(row)


    col1, col2, col3 = st.columns([1, 2, 2])

    with col1:
            
        associate_names = data1['Customer Success Associate'].unique()
        selected_associate = st.selectbox("Select Associate", associate_names)
        filtered_data_csa = data1[(data1['Customer Success Associate'] == selected_associate)]
                    
        res_lis = list(filtered_data_csa['Parent Restaurant name'].unique())+['Overall']
        trend_names = list(trends_dic.keys())
        selected_res = st.selectbox("Select Restaurant Name", res_lis)
        filtered_data_res = filtered_data_csa if selected_res == 'Overall' else filtered_data_csa[(filtered_data_csa['Parent Restaurant name'] == selected_res)]
              
        df_avg_trend = pd.DataFrame(columns = [f'Week_{i}' for i in range(1,len(orders_col)+1)]).T
        df_res_trend = pd.DataFrame(columns = [f'Week_{i}' for i in range(1,len(orders_col)+1)]).T
            
    
        for i in trends_dic.keys():
            if i == "Order Number Change Rate" :
                df_avg_trend[i] = [0] + list(data1[trends_dic[i]].mean())
                df_res_trend[i] = [0] + list(filtered_data_res[trends_dic[i]].mean())
            else:
                df_avg_trend[i] = list(data1[trends_dic[i]].mean())
                df_res_trend[i] = list(filtered_data_res[trends_dic[i]].mean())
    

    
    with col2:
        #col2.subheader("Health Scores Chart")
    
      #  fig_hs_hist, ax = plt.subplots(figsize=(8,5))
      #  ax.hist(filtered_data_csa['Health_Score'], bins=20, color='skyblue', edgecolor='black', alpha=0.7)

        fig_hs_hist = px.histogram(
            filtered_data_csa,
            x='Health_Score',
            nbins=20,
            title='Health Score Distribution with Average Line'
        )
        avg_hs = round(data['Health_Score'].mean(),2)
        fig_hs_hist.add_vline(x=avg_hs, line_dash="dash", line_color="red", name="Average")
    
    #    ax.axvline(avg_hs, color='red', linestyle='dashed', linewidth=2, label='Average')
    #    ax.set_xlabel('Health Score')
    #    ax.set_ylabel('Frequency')
    #    ax.set_title('Health Score Distribution with Average Line')
    #    ax.legend()
    
        st.plotly_chart(fig_hs_hist,use_container_width=True)

    with col3:
        ## Radar
       # col3.subheader("Components: Agg v.s. Selected Res")
        fig_radar = go.Figure()
        
        fig_radar.add_trace(go.Scatterpolar(
              r=data1[comp].mean(),
              theta=comp,
              fill='toself',
              name='Overall Avg'
        ))
        fig_radar.add_trace(go.Scatterpolar(
              r=filtered_data_res[comp].mean(),
              theta=comp,
              fill='toself',
              name='By CSA/Restaurant'
        ))
        
        fig_radar.update_layout(
          polar=dict(
            radialaxis=dict(
              visible=True,
              range=[0, 1]
            )),
          showlegend=True
        )
        
        st.plotly_chart(fig_radar, use_container_width=True)




    cl1, cl2 = st.columns([1, 3])
    filtered_data_csa['Unique Location ID'] = filtered_data_csa['Unique Location ID'].astype(str)
        
    comp_opration = ['Order Discrepancy', 'Cancellation Rate', 'Missed Orders Rate']
    comp_satisf = ['Churned','Payment Status Score', 'Loyalty_norm','Normalized Retention Score' ]
    comp_finance = ['Delivery Partner Score', 'Highest Product Score','Total_Order_Value_norm']
    opration_25p = np.percentile(data1[['Order Discrepancy', 'Cancellation Rate', 'Missed Orders Rate']].dot([-10,-5,-5]), 25)
    satisf_25p =  np.percentile(data1[['Churned','Payment Status Score', 'Loyalty_norm','Normalized Retention Score' ]].dot([-10,25,20,20]), 25)
    finance_25p =  np.percentile(data1[['Delivery Partner Score', 'Highest Product Score','Total_Order_Value_norm']].dot([10,20,25]), 25)

    df_opration_25p = filtered_data_csa[filtered_data_csa[['Order Discrepancy', 'Cancellation Rate', 'Missed Orders Rate']].dot([-10,-5,-5]) < opration_25p]
    df_satisf_25p =  filtered_data_csa[filtered_data_csa[['Churned','Payment Status Score', 'Loyalty_norm','Normalized Retention Score' ]].dot([-10,25,20,20]) < satisf_25p]
    df_finance_25p =  filtered_data_csa[filtered_data_csa[['Delivery Partner Score', 'Highest Product Score','Total_Order_Value_norm']].dot([10,20,25]) < finance_25p]
    df_churn = filtered_data_csa[filtered_data_csa['Churned'] == 1]
    col_comp = ['Parent Restaurant name','Unique Location ID'] + comp + ['Health_Score']
        
    with cl1:
        #col2.subheader("by Restaurant and Location")
        st.dataframe(filtered_data_csa[['Parent Restaurant name', 'Health_Score']].groupby(['Parent Restaurant name']).mean().style.apply(color_coding, axis=1))
   # with cl2:
   #     st.dataframe(filtered_data_csa[['Parent Restaurant name','Unique Location ID', 'Health_Score']].groupby(['Parent Restaurant name','Unique Location ID']).mean().style.apply(color_coding, axis=1))
    with cl2:

        seg = st.radio(
            "Select one of the segments below: ",
            ('Operational Issue', 'Customer Satisfaction', 'Financial Issue', 'Churned Customers')) 
        if seg == 'Operational Issue':
            cl3.subheader("Customers with Operational Issues")
            st.dataframe(df_opration_25p[col_comp].groupby(['Parent Restaurant name','Unique Location ID']).mean().style.apply(color_coding, axis=1))
        elif seg == 'Customer Satisfaction':
            cl3.subheader("Customers with Engagement Issue")
            st.dataframe(df_satisf_25p[col_comp].groupby(['Parent Restaurant name','Unique Location ID']).mean().style.apply(color_coding, axis=1))
        elif seg == 'Financial Issue':
            cl3.subheader("Customers with Financial Issue")
            st.dataframe(df_finance_25p[col_comp].groupby(['Parent Restaurant name','Unique Location ID']).mean().style.apply(color_coding, axis=1))
        else:
            cl3.subheader("Churned Customers")
            st.dataframe(df_churn[col_comp].groupby(['Parent Restaurant name','Unique Location ID']).mean().style.apply(color_coding, axis=1))
        
                
        
    
    c_avg1, c_avg2 = st.columns([1,1])
    
    with c_avg1:

    # Create the line chart using Plotly
        fig = go.Figure()
    
    # Add traces for Total Orders and Average Order Value
        fig.add_trace(go.Scatter(x=df_avg_trend.index, y=df_avg_trend['Total Orders'],
                             mode='lines+markers', name='Total Orders'))
        fig.add_trace(go.Scatter(x=df_avg_trend.index, y=df_avg_trend['Average Order Value'],
                                 mode='lines+markers', name='Average Order Value'))
        
        # Create a second y-axis
        fig.update_layout(yaxis=dict(title='Total Orders and Average Order Value'),
                          yaxis2=dict(title='Missed Orders, Change Rate, Discrepancy, Cancellation Rates',
                                      overlaying='y', side='right'))
        
        # Add traces for the second y-axis
        fig.add_trace(go.Scatter(x=df_avg_trend.index, y=df_avg_trend['Missed Orders'],
                                 mode='lines+markers', name='Missed Orders', yaxis='y2'))
        #fig.add_trace(go.Scatter(x=df_avg_trend.index, y=df_avg_trend['Order Number Change Rate'],
        #                         mode='lines+markers', name='Change Rate', yaxis='y2'))
        fig.add_trace(go.Scatter(x=df_avg_trend.index, y=df_avg_trend['Order Discrepancy'],
                                 mode='lines+markers', name='Discrepancy', yaxis='y2'))
        fig.add_trace(go.Scatter(x=df_avg_trend.index, y=df_avg_trend['Cancellation Rates'],
                                 mode='lines+markers', name='Cancellation Rates', yaxis='y2'))
        
    # Set layout and display the line chart
        fig.update_layout(title="Average Trend Line Chart",
                          xaxis=dict(title="Weeks"),
                          showlegend=True)
        
        st.plotly_chart(fig)

    with c_avg2:
        
    
    
        # Create the line chart using Plotly
        fig_res = go.Figure()
        
        # Add traces for Total Orders and Average Order Value
        fig_res.add_trace(go.Scatter(x=df_res_trend.index, y=df_res_trend['Total Orders'],
                             mode='lines+markers', name='Total Orders'))
        fig_res.add_trace(go.Scatter(x=df_res_trend.index, y=df_res_trend['Average Order Value'],
                                 mode='lines+markers', name='Average Order Value'))
        
        # Create a second y-axis
        fig_res.update_layout(yaxis=dict(title='Total Orders and Average Order Value'),
                          yaxis2=dict(title='Missed Orders, Change Rate, Discrepancy, Cancellation Rates',
                                      overlaying='y', side='right'))
        
        # Add traces for the second y-axis
        fig_res.add_trace(go.Scatter(x=df_res_trend.index, y=df_res_trend['Missed Orders'],
                                 mode='lines+markers', name='Missed Orders', yaxis='y2'))
        #fig_res.add_trace(go.Scatter(x=df_res_trend.index, y=df_res_trend['Order Number Change Rate'],
        #                         mode='lines+markers', name='Change Rate', yaxis='y2'))
        fig_res.add_trace(go.Scatter(x=df_res_trend.index, y=df_res_trend['Order Discrepancy'],
                                 mode='lines+markers', name='Discrepancy', yaxis='y2'))
        fig_res.add_trace(go.Scatter(x=df_res_trend.index, y=df_res_trend['Cancellation Rates'],
                                 mode='lines+markers', name='Cancellation Rates', yaxis='y2'))
        
        # Set layout and display the line chart
        fig_res.update_layout(title="Average Trend Line Chart by Associate/Restaurant",
                          xaxis=dict(title="Weeks"),
                           showlegend=True)
        
        st.plotly_chart(fig_res)
    


   
    
        


def main():

    st.set_page_config(layout="wide")
    st.title('Customer Success Dashboard - Welcome')


    '''
    Aggregate
    '''

    st.subheader("Overall Health Score Information")
    
    
    heal_perc = data[data['Health_Score'] >= 70]['Health_Score'].count()/len(data['Health_Score']) * 100
    
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric(label="Average Health Score", value=round(data['Health_Score'].mean(),2), delta= round(data['Health_Score'].mean()-55, 2))
    col2.metric(label="Healthy Customer (>=70) %", value= round(heal_perc,2), delta= round(heal_perc - 12, 2))
    col3.metric(label="Avg Weekly Order Number", value=round(data[orders_col[-1]].mean(), 0), 
                delta= round((data[orders_col[-2]].mean() - data[orders_col[-1]].mean()), 0))
    col4.metric(label="Avg Weekly Order Value", value=round(data[avg_val_col[-1]].mean(), 0), 
                delta= round((data[avg_val_col[-2]].mean() - data[avg_val_col[-1]].mean()), 0))
    col5.metric(label="Num of Churn", value=data['Churned'].sum(), delta= data['Churned'].sum()-1000)
    st.info('The charts presented above are intended for illustrative purposes only. Dynamic charts can be generated once additional data is obtained.', icon="ℹ️")


    
    ca1, ca2 = st.columns([2, 1])

    with ca1:
        #fig_health_score_distribution = px.histogram(data, x='Health_Score', nbins=10, title='Health Score Distribution')
        #fig = go.Figure()
        #fig.add_trace(fig_health_score_distribution.data[0])
        #fig.update_layout(title='Aggregated Performance', barmode='overlay', showlegend=False)
        hist_data = [data['Health_Score']]
        group_labels = ['Health_Score'] 
        
        fig = ff.create_distplot(hist_data,group_labels)
        st.plotly_chart(fig)
            
    with ca2:
        
        fig2 =go.Figure(go.Sunburst(
            labels= ["Weights",'Order Discrepancy', 'Cancellation Rate', 'Missed Orders Rate', 'Churn Score', 'Payment Status Score',
                          'Loyalty Score', 'Retention Score', 'Order Value Score','Delivery Partner Score', 'Highest Product Score'],
            parents=["", "Retention Score","Loyalty Score","Loyalty Score","Loyalty Score", 
                     'Weights','Weights', 'Weights', 'Weights',
                         'Weights', 'Weights'],
            values=[130,10, 5, 5, 10, 25, 20, 20, 25, 10, 20],
            marker=dict(colors= ["", '#e65d5d', '#ffa4a4','#ffb7a4','#ff7676','#5fc1d8','#7fcde0','#9fc5e8','#4c9aad','#afdeec','#7fb2e0']),
            branchvalues="total"
        ))
        fig2.update_layout(margin = dict(t=0, l=0, r=0, b=0))
                #fig2.update_traces(hoverinfo='label+percent', textinfo='value', textfont_size=20,
                #          marker=dict(colors=colors, line=dict(color='#000000', width=2)))

        st.plotly_chart(fig2, use_container_width=True)



    customer_accounts_view(data1)

    # Display additional content here

if __name__ == '__main__':
    main()
