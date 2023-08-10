import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

credentials = pd.read_csv('user_credentials.csv')
data = pd.read_excel('Data_Score.xlsx').iloc[:,1:]

def authenticate(username, password):
    user = credentials[(credentials['username'] == username) & (credentials['password'] == password)]
    if user.empty:
        return None
    return user.iloc[0]['role']


feat_num = []
feat_obj = []

for iclm in data.columns.to_list():
    try:
        pd.to_numeric(data[iclm])
        feat_num.append(iclm)
    except (ValueError, TypeError):
        feat_obj.append(iclm)
        
data[feat_num] = data[feat_num].astype(float)  


def aggregated_performance_view(data, selected_item):
    filtered_data = data if selected_item == 'Overall' else data[data['Payment Status'] == selected_item]

    st.subheader("Overall Health Score Information")
    
    fig_health_score_distribution = px.histogram(filtered_data, x='Health_Score', nbins=10, title='Health Score Distribution')

    fig = go.Figure()
    fig.add_trace(fig_health_score_distribution.data[0])
    
    fig.update_layout(title='Aggregated Performance', barmode='overlay', showlegend=False)

    # Show subplots
    st.plotly_chart(fig)

    max_loc = filtered_data[filtered_data['Health_Score'] == filtered_data['Health_Score'].max()]['Unique Location ID']
    min_loc = filtered_data[filtered_data['Health_Score'] == filtered_data['Health_Score'].min()]['Unique Location ID']

    overall_info = {
        'Mean Health Score': data['Health_Score'].mean(),
        'Min Health Score': data['Health_Score'].min(),
        'Max Health Score': data['Health_Score'].max(),
        'Client With Max Score': max_loc.values[0],
        'Client With Min Score': min_loc.values[0]
    }
    st.write(overall_info)
    st.write(filtered_data.describe())
    

def customer_accounts_view(data, selected_item):
    filtered_data = data if selected_item == 'Overall' else data[data['Payment Status'] == selected_item]

    st.subheader("Associate Aggregate Information")


    st.dataframe(associate_data.describe())
    fig = px.bar(associate_data, x='Unique Location ID', y='Health_Score', 
                 title=f'Health Scores for {selected_associate}',
                 labels={'Health Score': 'Health Score (0 to 100)'})
    st.plotly_chart(fig)
    
    max_loc = associate_data[associate_data['Health_Score'] == associate_data['Health_Score'].max()]['Unique Location ID']
    min_loc = associate_data[associate_data['Health_Score'] == associate_data['Health_Score'].min()]['Unique Location ID']
    
    overall_info = {
        'Mean Health Score': associate_data['Health_Score'].mean(),
        'Min Health Score': associate_data['Health_Score'].min(),
        'Max Health Score': associate_data['Health_Score'].max(),
        'Client With Max Score': max_loc.values[0],
        'Client With Min Score': min_loc.values[0]
        }
    st.write(overall_info)
    st.dataframe(associate_data[['Unique Location ID', 'Health_Score']])
    
    
        

    
 
def main():
    st.title('Customer Success Dashboard')

    # Login interface
    st.sidebar.title("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type='password')
    login_button = st.sidebar.button("Login")

    role = None
    if login_button:
        role = authenticate(username, password)
        if role is None:
            st.sidebar.error("Invalid credentials")
    else:
        selected_status = st.sidebar.selectbox("Filter by Payment Status",
                                            ['Overall'] + list(data['Payment Status'].unique()))

        if role == 'associate':
            st.subheader(f"Welcome, {username} (Associate)")
            filtered_data = selected_status[selected_status['Customer Success Associate'] == username]
        # Load and display associate-specific content here
        # Replace this with your charts and tables
        
        elif role == 'admin':
            st.subheader(f"Welcome, {username} (Admin)")
            filtered_data = selected_status
        # Load and display admin-specific content here
        # Replace this with your charts and tables
        
        col1, col2 = st.columns([1, 2])
        aggregated_performance_view(filtered_data, selected_status)
        customer_accounts_view(filtered_data, selected_status)







    #st.header('Individual Health Scores')
    #plot_individual_health_scores()
    #col1, col2 = st.columns([1, 2])

    

    #with col1:
    aggregated_performance_view(data, selected_item)

    #with col2:
    customer_accounts_view(data, selected_item)

if __name__ == '__main__':
    main()

   
