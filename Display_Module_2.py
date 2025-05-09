import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import os
import sys
import numpy as np

# Get the absolute path to the 'Home' directory
home_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Home'))

# Ensure the 'Home' directory is added to the Python path
sys.path.insert(0, home_path)

# Now import Navbar from navbar
from navbar import Navbar

# Set up file paths and load data
BasePath = os.path.dirname(os.path.abspath(__file__))
PathData = os.path.join(BasePath, 'psd_north_africa.csv')
data = pd.read_csv(PathData)

# Prepare options for the country dropdown
country_options = [{'label': country, 'value': country} for country in data['Country_Name'].unique()]

# Create a mapping of commodity groups to their respective commodities
commodity_groups = {
    'Cereals': {
        '430000': 'Barley',
        '440000': 'Corn',
        '459100': 'Millet',
        '452000': 'Oats',
        '422110': 'Rice, Milled',
        '459200': 'Sorghum',
        '410000': 'Wheat',
        '490000': 'Coarse Grains',
        '400000': 'Cereals'
    },
    'Coarse Grains': {
        '430000': 'Barley',
        '440000': 'Corn',
        '459100': 'Millet',
        '452000': 'Oats',
        '459200': 'Sorghum'
    },
    'Oilseeds': {
        '2223000': 'Oilseed, Cottonseed',
        '2221000': 'Oilseed, Peanut',
        '2226000': 'Oilseed, Rapeseed',
        '2222000': 'Oilseed, Soybean',
        '2224000': 'Oilseed, Sunflowerseed',
        '2200000': 'Oilseeds'
    },
    'Vegetable Oils': {
        '4233000': 'Oil, Cottonseed',
        '4235000': 'Oil, Olive',
        '4243000': 'Oil, Palm',
        '4239100': 'Oil, Rapeseed',
        '4232000': 'Oil, Soybean',
        '4236000': 'Oil, Sunflowerseed',
        '4200000': 'Vegetable Oils'
    },
    'Oilmeals': {
        '813300': 'Meal, Cottonseed',
        '814200': 'Meal, Fish',
        '813200': 'Meal, Peanut',
        '813600': 'Meal, Rapeseed',
        '813100': 'Meal, Soybean',
        '813500': 'Meal, Sunflowerseed',
        '810000': 'Oilmeals'
    },
}

# Prepare options for the commodity group dropdown
commodity_group_options = [{'label': group, 'value': group} for group in commodity_groups.keys()]

# Prepare options for the commodity dropdown including aggregate options
commodity_options = [{'label': desc, 'value': desc} for group in commodity_groups.values() for desc in group.values()]
commodity_options.extend([
    {'label': 'Coarse Grains', 'value': 'Coarse Grains'},
    {'label': 'Cereals', 'value': 'Cereals'},
    {'label': 'Oilseeds', 'value': 'Oilseeds'},
    {'label': 'Vegetable Oils', 'value': 'Vegetable Oils'},
    {'label': 'Oilmeals', 'value': 'Oilmeals'},
])

# Initialize the Dash app
app = dash.Dash(__name__, assets_folder='assets')

external_stylesheets = [
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css',
    '/assets/style.css'  # Use relative path
]

