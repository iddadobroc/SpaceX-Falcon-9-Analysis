# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX launch data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a Dash application
app = dash.Dash(__name__)

# Create the app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # TASK 1: Dropdown list to enable Launch Site selection
    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': 'All Sites', 'value': 'ALL'},
            {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
            {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
            {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
            {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
        ],
        value='ALL',
        placeholder="Select a Launch Site here",
        searchable=True
    ),
    html.Br(),
    
    # TASK 2: Pie chart to show the total successful launches count for all sites
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),
    
    html.P("Payload range (Kg):"),
    
    # TASK 3: Slider to select payload range
    dcc.RangeSlider(
        id='payload-slider',
        min=0, max=10000, step=1000,
        value=[min_payload, max_payload]
    ),
    
    # TASK 4: Scatter chart to show the correlation between payload and launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# TASK 2: Callback function for success-pie-chart
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    filtered_df = spacex_df
    if entered_site == 'ALL':
        # Filter only successful launches for all sites
        all_sites_df = spacex_df[spacex_df['class'] == 1]
        fig = px.pie(
            all_sites_df,
            names='Launch Site',
            title='Total Success Launches by Site'
        )
    else:
        # Filter data for the selected launch site
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        
        # Count the number of successes (1) and failures (0)
        success_count = filtered_df['class'].value_counts()
        
        # Create a pie chart with explicit color mapping
        fig = px.pie(
            names=success_count.index,
            values=success_count.values,
            title=f'Total Success and Failure for site {entered_site}',
            color=success_count.index,  # Map colors based on success (1) and failure (0)
            color_discrete_map={0: 'blue', 1: 'red'}  # Assign blue for failure, red for success
        )
    return fig


# TASK 4: Callback function for success-payload-scatter-chart
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [
        Input(component_id='site-dropdown', component_property='value'),
        Input(component_id="payload-slider", component_property="value")
    ]
)
def get_scatter_chart(entered_site, payload_range):
    # Filter the dataframe based on the selected launch site
    filtered_df = spacex_df

    # Filter by payload range
    filtered_df = filtered_df[
        (filtered_df['Payload Mass (kg)'] >= payload_range[0]) & 
        (filtered_df['Payload Mass (kg)'] <= payload_range[1])
    ]
    
    # If a specific launch site is selected, filter by that site
    if entered_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]

    # Create the scatter plot
    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',  # Color points by booster version
        title=f"Payload vs Success for {entered_site} (Payload range: {payload_range[0]} - {payload_range[1]} kg)",
        labels={"class": "Launch Outcome (0 = Failure, 1 = Success)"},
        hover_data=['Booster Version Category', 'Launch Site']  # Additional info on hover
    )
    
    # Return the figure
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server()

