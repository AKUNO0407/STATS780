import yaml
import streamlit as st
from yaml.loader import SafeLoader
import streamlit.components.v1 as components
import pandas as pd

from hasher import Hasher
from authenticate import Authenticate


    # Alternatively you may use st.session_state['name'], st.session_state['authentication_status'], 
    # and st.session_state['username'] to access the name, authentication_status, and username. 

    # if st.session_state['authentication_status']:
    #     authenticator.logout('Logout', 'main')
    #     st.write(f'Welcome *{st.session_state["name"]}*')
    #     st.title('Some content')
    # elif st.session_state['authentication_status'] is False:
    #     st.error('Username/password is incorrect')
    # elif st.session_state['authentication_status'] is None:
    #     st.warning('Please enter your username and password')

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

    _RELEASE = True

if not _RELEASE:
    # hashed_passwords = Hasher(['abc', 'def']).generate()

    # Loading config file
    with open('../config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)

    # Creating the authenticator object
    authenticator = Authenticate(
        config['credentials'],
        config['cookie']['name'], 
        config['cookie']['key'], 
        config['cookie']['expiry_days'],
        config['preauthorized']
    )

    # creating a login widget
    name, authentication_status, username = authenticator.login('Login', 'main')

    
    if authentication_status:
        authenticator.logout('Logout', 'main')
        st.write(f'Welcome *{name}*')
        st.title('Some content')
    elif authentication_status is False:
        st.error('Username/password is incorrect')
    elif authentication_status is None:
        st.warning('Please enter your username and password')

    # Creating a password reset widget
    if authentication_status:
        try:
            if authenticator.reset_password(username, 'Reset password'):
                st.success('Password modified successfully')
        except Exception as e:
            st.error(e)

    # Creating a new user registration widget
    try:
        if authenticator.register_user('Register user', preauthorization=False):
            st.success('User registered successfully')
    except Exception as e:
        st.error(e)

    # Creating a forgot password widget
    try:
        username_forgot_pw, email_forgot_password, random_password = authenticator.forgot_password('Forgot password')
        if username_forgot_pw:
            st.success('New password sent securely')
            # Random password to be transferred to user securely
        else:
            st.error('Username not found')
    except Exception as e:
        st.error(e)

    # Creating a forgot username widget
    try:
        username_forgot_username, email_forgot_username = authenticator.forgot_username('Forgot username')
        if username_forgot_username:
            st.success('Username sent securely')
            # Username to be transferred to user securely
        else:
            st.error('Email not found')
    except Exception as e:
        st.error(e)

    # Creating an update user details widget
    if authentication_status:
        try:
            if authenticator.update_user_details(username, 'Update user details'):
                st.success('Entries updated successfully')
        except Exception as e:
            st.error(e)

    # Saving config file
    with open('../config.yaml', 'w') as file:
        yaml.dump(config, file, default_flow_style=False)

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
