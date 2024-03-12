# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Part of task 1 - get distinct launch sites:
launch_sites = spacex_df['Launch Site'].unique()
dropdown_options = [{'label': site, 'value': site} for site in launch_sites]
dropdown_options.insert(0, {'label': 'All Sites', 'value': 'ALL'})

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),

                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(
                                    id='site-dropdown',
                                    options=dropdown_options,
                                    value='ALL',
                                    placeholder='Select a Launch Site here',
                                    searchable=True
                                ),

                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                                min=0, 
                                                max=10000, 
                                                step=1000,
                                                marks={
                                                    0: '0',
                                                    2500: '2500',
                                                    5000: '5000',
                                                    7500: '7500'
                                                    },
                                                value=[spacex_df['Payload Mass (kg)'].min(), spacex_df['Payload Mass (kg)'].max()]
                                            ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Aggregate data to get total successful launches for each site
        site_success_counts = spacex_df[spacex_df['class'] == 1].groupby('Launch Site').size().reset_index(name='Success Count')
        # Plot pie chart with distribution of total successes for each site
        fig = px.pie(site_success_counts, names='Launch Site', values='Success Count', title='Total Successful Launches by Site')
        return fig
    else:
        # return the outcomes piechart for a selected site
        # Filter the DataFrame to include only data for the selected site
        filtered_df  = spacex_df[spacex_df['Launch Site'] == entered_site]
        # Count success and failure launches for the selected site
        success_count = filtered_df [filtered_df ['class'] == 1]['class'].count()
        failure_count = filtered_df [filtered_df ['class'] == 0]['class'].count()
        # Render a pie chart for success and failure counts for the selected site
        fig = px.pie(names=['Success', 'Failure'], values=[success_count, failure_count], title=f'Success vs Failure for {entered_site}')
        return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
# Define the callback function for the scatter plot
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter_plot(entered_site, selected_payload_range):
    # Filter the DataFrame based on the selected site
    if entered_site == 'ALL':
        filtered_df = spacex_df
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
    
    # Filter the DataFrame based on the selected payload range
    if selected_payload_range:
        filtered_df = filtered_df[
            (filtered_df['Payload Mass (kg)'] >= selected_payload_range[0]) &
            (filtered_df['Payload Mass (kg)'] <= selected_payload_range[1])
        ]
    
    # Create scatter plot
    fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class', color='Booster Version Category',
                     title='Payload vs Launch Outcome', 
                     labels={'class': 'Launch Outcome', 'Payload Mass (kg)': 'Payload Mass (kg)', 'Booster Version Category': 'Booster Version Category'})
    
    return fig


# Run the app
if __name__ == '__main__':
    app.run_server()