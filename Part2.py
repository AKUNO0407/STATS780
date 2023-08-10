import yaml
import streamlit as st
from yaml.loader import SafeLoader
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

#credentials = pd.read_csv('user_credentials.csv')

authenticator = Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

name, authentication_status, username = authenticator.login('Login', 'main')



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


#def authenticate(username, password):
#    user = credentials[(credentials['username'] == username) & (credentials['password'] == password)]
#    if user.empty:
#        return None
#    return user.iloc[0]['role']



def aggregated_performance_view(filtered_data, selected_item):
    f_data = filtered_data if selected_item == 'Overall' else filtered_data[filtered_data['Payment Status'] == selected_item]

    st.subheader("Overall Health Score Information")
    
    fig_health_score_distribution = px.histogram(f_data, x='Health_Score', nbins=10, title='Health Score Distribution')

    fig = go.Figure()
    fig.add_trace(fig_health_score_distribution.data[0])
    
    fig.update_layout(title='Aggregated Performance', barmode='overlay', showlegend=False)

    # Show subplots
    st.plotly_chart(fig)

    max_loc = f_data[f_data['Health_Score'] == f_data['Health_Score'].max()]['Unique Location ID']
    min_loc = f_data[f_data['Health_Score'] == f_data['Health_Score'].min()]['Unique Location ID']

    overall_info = {
        'Mean Health Score': data['Health_Score'].mean(),
        'Min Health Score': data['Health_Score'].min(),
        'Max Health Score': data['Health_Score'].max(),
        'Client With Max Score': max_loc.values[0],
        'Client With Min Score': min_loc.values[0]
    }
    st.write(overall_info)
    st.write(f_data.describe())
    

def customer_accounts_view(filtered_data, selected_item):
    f_data = filtered_data if selected_item == 'Overall' else filtered_data[filtered_data['Payment Status'] == selected_item]

    st.subheader("Associate Aggregate Information")


    st.dataframe(f_data.describe())
    fig = px.bar(f_data, x='Unique Location ID', y='Health_Score', 
                 title=f'Health Scores',
                 labels={'Health Score': 'Health Score (0 to 100)'})
    st.plotly_chart(fig)
    
    max_loc = f_data[f_data['Health_Score'] == f_data['Health_Score'].max()]['Unique Location ID']
    min_loc = f_data[f_data['Health_Score'] == f_data['Health_Score'].min()]['Unique Location ID']
    
    overall_info = {
        'Mean Health Score': f_data['Health_Score'].mean(),
        'Min Health Score': f_data['Health_Score'].min(),
        'Max Health Score': f_data['Health_Score'].max(),
        'Client With Max Score': max_loc.values[0],
        'Client With Min Score': min_loc.values[0]
        }
    st.write(overall_info)
    st.dataframe(f_data[['Unique Location ID', 'Health_Score']])
    
    
        


def main():


    # Login interface
    #st.sidebar.title("Login")
    #username = st.sidebar.text_input("Username")
    #password = st.sidebar.text_input("Password", type='password')
    #login_button = st.sidebar.button("Login")

    if authentication_status == False:
        st.error('Username/password is incorrect')
    elif authentication_status == None:
        st.warning('Please enter your username and password')
    elif authentication_status:
        authenticator.logout('Logout', 'main')
        st.set_page_config(layout="wide")
        st.title('Customer Success Dashboard')
        st.write(f'Welcome *{name}*')
        #st.title('Some content')

    #if login_button:
    #    role = authenticate(username, password)
    #    if role is None:
    #        st.sidebar.error("Invalid credentials")
    #    else:
    #        st.sidebar.empty()  # Clear the login interface
    #        st.subheader(f"Welcome, {username} ({role.capitalize()})")
    #        selected_item = st.sidebar.selectbox("Filter by Payment Status", ['Overall'] + list(data['Payment Status'].unique()))


        if username == 'admin':
            associate_list = data['Customer Success Associate'].unique().tolist()
            selected_associate = st.selectbox("Select Associate", associate_list)
            filtered_data_adm = data[data['Customer Success Associate'] == selected_associate]   

            col1, col2 = st.columns([2])
            with col1:
                st.subheader("Aggregated Performance")
                aggregated_performance_view(data,selected_item)
            with col2:
                st.subheader(f"{selected_associate}'s Performance")
                customer_accounts_view(filtered_data_adm,selected_item)

        else:
            filtered_data_as = data[data['Customer Success Associate'] == username]
            col1, col2 = st.columns([2])
            with col1:
                st.subheader("Aggregated Performance")
                aggregated_performance_view(data,selected_item)
            with col2:
                st.subheader(f"{username}'s Performance")
                customer_accounts_view(filtered_data_as,selected_item)

            # Display additional content here

if __name__ == '__main__':
    main()