app.layout = html.Div([
    Navbar(),
    html.H1("1. Commodity Balances"),
    html.H3("Data from PS&D (USDA)"),

    html.Div([
        html.Div([
            html.Label("Select Commodity Group:"),
            dcc.Dropdown(
                id='commodity-group-dropdown',
                options=commodity_group_options,
                value='Cereals'  # Default value
            ),
        ], style={'display': 'inline-block', 'width': '20%'}),

        html.Div([
            html.Label("Select Commodity:"),
            dcc.Dropdown(
                id='commodity-dropdown',
                options=commodity_options,
                value='Wheat'  # Default value
            ),
        ], style={'display': 'inline-block', 'width': '30%'}),

        html.Div([
            html.Label("Select Country:"),
            dcc.Dropdown(
                id='country-dropdown',
                options=country_options,
                value='Morocco'  # Default value
            ),
        ], style={'display': 'inline-block', 'width': '25%'}),

        html.Div([
            html.Label("Select Market Year:"),
            dcc.Dropdown(
                id='year-dropdown'
            ),
        ], style={'display': 'inline-block', 'width': '15%'})
    ], style={'display': 'flex', 'justifyContent': 'space-between', 'padding': '0 10px'}),
    
    dcc.Graph(id='balance-graph'),

    html.Button("Hide/Show Table", id='toggle-table-button', n_clicks=0, style={'backgroundColor': 'lightblue', 'height': '30px', 'width': '150px'}),
    html.Button("Export CSV", id='export-csv-button', n_clicks=0, style={'backgroundColor': 'darkblue', 'color': 'white', 'height': '30px', 'width': '150px'}),
    html.Div(id='table-container', style={'display': 'none'}),

    dcc.Download(id="download-dataframe-csv"),

    # Add horizontal line and 20px vertical space
    html.Hr(),  # Horizontal line
    html.Div(style={'height': '20px'}),  # 20px vertical space

    html.H1("2. Key Performance Indicators"),

    # Add KPI container
    html.Div(id='kpi-container', style={'display': 'flex', 'flexWrap': 'wrap'}),

    # Add horizontal line and 20px vertical space
    html.Hr(),  # Horizontal line
    html.Div(style={'height': '20px'}),  # 20px vertical space

    html.H1("3. Time Series Analysis"),
    html.Div([
        html.Div([
            html.Label("Select Series for the left Y-axis:"),
            dcc.Checklist(
                id='attribute-checklist-primary',
                options=[
                    {'label': 'Production', 'value': 'Production'},
                    {'label': 'Yield', 'value': 'Yield'},
                    {'label': 'Area Harvested', 'value': 'Area Harvested'},
                    {'label': 'Beginning Stocks', 'value': 'Beginning Stocks'},
                    {'label': 'Imports', 'value': 'Imports'},
                    {'label': 'Total Supply', 'value': 'Total Supply'},
                    {'label': 'Ending Stocks', 'value': 'Ending Stocks'},
                    {'label': 'Feed', 'value': 'Feed Dom. Consumption'},
                    {'label': 'Exports', 'value': 'Exports'},
                    {'label': 'Domestic Consumption', 'value': 'Domestic Consumption'},
                    {'label': 'FSI Consumption', 'value': 'FSI Consumption'},
                ],
                value=['Production'],  # Default values
                labelStyle={'display': 'block'}
            )
        ], style={'flex': '1'}),

        html.Div([
            dcc.Graph(id='line-chart')
        ], style={'flex': '3'}),  # Assign more space to the chart

        html.Div([
            html.Label("Select Series for the right Y-axis:"),
            dcc.Checklist(
                id='attribute-checklist-secondary',
                options=[
                    {'label': 'Production', 'value': 'Production'},
                    {'label': 'Yield', 'value': 'Yield'},
                    {'label': 'Area Harvested', 'value': 'Area Harvested'},
                    {'label': 'Beginning Stocks', 'value': 'Beginning Stocks'},
                    {'label': 'Imports', 'value': 'Imports'},
                    {'label': 'Total Supply', 'value': 'Total Supply'},
                    {'label': 'Feed', 'value': 'Feed Dom. Consumption'},
                    {'label': 'Ending Stocks', 'value': 'Ending Stocks'},
                    {'label': 'Exports', 'value': 'Exports'},
                    {'label': 'Domestic Consumption', 'value': 'Domestic Consumption'},
                    {'label': 'FSI Consumption', 'value': 'FSI Consumption'},
                ],
                value=[],  # Default values
                labelStyle={'display': 'block'}
            )
        ], style={'flex': '1'}),
    ], style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'flex-start', 'padding': '20px 0'}),

    html.Div([
        html.Label("Select Trend Line Order:"),
        dcc.RadioItems(
            id='trendline-order',
            options=[
                {'label': 'None', 'value': 0},
                {'label': 'First Order', 'value': 1},
                {'label': 'Second Order', 'value': 2},
                {'label': 'Third Order', 'value': 3}
            ],
            value=0,  # Default value
            labelStyle={'display': 'inline-block', 'margin-right': '10px'}
        ),
    ], style={'textAlign': 'center', 'padding': '20px 0'})  # Centered and padded
])


# Update the commodity dropdown based on selected commodity group
@app.callback(
    [Output('commodity-dropdown', 'options'),
     Output('commodity-dropdown', 'value')],
    Input('commodity-group-dropdown', 'value')
)
def set_commodity_options(selected_group):
    if selected_group is None:
        return commodity_options, 'Wheat'
    
    options = [{'label': desc, 'value': desc} for code, desc in commodity_groups[selected_group].items()]
    
    default_values = {
        'Cereals': 'Wheat',
        'Coarse Grains': 'Barley',
        'Oilseeds': 'Oilseed, Soybean',
        'Vegetable Oils': 'Oil, Olive',
        'Oilmeals': 'Meal, Soybean'
    }
    
    default_value = default_values.get(selected_group, options[0]['value'] if options else 'Wheat')
    
    return options, default_value


