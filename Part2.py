import yaml
import streamlit as st
from yaml.loader import SafeLoader
import streamlit.components.v1 as components
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

credentials = pd.read_csv('user_credentials.csv')
data = pd.read_excel('Data_Score.xlsx').iloc[:,1:]


feat_num = []
feat_obj = []

for iclm in data.columns.to_list():
    try:
        pd.to_numeric(data[iclm])
        feat_num.append(iclm)
    except (ValueError, TypeError):
        feat_obj.append(iclm)
        
data[feat_num] = data[feat_num].astype(float)  


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

    c1, c2 = st.columns([0.7, 0.3])
    
    with c1:
        fig_health_score_distribution = px.histogram(data, x='Health_Score', nbins=10, title='Health Score Distribution')
        fig = go.Figure()
        fig.add_trace(fig_health_score_distribution.data[0])
        
        fig.update_layout(title='Aggregated Performance', barmode='overlay', showlegend=False)
        st.plotly_chart(fig)
    with c2:
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
    st.dataframe(data.describe())



def customer_accounts_view(filtered_data):
   # f_data = filtered_data if selected_item == 'Overall' else filtered_data[filtered_data['Payment Status'] == selected_item]

    st.subheader("Associate Aggregate Information")

    st.dataframe(filtered_data.describe())
    
    fig = px.bar(filtered_data, x='Unique Location ID', y='Health_Score', 
                 title=f'Health Scores',
                 labels={'Health Score': 'Health Score (0 to 100)'})
    st.plotly_chart(fig)
    
    max_loc = filtered_data[filtered_data['Health_Score'] == filtered_data['Health_Score'].max()]['Unique Location ID']
    min_loc = filtered_data[filtered_data['Health_Score'] == filtered_data['Health_Score'].min()]['Unique Location ID']
    
    overall_info = {
        'Mean Health Score': filtered_data['Health_Score'].mean(),
        'Min Health Score': filtered_data['Health_Score'].min(),
        'Max Health Score': filtered_data['Health_Score'].max(),
        'Client With Max Score': max_loc.values[0],
        'Client With Min Score': min_loc.values[0]
        }
    st.write(overall_info)
    st.dataframe(filtered_data[['Unique Location ID', 'Health_Score']])
    
    
        


def main():

    st.set_page_config(layout="wide")
    # Login interface
    state = SessionState(logged_in=False, username=None, role=None)

    if not state.logged_in:
        st.title('Customer Success Dashboard')
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
            selected_associate = st.selectbox("Select Associate", associate_list, key=f"{username}_select_associate")
            filtered_data_adm = data[data['Customer Success Associate'].str.strip() == selected_associate]   

            col1, col2 = st.columns([1,1])
            #with col1:
            st.subheader("Aggregated Performance")
            aggregated_performance_view(data)
               # with col2:
            st.subheader("Associate's Performance")
            customer_accounts_view(filtered_data_adm)

        else:
          #  st.subheader(f"Welcome, {username} (Associate)")
            filtered_data_as = data[data['Customer Success Associate'].str.strip() == username]
            col1, col2 = st.columns([1,1])

            st.subheader("Aggregated Performance")
            aggregated_performance_view(data)
           # with col2:
            st.subheader(f"{username}'s Performance")
            customer_accounts_view(filtered_data_as)


    
                # Display additional content here

if __name__ == '__main__':
    main()
