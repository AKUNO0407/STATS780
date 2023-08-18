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

from Data_Prep import normalize, data_prep, calculate_health_score

credentials = pd.read_csv('user_credentials.csv')
data_raw = pd.read_excel('Input_Data_File.xlsx').iloc[:,1:]

data = data_prep(data_raw)
data['Health_Score'] = data.apply(calculate_health_score, axis=1)


feat_num = []
feat_obj = []

for iclm in data.columns.to_list():
    try:
        pd.to_numeric(data[iclm])
        feat_num.append(iclm)
    except (ValueError, TypeError):
        feat_obj.append(iclm)
        
data[feat_num] = data[feat_num].astype(float)  
num_lis = ['# Printers', '# Tablets', 'Number of online delivery partners', 'Highest Product_num','Total_orders',
          'Retention Score','Churned','Total_Order_Value','Total_Cancellation','Total_Missed', 'Total_Printed', 'Health_Score']


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
    orders_col = data.columns[data.columns.map(lambda x: x.startswith("Orders Week"))]
    orders_col = sorted(orders_col, key = lambda sub : sub[-1])
    
    heal_perc = data['Health_Score'][data['Health_Score'] >= 80].sum()/len(data['Health_Score'])
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(label="Average Health Score", value=86, 
                delta= round((86-data['Health_Score'].mean())/data['Health_Score'].mean(), 2))
    col2.metric(label="Healthy Customer (>=80) %", value=0.4, delta= round((0.4-heal_perc)/heal_perc, 2))
    col3.metric(label="Avg Weekly Order Number", value=round(data[orders_col[-1]].mean(), 0), 
                delta= round((data[orders_col[-2]].mean() - data[orders_col[-1]].mean()), 0))
    col4.metric(label="Num of Churn", value=1300, delta= 1300 - data['Churned'].sum())
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
    

    cb1, cb2 = st.columns([1, 2])
    with cb1:
        max_loc = data[data['Health_Score'] == data['Health_Score'].max()]['Unique Location ID']
        min_loc = data[data['Health_Score'] == data['Health_Score'].min()]['Unique Location ID']
        
        overall_info = {
            'Mean Health Score': data['Health_Score'].mean(),
            'Min Health Score': data['Health_Score'].min(),
            'Max Health Score': data['Health_Score'].max(),
            'Client With Max Score': max_loc.values[0],
            'Client With Min Score': min_loc.values[0]
        }
        st.write(overall_info)

    with cb2:
        st.dataframe(round(data.describe(),2))

    

    df_gp = data.groupby(['Parent Restaurant name'])[num_lis].sum()
    df_gp['Avg Health Score'] = data.groupby(['Parent Restaurant name'])['Health_Score'].mean()
    df_gp['Number of location'] = data.groupby(['Parent Restaurant name'])['Unique Location ID'].count()
    
    st.dataframe(round(df_gp,2))



def customer_accounts_view(filtered_data):
   # f_data = filtered_data if selected_item == 'Overall' else filtered_data[filtered_data['Payment Status'] == selected_item]

   # st.subheader("Associate Aggregate Information")

    col1, col2 = st.columns([3, 1])
    
    col1.subheader("Health Scores Chart")
    col1.line_chart(filtered_data['Health_Score'])
    
    col2.subheader("A narrow column with the data")
    col2.write(filtered_data[['Unique Location ID', 'Health_Score']])


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
    # Login interface
    state = SessionState(logged_in=False, username=None, role=None)

    if not state.logged_in:
        st.sidebar.title("Login")
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type='password')
        login_button = st.sidebar.button("Login")

        if login_button:
            role = authenticate(username, password)
            if role is None:
                st.sidebar.error("Invalid credentials")
            else:
                state.logged_in = True
                state.username = username
                state.role = role
    if state.logged_in:
        st.title(f'Customer Success Dashboard - Welcome, {state.username} ({state.role.capitalize()})')
        #selected_item = st.sidebar.selectbox("Filter by Payment Status",
        #                                    ['Overall'] + list(data['Payment Status'].unique()))

        if username == 'admin':
           # st.subheader(f"Welcome, {username}")
            associate_list = data['Customer Success Associate'].unique().tolist()
           # selected_associate = st.selectbox("Select Associate", associate_list, key=f"{username}_select_associate")
           # filtered_data_adm = data[data['Customer Success Associate'].str.strip() == selected_associate]   

            
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
            

        else:
          #  st.subheader(f"Welcome, {username} (Associate)")
            filtered_data_as = data[data['Customer Success Associate'].str.strip() == username]
            col1, col2 = st.columns([1,1])

            #st.subheader("Aggregated Performance")
            aggregated_performance_view(data)
           # with col2:
            st.subheader(f"{username}'s Performance")
            customer_accounts_view(filtered_data_as)


    
                # Display additional content here

if __name__ == '__main__':
    main()