# Update the year dropdown based on selected commodity and country
@app.callback(
    Output('year-dropdown', 'options'),
    [Input('commodity-dropdown', 'value'),
     Input('country-dropdown', 'value')]
)
def set_year_options(selected_commodity, selected_country):
    filtered_data = data[(data['Commodity_Description'] == selected_commodity) & (data['Country_Name'] == selected_country)]
    years = filtered_data['Market_Year'].unique()
    return [{'label': year, 'value': year} for year in years]

# Update the year dropdown value based on available options (default to the latest year)
@app.callback(
    Output('year-dropdown', 'value'),
    [Input('year-dropdown', 'options')]
)
def set_year_value(available_options):
    return max(option['value'] for option in available_options) if available_options else None

# Define callback to update graph based on selected commodity, country, and year
@app.callback(
    [Output('balance-graph', 'figure'),
     Output('kpi-container', 'children')],
    [Input('commodity-dropdown', 'value'),
     Input('country-dropdown', 'value'),
     Input('year-dropdown', 'value')]
)
def update_graph(selected_commodity, selected_country, selected_year):
    # Filter data based on selections
    filtered_data = data[(data['Commodity_Description'] == selected_commodity) & 
                         (data['Country_Name'] == selected_country) &
                         (data['Market_Year'] == selected_year)]
    
    if filtered_data.empty:
        return {
            'data': [],
            'layout': {
                'title': 'No data available for the selected combination.'
            }
        }, []

    # Replace 'Feed Dom. Consumption' with 'Feed'
    filtered_data.loc[filtered_data['Attribute_Description'] == 'Feed Dom. Consumption', 'Attribute_Description'] = 'Feed'
    
    # Recalculate 'Domestic Consumption' without 'Feed'
    if 'Domestic Consumption' in filtered_data['Attribute_Description'].values and 'Feed' in filtered_data['Attribute_Description'].values:
        total_domestic_consumption = filtered_data[filtered_data['Attribute_Description'] == 'Domestic Consumption']['Value'].values[0]
        feed_consumption = filtered_data[filtered_data['Attribute_Description'] == 'Feed']['Value'].values[0]
        recalculated_domestic_consumption = total_domestic_consumption - feed_consumption
        filtered_data.loc[filtered_data['Attribute_Description'] == 'Domestic Consumption', 'Value'] = recalculated_domestic_consumption

    # Rename 'Domestic Consumption' to 'Food, Seed, Ind. Use'
    filtered_data.loc[filtered_data['Attribute_Description'] == 'Domestic Consumption', 'Attribute_Description'] = 'Food, Seed, Ind. Use'
    
    # Drop 'Area Harvested', 'Yield', and any remaining 'Food, Seed, Ind. Use' before renaming
    filtered_data = filtered_data[(filtered_data['Attribute_Description'] != 'Area Harvested') & 
                                  (filtered_data['Attribute_Description'] != 'Yield')]

    # Pivot the data to transpose the matrix so that Attribute_Descriptions are columns
    pivoted_data = filtered_data.pivot_table(
        index=['Market_Year'],
        columns='Attribute_Description',
        values='Value'
    ).reset_index()

    # Explicitly set positive and negative attributes
    attributes_order = ['Rough Production', 'Production', 'Imports', 'Beginning Stocks', 
                        '<->', 'Exports', 'Ending Stocks', 'Feed', 'Food, Seed, Ind. Use']  # Use 'Food, Seed, Ind. Use' here
    positive_attributes = ['Rough Production', 'Production', 'Imports', 'Beginning Stocks']
    negative_attributes = ['Exports', 'Ending Stocks', 'Feed', 'Food, Seed, Ind. Use']

    # Filter attributes to ensure they exist in the DataFrame
    positive_attributes = [attr for attr in positive_attributes if attr in pivoted_data.columns]
    negative_attributes = [attr for attr in negative_attributes if attr in pivoted_data.columns]

    # Define unique colors for each attribute
    colors = {
        'Rough Production': 'yellow',
        'Production': 'blue',
        'Beginning Stocks': 'green',
        'Imports': 'orange',
        'Ending Stocks': 'red',
        'Exports': 'maroon',
        'Feed': 'salmon',
        'Food, Seed, Ind. Use': 'lightgreen',  # Use 'Food, Seed, Ind. Use' here
    }

    # Calculate the positions for the annotations
    max_positive_value = max([pivoted_data[attr].values[0] for attr in positive_attributes], default=0)
    min_negative_value = min([pivoted_data[attr].values[0] for attr in negative_attributes], default=0)

    # Create the figure
    fig = {
        'data': [],
        'layout': {
            'title': {
                'text': f'Supply/Utilization Balance for {selected_commodity}, {selected_country}, {selected_year}',
                'font': {'size': 28}
            },
            'xaxis': {
                'title': '',
                'tickfont': {'size': 16},  # Increase font size of x-axis tick marks to 20px
                'tickangle': 0,  # Ensure the labels are horizontal
                'categoryorder': 'array',
                'categoryarray': attributes_order,  # Set the order of the attributes
            },
            'yaxis': {
                'title': '1000 MT',
                'tickfont': {'size': 16}  # Increase font size of y-axis tick marks
            },
            'barmode': 'group',
            'annotations': [
                {
                    'x': 0.30,
                    'y': max_positive_value * 1 if positive_attributes else 0,
                    'xref': 'paper',
                    'yref': 'y',
                    'text': 'Supply',
                    'showarrow': False,
                    'font': {'size': 20, 'color': 'black'},
                    'align': 'center'
                },
                {
                    'x': 0.56,
                    'y': max_positive_value * -1 if negative_attributes else 0,  # Adjust distance of 'Utilization'
                    'xref': 'paper',
                    'yref': 'y',
                    'text': 'Utilization',
                    'showarrow': False,
                    'font': {'size': 20, 'color': 'black'},
                    'align': 'center'
                }
            ]
        }
    }

    # Add bars for each attribute in the specified order
    for attr in attributes_order:
        if attr == '<->':
            fig['data'].append({
                'x': [' '],  # Placeholder for the space before 'Exports'
                'y': [0],
                'type': 'bar',
                'name': '',
                'marker': {'color': 'white'},
                'showlegend': False,
                'hoverinfo': 'none'
            })
        elif attr in positive_attributes:
            value = pivoted_data[attr].values[0]
            fig['data'].append({
                'x': [attr],
                'y': [value],
                'type': 'bar',
                'name': attr,
                'text': [round(value, 0)],
                'textposition': 'auto',
                'textfont': {'size': 18},  # Increase font size of numbers on bars to 20px
                'marker': {'color': colors.get(attr, 'gray')},
            })
        elif attr in negative_attributes:
            value = pivoted_data[attr].values[0]
            fig['data'].append({
                'x': [attr],
                'y': [-value],
                'type': 'bar',
                'name': attr,
                'text': [-round(value, 0)],
                'textposition': 'auto',
                'textfont': {'size': 18},  # Increase font size of numbers on bars to 20px
                'marker': {'color': colors.get(attr, 'gray')},
            })

    # Calculate KPIs
    production = filtered_data[filtered_data['Attribute_Description'] == 'Production']['Value'].sum()
    imports = filtered_data[filtered_data['Attribute_Description'] == 'Imports']['Value'].sum()
    beginning_stocks = filtered_data[filtered_data['Attribute_Description'] == 'Beginning Stocks']['Value'].sum()
    ending_stocks = filtered_data[filtered_data['Attribute_Description'] == 'Ending Stocks']['Value'].sum()
    total_supply = production + imports + beginning_stocks - ending_stocks

    self_sufficiency_ratio = production / total_supply if total_supply != 0 else 0
    import_dependency_ratio = imports / total_supply if total_supply != 0 else 0
    stocks_to_use_ratio = beginning_stocks / total_supply if total_supply != 0 else 0
    
    # Calculate Coefficient of Variation (CV) on first differences of yield
    def calculate_cv_first_diff(data, start_year, end_year):
        period_data = data[(data['Market_Year'] >= start_year) & (data['Market_Year'] <= end_year)]
        if not period_data.empty:
            first_diff = period_data['Value'].diff().dropna()
            return (first_diff.std() / first_diff.mean() / 100) if first_diff.mean() != 0 else None
        return None

    # Calculate CAGR for yield growth rates
    def calculate_cagr(start_value, end_value, periods):
        if start_value > 0 and end_value > 0:
            return (end_value / start_value) ** (1 / periods) - 1
        return 0

    yield_data = data[(data['Commodity_Description'] == selected_commodity) &
                      (data['Country_Name'] == selected_country) &
                      (data['Attribute_Description'] == 'Yield')]

    yield_cv_1 = calculate_cv_first_diff(yield_data, 1960, 1990)
    yield_cv_2 = calculate_cv_first_diff(yield_data, 1980, 2010)
    yield_cv_3 = calculate_cv_first_diff(yield_data, 2000, 2024)

    early_yield = yield_data[(yield_data['Market_Year'] >= 1980) & (yield_data['Market_Year'] <= 1984)]['Value'].mean()
    late_yield = yield_data[(yield_data['Market_Year'] >= 2020) & (yield_data['Market_Year'] <= 2024)]['Value'].mean()
    mid_yield = yield_data[(yield_data['Market_Year'] >= 2000) & (yield_data['Market_Year'] <= 2004)]['Value'].mean()

    cagr_early_to_late = calculate_cagr(early_yield, late_yield, 40)
    cagr_mid_to_late = calculate_cagr(mid_yield, late_yield, 20)

    # Filter data based on selections
    filtered_data = data[(data['Commodity_Description'] == selected_commodity) & 
                         (data['Country_Name'] == selected_country) &
                         (data['Market_Year'] == selected_year)]

    # Calculate Yield Ratio to North Africa for the selected year
    north_africa_yield_data = data[(data['Commodity_Description'] == selected_commodity) &
                                   (data['Country_Name'] == 'North Africa') &
                                   (data['Market_Year'] == selected_year) &
                                   (data['Attribute_Description'] == 'Yield')]

    north_africa_yield = north_africa_yield_data['Value'].mean()

    current_year_yield = filtered_data[(filtered_data['Attribute_Description'] == 'Yield')]['Value'].mean()

    yield_ratio = (current_year_yield / north_africa_yield * 100) if north_africa_yield != 0 else None

    # Calculate Per Capita KPIs
    population = filtered_data['Population'].values[0] if not filtered_data.empty else 0

    per_capita_production = (production / population) * 1000 if population != 0 else 0
    per_capita_imports = (imports / population) * 1000 if population != 0 else 0
    per_capita_supply = (total_supply / population) * 1000 if population != 0 else 0

    # Replace 'FSI Consumption' with 'Food, Seed, Ind. Use'
    filtered_data.loc[filtered_data['Attribute_Description'] == 'FSI Consumption', 'Attribute_Description'] = 'Food, Seed, Ind. Use'

    # Calculate Per Capita Food, Seed, Ind. Use
    food_seed_ind_use = filtered_data[filtered_data['Attribute_Description'] == 'Food, Seed, Ind. Use']['Value'].sum()

    # Calculate population value
    population = filtered_data['Population'].values[0] if not filtered_data.empty else 0

    # Calculate Per Capita Food, Seed, Ind. Use
    per_capita_food_seed_ind_use = (food_seed_ind_use / population) * 1000 if population != 0 else 0

    kpi_tiles = [
        html.Div([
            html.H1(f"Self-sufficiency Ratio ({selected_country}, {selected_commodity}, {selected_year})", style={'textAlign': 'center'}),
            html.P(f"{self_sufficiency_ratio:.1%}", style={'fontSize': '50px', 'textAlign': 'center', 'fontWeight': 'bold', 'color':'orange'})
        ], style={'padding': '20px', 'margin': '10px', 'border': '1px solid #ccc', 'borderRadius': '5px', 'width': '28%', 'backgroundColor': '#f2f2f2'}),
        html.Div([
            html.H1(f"Import Dependency Ratio ({selected_country}, {selected_commodity}, {selected_year})", style={'textAlign': 'center'}),
            html.P(f"{import_dependency_ratio:.1%}", style={'fontSize': '50px', 'textAlign': 'center', 'fontWeight': 'bold', 'color':'orange'})
        ], style={'padding': '20px', 'margin': '10px', 'border': '1px solid #ccc', 'borderRadius': '5px', 'width': '28%', 'backgroundColor': '#f2f2f2'}),
        html.Div([
            html.H1(f"CAGR Yield Growth (1980/84 - 2020/24) ({selected_country}, {selected_commodity})", style={'textAlign': 'center'}),
            html.P(f"{cagr_early_to_late:.2%}", style={'fontSize': '50px', 'textAlign': 'center', 'fontWeight': 'bold', 'color':'blue'})
        ], style={'padding': '20px', 'margin': '10px', 'border': '1px solid #ccc', 'borderRadius': '5px', 'width': '28%', 'backgroundColor': '#e6f7ff'}),
        html.Div([
            html.H1(f"CAGR Yield Growth (2000/04 - 2020/24) ({selected_country}, {selected_commodity})", style={'textAlign': 'center'}),
            html.P(f"{cagr_mid_to_late:.2%}", style={'fontSize': '50px', 'textAlign': 'center', 'fontWeight': 'bold', 'color':'blue'})
        ], style={'padding': '20px', 'margin': '10px', 'border': '1px solid #ccc', 'borderRadius': '5px', 'width': '28%', 'backgroundColor': '#e6f7ff'}),
        html.Div([
            html.H1(f"Yield Variability (Coefficient of Variation, first difference) 1960-1990", style={'textAlign': 'center'}),
            html.P(f"{yield_cv_1:.1%}" if yield_cv_1 is not None else "N/A", style={'fontSize': '50px', 'textAlign': 'center', 'fontWeight': 'bold', 'color':'purple'})
        ], style={'padding': '20px', 'margin': '10px', 'border': '1px solid #ccc', 'borderRadius': '5px', 'width': '28%', 'backgroundColor': '#e6f7ff'}),
        html.Div([
            html.H1(f"Yield Variability (Coefficient of Variation, first difference) 1980-2010", style={'textAlign': 'center'}),
            html.P(f"{yield_cv_2:.1%}" if yield_cv_2 is not None else "N/A", style={'fontSize': '50px', 'textAlign': 'center', 'fontWeight': 'bold', 'color':'purple'})
        ], style={'padding': '20px', 'margin': '10px', 'border': '1px solid #ccc', 'borderRadius': '5px', 'width': '28%', 'backgroundColor': '#e6f7ff'}),
        html.Div([
            html.H1(f"Yield Variability (Coefficient of Variation, first difference) 2000-2024", style={'textAlign': 'center'}),
            html.P(f"{yield_cv_3:.1%}" if yield_cv_3 is not None else "N/A", style={'fontSize': '50px', 'textAlign': 'center', 'fontWeight': 'bold', 'color':'purple'})
        ], style={'padding': '20px', 'margin': '10px', 'border': '1px solid #ccc', 'borderRadius': '5px', 'width': '28%', 'backgroundColor': '#e6f7ff'}),
        html.Div([
            html.H1(f"Per Capita Production (kg/person/year) ({selected_country}, {selected_commodity}, {selected_year})", style={'textAlign': 'center'}),
            html.P(f"{per_capita_production:.1f}", style={'fontSize': '50px', 'textAlign': 'center', 'fontWeight': 'bold', 'color':'green'})
        ], style={'padding': '20px', 'margin': '10px', 'border': '1px solid #ccc', 'borderRadius': '5px', 'width': '28%', 'backgroundColor': '#ffffcc'}),
        html.Div([
            html.H1(f"Per Capita Imports (kg/person/year) ({selected_country}, {selected_commodity}, {selected_year})", style={'textAlign': 'center'}),
            html.P(f"{per_capita_imports:.1f}", style={'fontSize': '50px', 'textAlign': 'center','fontWeight': 'bold', 'color':'green'})
        ], style={'padding': '20px', 'margin': '10px', 'border': '1px solid #ccc', 'borderRadius': '5px', 'width': '28%', 'backgroundColor': '#ffffcc'}),
        html.Div([
            html.H1(f"Per Capita Supply (kg/person/year) ({selected_country}, {selected_commodity}, {selected_year})", style={'textAlign': 'center'}),
            html.P(f"{per_capita_supply:.1f}", style={'fontSize': '50px', 'textAlign': 'center','fontWeight': 'bold', 'color':'green'})
        ], style={'padding': '20px', 'margin': '10px', 'border': '1px solid #ccc', 'borderRadius': '5px', 'width': '28%', 'backgroundColor': '#ffffcc'}),
        html.Div([
            html.H1(f"Per Capita Food, Seed, Ind. Use (kg/person/year) ({selected_country}, {selected_commodity}, {selected_year})", style={'textAlign': 'center'}),
            html.P(f"{per_capita_food_seed_ind_use:.1f}", style={'fontSize': '50px', 'textAlign': 'center', 'fontWeight': 'bold', 'color':'green'})
        ], style={'padding': '20px', 'margin': '10px', 'border': '1px solid #ccc', 'borderRadius': '5px', 'width': '28%', 'backgroundColor': '#ffffcc'}),
        html.Div([
            html.H1(f"Yield level relative to North Africa (%) ({selected_country}, {selected_commodity}, {selected_year})", style={'textAlign': 'center'}),
            html.P(f"{yield_ratio:.1f}%" if yield_ratio is not None else "N/A", style={'fontSize': '50px', 'textAlign': 'center', 'fontWeight': 'bold', 'color':'black'})
        ], style={'padding': '20px', 'margin': '10px', 'border': '1px solid #ccc', 'borderRadius': '5px', 'width': '28%', 'backgroundColor': '#cccccc'}),
    ]

    return fig, kpi_tiles

