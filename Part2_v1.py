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

from Data_Prep import normalize, data_prep, calculate_health_score

#credentials = pd.read_csv('user_credentials.csv')
data_raw = pd.read_excel('Input_Data_File.xlsx').iloc[:,1:]

data_pre = data_prep(data_raw)

data = calculate_health_score(data_pre)

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


class SessionState:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
    

def authenticate(username, password):
    user = credentials[(credentials['username'] == username) & (credentials['password'] == password)]
    if user.empty:
        return None
    return user.iloc[0]['role']



def aggregated_performance_view(data):
    
    # f_data = filtered_data if selected_item == 'Overall' else filtered_data[filtered_data['Payment Status'] == selected_item]

    st.subheader("Overall Health Score Information")
    
    
    heal_perc = data['Health_Score'][data['Health_Score'] >= 80].sum()/len(data['Health_Score'])
    
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric(label="Average Health Score", value=round(data['Health_Score'].mean(),2), delta= round(data['Health_Score'].mean()-55, 2))
    col2.metric(label="Healthy Customer (>=80) %", value= round(heal_perc,2), delta= round((heal_perc - 0.4)/heal_perc, 2))
    col3.metric(label="Avg Weekly Order Number", value=round(data[orders_col[-1]].mean(), 0), 
                delta= round((data[orders_col[-2]].mean() - data[orders_col[-1]].mean()), 0))
    col4.metric(label="Avg Weekly Order Number", value=round(data[orders_col[-1]].mean(), 0), 
                delta= round((data[orders_col[-2]].mean() - data[orders_col[-1]].mean()), 0))
    col5.metric(label="Num of Churn", value=data['Churned'].sum(), delta= data['Churned'].sum()-1000)
    st.info('The charts presented above are intended for illustrative purposes only. Dynamic charts can be generated once additional data is obtained.', icon="ℹ️")


    
    ca1, ca2 = st.columns([7, 3])

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
    


    

#    df_gp = data.groupby(['Parent Restaurant name'])[num_lis].sum()
#    df_gp['Avg Health Score'] = data.groupby(['Parent Restaurant name'])['Health_Score'].mean()
#    df_gp['Number of location'] = data.groupby(['Parent Restaurant name'])['Unique Location ID'].count()
    
#    st.dataframe(round(df_gp,2))








def customer_accounts_view(data):
    data1 = data.fillna(0)
    
    trends_dic = {
            "Total Orders":orders_col,
            "Average Order Value": avg_val_col,
            "Missed Orders": missed_rate,
            "Order Number Change Rate":orders_change_rate,
            "Order Discrepancy": orders_discrepancy_rate,
            "Cancellation Rates": cancellation_rate
        }    

    
    associate_names = data1['Customer Success Associate'].str.strip().unique()
    selected_associate = st.selectbox("Select Associate", associate_names)
    filtered_data_csa = data1[(data['Customer Success Associate'].str.strip() == selected_associate)]
    
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


    
    c_avg1, c_avg2 = st.columns([1,1])
    
    with c_avg1:
        #st.title("Average Trend Line Chart")

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
        
    
        #st.title("Average Trend Line Chart For Selected Restaurant")
    
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
    


    

    col1, col2, col3 = st.columns([1, 1,1])
    
    col1.subheader("Health Scores Chart")
    
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
    
    col1.plotly_chart(fig_hs_hist)
   # col1.line_chart(filtered_data_csa['Health_Score'])
    
    col2.subheader("Health Scores by Restaurant and Location")
    col2.write(filtered_data_csa[['Parent Restaurant name', 'Unique Location ID', 'Health_Score']].groupby(['Parent Restaurant name']).mean())
    col3.write(filtered_data_csa[['Unique Location ID', 'Health_Score']].groupby(['Unique Location ID']).mean())


    
    
    
        


def main():


    st.set_page_config(layout="wide")
    st.title('Customer Success Dashboard - Welcome')


    aggregated_performance_view(data)

    st.subheader("Associate Information Summary")

    col1, col2 = st.columns([1,1])
    with col1:
        fig_scat = px.scatter(data, x="Health_Score", y='Total_Order_Value', color='Customer Success Associate',
                size="Total_Order_Value_norm", 
                hover_data=["Parent Restaurant name", 'Retention Score','Churned' ])
        st.plotly_chart(fig_scat)

    with col2:
        fig_hist = px.histogram(data, x = 'Health_Score', color="Customer Success Associate",
                               marginal="box", # or violin, rug
                               hover_data=num_lis)
        st.plotly_chart(fig_hist)
            
    #df_gp = data.groupby(['Customer Success Associate'])[num_lis].sum()
    #df_gp[['Avg Retention Score','Avg Health Score']] = data.groupby(['Customer Success Associate'])[['Retention Score','Health_Score']].mean()
    #df_gp['Number of location'] = data.groupby(['Customer Success Associate'])['Unique Location ID'].count()
    #st.dataframe(round(df_gp, 2))
            
    #filtered_data_as = data[data['Customer Success Associate'].str.strip() == username]

    customer_accounts_view(data)

    # Display additional content here

if __name__ == '__main__':
    main()
