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
missed_col = data.columns[data.columns.map(lambda x: x.startswith("Missed Order"))]
missed_col = natsorted(missed_col)
orders_change_rate = data.columns[data.columns.map(lambda x: x.startswith("Orders_Change"))]
orders_change_rate = natsorted(orders_change_rate)
orders_discrepancy_rate = data.columns[data.columns.map(lambda x: x.startswith("Orders_Discrepancy"))]
orders_discrepancy_rate = natsorted(orders_discrepancy_rate)
cancellation_col = data.columns[data.columns.map(lambda x: x.startswith("Cancellation"))]
cancellation_col = natsorted(cancellation_col)


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
    


    

    df_gp = data.groupby(['Parent Restaurant name'])[num_lis].sum()
    df_gp['Avg Health Score'] = data.groupby(['Parent Restaurant name'])['Health_Score'].mean()
    df_gp['Number of location'] = data.groupby(['Parent Restaurant name'])['Unique Location ID'].count()
    
    st.dataframe(round(df_gp,2))



def customer_accounts_view(data):
    associate_names = data['Customer Success Associate'].unique()
    selected_associate = st.sidebar.selectbox("Select Associate", associate_names)
    filtered_data_csa = data[(data['Customer Success Associate'] == selected_associate)]

    trends_dic = {
        "Total Orders":orders_col,
        "Average Order Value": avg_val_col,
        "Missed Orders": missed_col,
        "Order Number Change Rate":orders_change_rate,
        "Order Discrepancy": orders_discrepancy_rate,
        "Cancellations": cancellation_col
    }    

    trend_names = list(trends_dic.keys())
    selected_trend_data = st.selectbox("Select Data", trend_names)
    filtered_res_trend = filtered_data_csa[trends_dic[selected_trend_data]]
    
    df_res_trend = filtered_res_trend.T     
    st.line_chart(filtered_res_trend.T, x = natsorted(df_res_trend.index))
    

   # st.subheader("Associate Aggregate Information")

    col1, col2 = st.columns([3, 1])
    
    col1.subheader("Health Scores Chart")
    col1.line_chart(filtered_data_csa['Health_Score'])
    
    col2.subheader("A narrow column with the data")
    col2.write(filtered_data_csa[['Unique Location ID', 'Health_Score']])


    c1, c2 = st.columns([1, 3])

        
    max_loc = filtered_data[filtered_data['Health_Score'] == filtered_data['Health_Score'].max()]['Unique Location ID']
    min_loc = filtered_data[filtered_data['Health_Score'] == filtered_data['Health_Score'].min()]['Unique Location ID']
    
    overall_info = {
        'Mean Health Score': filtered_data['Health_Score'].mean(),
        'Min Health Score': filtered_data['Health_Score'].min(),
        'Max Health Score': filtered_data['Health_Score'].max(),
        'Client With Max Score': max_loc.values[0],
        'Client With Min Score': min_loc.values[0]
        }
    c1.write(overall_info)   
    c2.subheader("A narrow column with the data")
    df_gp = filtered_data.groupby(['Parent Restaurant name'])[num_lis].sum()
    df_gp['Avg Health Score'] = filtered_data.groupby(['Parent Restaurant name'])['Health_Score'].mean()
    df_gp['Number of location'] = filtered_data.groupby(['Parent Restaurant name'])['Unique Location ID'].count()
    
    c2.dataframe(round(df_gp,2))
    
    #fig = px.bar(filtered_data, x='Unique Location ID', y='Health_Score', 
    #             title=f'Health Scores',
    #             labels={'Health Score': 'Health Score (0 to 100)'})
    #st.plotly_chart(fig)

    
    
    
        


def main():


    st.set_page_config(layout="wide")
    st.title('Customer Success Dashboard - Welcome')

            #with col1:
                #st.subheader("Aggregated Performance")
    aggregated_performance_view(data)
            #with col2:
                #customer_accounts_view(data)
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
            
    df_gp = data.groupby(['Customer Success Associate'])[num_lis].sum()
    df_gp[['Avg Retention Score','Avg Health Score']] = data.groupby(['Customer Success Associate'])[['Retention Score','Health_Score']].mean()
    df_gp['Number of location'] = data.groupby(['Customer Success Associate'])['Unique Location ID'].count()
    st.dataframe(round(df_gp, 2))
            

    #filtered_data_as = data[data['Customer Success Associate'].str.strip() == username]

    customer_accounts_view(data)

    # Display additional content here

if __name__ == '__main__':
    main()