# Update line chart with trend lines
@app.callback(
    Output('line-chart', 'figure'),
    [Input('commodity-dropdown', 'value'),
     Input('country-dropdown', 'value'),
     Input('attribute-checklist-primary', 'value'),
     Input('attribute-checklist-secondary', 'value'),
     Input('trendline-order', 'value')]
)
def update_line_chart(selected_commodity, selected_country, primary_attributes, secondary_attributes, trendline_order):
    # Define unique colors for each attribute
    colors = {
        'Production': 'blue',
        'Beginning Stocks': 'green',
        'Imports': 'orange',
        'Total Supply': 'cyan',
        'Area Harvested': 'darkgreen',
        'Ending Stocks': 'red',
        'Exports': 'maroon',
        'Feed': 'salmon',
        'Industrial Dom. Consumption': 'firebrick',
        'Yield': 'brown',
        'Population': 'gold'
    }

    # Filter data based on selections
    filtered_data = data[(data['Commodity_Description'] == selected_commodity) & 
                         (data['Country_Name'] == selected_country)]
    
    # Drop 'Food, Seed, Ind. Use'
    filtered_data = filtered_data[filtered_data['Attribute_Description'] != 'Food, Seed, Ind. Use']

    # Make 'Imports from the US' positive
    filtered_data.loc[filtered_data['Attribute_Description'] == 'TY Imp. from U.S.', 'Value'] = abs(filtered_data['Value'])
    
    # Pivot the data to transpose the matrix so that Attribute_Descriptions are columns
    pivoted_data = filtered_data.pivot_table(
        index=['Market_Year'],
        columns='Attribute_Description',
        values='Value'
    ).reset_index()

    # Create the title string
    primary_attributes_str = ", ".join(primary_attributes)
    secondary_attributes_str = ", ".join(secondary_attributes)
    title_text = f'Long-term Trend in {selected_commodity} {primary_attributes_str}, {secondary_attributes_str} {selected_country}'

    # Determine y-axis titles
    def determine_yaxis_title(attributes):
        if 'Yield' in attributes:
            return 'MT/ha'
        elif 'Area Harvested' in attributes:
            return '1000 ha'
        else:
            return '1000 MT'

    yaxis_title = determine_yaxis_title(primary_attributes)
    yaxis2_title = determine_yaxis_title(secondary_attributes)

    # Create the figure
    fig = {
        'data': [],
        'layout': {
            'title': {
                'text': title_text,
                'font': {'family': 'Times New Roman', 'size': 20, 'color': 'black', 'weight': 'bold'},
                'x': 0,  # left aligned
                'xanchor': 'left'  # left aligned
            },
            'xaxis': {
                'title': '',
                'tickfont': {'size': 14}  # Increase font size of x-axis tick marks
            },
            'yaxis': {
                'title': yaxis_title,
                'tickfont': {'size': 14},  # Increase font size of y-axis tick marks
                'showgrid': False
            },
            'yaxis2': {
                'title': yaxis2_title,
                'tickfont': {'size': 14},  # Increase font size of y-axis tick marks
                'overlaying': 'y',
                'side': 'right',
                'showgrid': False
            },
            'legend': {
                'x': 0,
                'y': 1,
                'xanchor': 'left',
                'yanchor': 'top'
            }
        }
    }

    # Add lines for each primary attribute
    for primary_attribute in primary_attributes:
        if primary_attribute in pivoted_data.columns:
            fig['data'].append({
                'x': pivoted_data['Market_Year'],
                'y': pivoted_data[primary_attribute],
                'type': 'line',
                'name': primary_attribute,
                'marker': {'color': colors.get(primary_attribute, 'gray')},
                'yaxis': 'y1'
            })
            # Add trend line for primary attribute if trendline_order is not None
            if trendline_order > 0:
                z = np.polyfit(pivoted_data['Market_Year'], pivoted_data[primary_attribute], trendline_order)
                p = np.poly1d(z)
                trendline = p(pivoted_data['Market_Year'])
                equation = f'{z[0]:.2f}x'
                for i, coef in enumerate(z[1:], start=1):
                    equation += f' + {coef:.2f}x^{i}'
                fig['data'].append({
                    'x': pivoted_data['Market_Year'],
                    'y': trendline,
                    'type': 'line',
                    'name': equation,
                    'line': {'dash': 'dash', 'color': colors.get(primary_attribute, 'gray')}
                })
        elif primary_attribute == 'Population':
            country_population = data[(data['Country_Name'] == selected_country) & 
                                      (data['Attribute_Description'] == 'Total Population')]
            fig['data'].append({
                'x': country_population['Market_Year'],
                'y': country_population['Value'],
                'type': 'line',
                'name': 'Population',
                'marker': {'color': colors.get('Population', 'gold')},
                'yaxis': 'y1'
            })

    # Add lines for each secondary attribute
    for secondary_attribute in secondary_attributes:
        if secondary_attribute in pivoted_data.columns:
            fig['data'].append({
                'x': pivoted_data['Market_Year'],
                'y': pivoted_data[secondary_attribute],
                'type': 'line',
                'name': secondary_attribute,
                'marker': {'color': colors.get(secondary_attribute, 'gray')},
                'yaxis': 'y2'
            })
            # Add trend line for secondary attribute if trendline_order is not None
            if trendline_order > 0:
                z = np.polyfit(pivoted_data['Market_Year'], pivoted_data[secondary_attribute], trendline_order)
                p = np.poly1d(z)
                trendline = p(pivoted_data['Market_Year'])
                equation = f'{z[0]:.2f}x'
                for i, coef in enumerate(z[1:], start=1):
                    equation += f' + {coef:.2f}x^{i}'
                fig['data'].append({
                    'x': pivoted_data['Market_Year'],
                    'y': trendline,
                    'type': 'line',
                    'name': equation,
                    'line': {'dash': 'dash', 'color': colors.get(secondary_attribute, 'gray')}
                })
        elif secondary_attribute == 'Population':
            country_population = data[(data['Country_Name'] == selected_country) & 
                                      (data['Attribute_Description'] == 'Total Population')]
            fig['data'].append({
                'x': country_population['Market_Year'],
                'y': country_population['Value'],
                'type': 'line',
                'name': 'Population',
                'marker': {'color': colors.get('Population', 'gold')},
                'yaxis': 'y2'
            })
    
    return fig


