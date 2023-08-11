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


from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)
import pandas as pd
import streamlit as st



def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a UI on top of a dataframe to let viewers filter columns

    Args:
        df (pd.DataFrame): Original dataframe

    Returns:
        pd.DataFrame: Filtered dataframe
    """
    modify = st.checkbox("Add filters")

    if not modify:
        return df

    df = df.copy()

    # Try to convert datetimes into a standard format (datetime, no timezone)
    for col in df.columns:
        if is_object_dtype(df[col]):
            try:
                df[col] = pd.to_datetime(df[col])
            except Exception:
                pass

        if is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.tz_localize(None)

    modification_container = st.container()

    with modification_container:
        to_filter_columns = st.multiselect("Filter dataframe on", df.columns)
        for idx, column in enumerate(to_filter_columns):
            left, right = st.columns((1, 20))
            unique_key = f"{column}_{idx}"
            # Treat columns with < 10 unique values as categorical
            if is_categorical_dtype(df[column]) or df[column].nunique() < 10:
                user_cat_input = right.multiselect(
                    f"Values for {column}",
                    df[column].unique(),
                    default=list(df[column].unique()),
                )
                df = df[df[column].isin(user_cat_input)]
            elif is_numeric_dtype(df[column]):
                _min = float(df[column].min())
                _max = float(df[column].max())
                step = (_max - _min) / 100
                user_num_input = right.slider(
                    f"Values for {column}",
                    min_value=_min,
                    max_value=_max,
                    value=(_min, _max),
                    step=step,
                )
                df = df[df[column].between(*user_num_input)]
            elif is_datetime64_any_dtype(df[column]):
                user_date_input = right.date_input(
                    f"Values for {column}",
                    value=(
                        df[column].min(),
                        df[column].max(),
                    ),
                )
                if len(user_date_input) == 2:
                    user_date_input = tuple(map(pd.to_datetime, user_date_input))
                    start_date, end_date = user_date_input
                    df = df.loc[df[column].between(start_date, end_date)]
            else:
                user_text_input = right.text_input(
                    f"Substring or regex in {column}",
                )
                if user_text_input:
                    df = df[df[column].astype(str).str.contains(user_text_input)]

    return df
    

def authenticate(username, password):
    user = credentials[(credentials['username'] == username) & (credentials['password'] == password)]
    if user.empty:
        return None
    return user.iloc[0]['role']



def aggregated_performance_view(filtered_data, selected_item):
    # f_data = filtered_data if selected_item == 'Overall' else filtered_data[filtered_data['Payment Status'] == selected_item]

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
        'Mean Health Score': filtered_data['Health_Score'].mean(),
        'Min Health Score': filtered_data['Health_Score'].min(),
        'Max Health Score': filtered_data['Health_Score'].max(),
        'Client With Max Score': max_loc.values[0],
        'Client With Min Score': min_loc.values[0]
    }
    st.write(overall_info)
    st.dataframe(filter_dataframe(filtered_data).describe())

def customer_accounts_view(filtered_data, selected_item):
   # f_data = filtered_data if selected_item == 'Overall' else filtered_data[filtered_data['Payment Status'] == selected_item]

    st.subheader("Associate Aggregate Information")

    st.dataframe(filter_dataframe(filtered_data))
    
    fig = px.bar(f_data, x='Unique Location ID', y='Health_Score', 
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
    st.dataframe(filter_dataframe(filtered_data[['Unique Location ID', 'Health_Score']]))
    
    
        


def main():

    st.set_page_config(layout="wide")
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
            selected_item = st.sidebar.selectbox("Filter by Payment Status",
                                            ['Overall'] + list(data['Payment Status'].unique()))

            if username == 'admin':
                st.subheader(f"Welcome, {username}")
                #associate_list = data['Customer Success Associate'].unique().tolist()
                #selected_associate = st.selectbox("Select Associate", associate_list, key=f"{username}_select_associate")
                #filtered_data_adm = data[data['Customer Success Associate'] == selected_associate]   
                filtered_data_adm = data

                col1, col2 = st.columns([1,1])
                with col1:
                    st.subheader("Aggregated Performance")
                    aggregated_performance_view(data,selected_item)
                with col2:
                    st.subheader("Associate's Performance")
                    customer_accounts_view(filtered_data_adm,selected_item)

            else:
                st.subheader(f"Welcome, {username} (Associate)")
                filtered_data_as = data[data['Customer Success Associate'] == username]
                col1, col2 = st.columns([1,1])
                with col1:
                    st.subheader("Aggregated Performance")
                    aggregated_performance_view(data,selected_item)
                with col2:
                    st.subheader(f"{username}'s Performance")
                    customer_accounts_view(filtered_data_as,selected_item)


    
                # Display additional content here

if __name__ == '__main__':
    main()
