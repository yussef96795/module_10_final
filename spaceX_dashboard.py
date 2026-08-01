# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# ── Load Data ──────────────────────────────────────────────────────────────────
URL = ("https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/"
       "IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv")

try:
    spacex_df = pd.read_csv(URL)
except Exception:
    # Fallback mirror if IBM server is blocked
    FALLBACK = ("https://raw.githubusercontent.com/dalalalhabad/"
                "IBM-Applied-Data-Science-Capstone/main/spacex_launch_dash.csv")
    spacex_df = pd.read_csv(FALLBACK)

max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# ── App Layout ─────────────────────────────────────────────────────────────────
app = dash.Dash(__name__)

app.layout = html.Div(children=[

    html.H1(
        'SpaceX Launch Records Dashboard',
        style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}
    ),

    # ── TASK 1: Dropdown ────────────────────────────────────────────────────────
    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': 'All Sites', 'value': 'ALL'},
            {'label': 'CCAFS LC-40',  'value': 'CCAFS LC-40'},
            {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
            {'label': 'KSC LC-39A',   'value': 'KSC LC-39A'},
            {'label': 'VAFB SLC-4E',  'value': 'VAFB SLC-4E'},
        ],
        value='ALL',
        placeholder='Select a Launch Site here',
        searchable=True
    ),

    html.Br(),

    # ── TASK 2: Pie chart ───────────────────────────────────────────────────────
    html.Div(dcc.Graph(id='success-pie-chart')),

    html.Br(),

    html.P("Payload range (Kg):"),

    # ── TASK 3: Range Slider ────────────────────────────────────────────────────
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        marks={i: str(i) for i in range(0, 10001, 1000)},
        value=[min_payload, max_payload]
    ),

    html.Br(),

    # ── TASK 4: Scatter chart ───────────────────────────────────────────────────
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])


# ── TASK 2: Callback — Pie chart ───────────────────────────────────────────────
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown',      component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        fig = px.pie(
            spacex_df,
            values='class',
            names='Launch Site',
            title='Total Successful Launches by Site'
        )
    else:
        filtered = spacex_df[spacex_df['Launch Site'] == entered_site]
        fig = px.pie(
            filtered,
            names='class',
            title=f'Total Success Launches for site {entered_site}'
        )
    return fig


# ── TASK 4: Callback — Scatter chart ──────────────────────────────────────────
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown',   component_property='value'),
     Input(component_id='payload-slider',  component_property='value')]
)
def get_scatter_chart(entered_site, payload_range):
    low, high = payload_range
    mask = (
        (spacex_df['Payload Mass (kg)'] >= low) &
        (spacex_df['Payload Mass (kg)'] <= high)
    )
    filtered = spacex_df[mask]

    if entered_site == 'ALL':
        fig = px.scatter(
            filtered,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title='Correlation between Payload and Success for all Sites'
        )
    else:
        site_filtered = filtered[filtered['Launch Site'] == entered_site]
        fig = px.scatter(
            site_filtered,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title=f'Correlation between Payload and Success for {entered_site}'
        )
    return fig


# ── Run ────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=True)