# Toggle table visibility
@app.callback(
    Output('table-container', 'style'),
    [Input('toggle-table-button', 'n_clicks')],
    [State('table-container', 'style')]
)
def toggle_table_visibility(n_clicks, current_style):
    if n_clicks is None:
        n_clicks = 0
    if n_clicks % 2 == 1:
        return {'display': 'block'}
    else:
        return {'display': 'none'}

# Export CSV
@app.callback(
    Output('download-dataframe-csv', 'data'),
    [Input('export-csv-button', 'n_clicks')],
    [State('commodity-dropdown', 'value'),
     State('country-dropdown', 'value'),
     State('year-dropdown', 'value')],
    prevent_initial_call=True
)
def generate_csv(n_clicks, selected_commodity, selected_country, selected_year):
    # Filter data based on selections
    filtered_data = data[(data['Commodity_Description'] == selected_commodity) & 
                         (data['Country_Name'] == selected_country) &
                         (data['Market_Year'] == selected_year)]
    
    if filtered_data.empty:
        return ''
    
    return dcc.send_data_frame(filtered_data.to_csv, f"{selected_commodity}_{selected_country}_{selected_year}.csv")

# Display table
@app.callback(
    Output('table-container', 'children'),
    [Input('commodity-dropdown', 'value'),
     Input('country-dropdown', 'value'),
     Input('year-dropdown', 'value')]
)
def update_table(selected_commodity, selected_country, selected_year):
    filtered_data = data[(data['Commodity_Description'] == selected_commodity) & 
                         (data['Country_Name'] == selected_country) &
                         (data['Market_Year'] == selected_year)]
    
    if filtered_data.empty:
        return html.Div('No data available for the selected combination.')
    
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in filtered_data.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(filtered_data.iloc[i][col]) for col in filtered_data.columns
            ]) for i in range(len(filtered_data))
        ])
    ])

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
