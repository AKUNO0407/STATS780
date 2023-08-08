import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go


data = pd.read_excel('Data_Score.xlsx').iloc[:,1:]

def aggregated_performance_view(data, selected_item):
    filtered_data = data if selected_item == 'Overall' else data[data['Payment Status'] == selected_item]
    fig_health_score_distribution = px.histogram(filtered_data, x='Health_Score', nbins=10, title='Health Score Distribution')

    fig = go.Figure()
    fig.add_trace(fig_health_score_distribution.data[0])
    
    fig.update_layout(title='Aggregated Performance', barmode='overlay', showlegend=False)

    # Show subplots
    st.plotly_chart(fig)

    # Summary Statistics by Associate
    #st.subheader("Overall Summary Statistics")
    #summary_by_associate = data.groupby('Customer Success Associate')['Health Score', 'Average Order Value'].mean()
    #st.dataframe(summary_by_associate)

    # Overall Aggregate Information
    st.subheader("Aggregate Information")
#    overall_info = {
#        'Mean Health Score': data['Health_Score'].mean(),
#        'Min Health Score': data['Health_Score'].min(),
#        'Max Health Score': data['Health_Score'].max(),
#        'Mean Order Value': data['Average Order Value'].mean(),
#        'Min Order Value': data['Average Order Value'].min(),
#        'Max Order Value': data['Average Order Value'].max()
#    }
    st.write(filtered_data.describe())
    

def customer_accounts_view(data, selected_item):
    filtered_data = data if selected_item == 'Overall' else data[data['Payment Status'] == selected_item]
    selected_associate = st.selectbox('Select Customer Success Associate:', filtered_data['Customer Success Associate'].unique())
    associate_data = filtered_data[filtered_data['Customer Success Associate'] == selected_associate]
    st.dataframe(associate_data[['Unique Location ID', 'Health_Score']])
    st.dataframe(associate_data.groupby('Customer Success Associate').mean())
    
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
        

    
 
def main():
    st.title('Customer Success Dashboard')
    selected_item = st.sidebar.selectbox("Filter by Payment Status",
                                            ['Overall'] + list(data['Payment Status'].unique()))

    # Aggregated performance view
   # plot_health_score_distribution()
   # plot_health_score_vs_revenue()

    # Individual health scores for customer success associates
    st.header('Individual Health Scores')
    #plot_individual_health_scores()
    #col1, col2 = st.columns([1, 2])

    #with col1:
    aggregated_performance_view(data, selected_item)

    #with col2:
    customer_accounts_view(data, selected_item)

if __name__ == '__main__':
    main()

   
