from dash import dcc
from dash import html
from dash import Input, Output, State, ALL
import sqlite3
import pandas as pd
from datetime import datetime

from maindash import my_app

# Features:
# Can share to social media
# Can download as PDF

# Connect to the SQLite database
def fetch_advisories(offset=0, limit=10):
    conn = sqlite3.connect('advisories.db')
    query = f"SELECT * FROM advisory ORDER BY publication_date DESC LIMIT {limit} OFFSET {offset}"
    advisories = pd.read_sql_query(query, conn)
    conn.close()
    return advisories

def fetch_advisory_details(advisory_id):
    conn = sqlite3.connect('advisories.db')
    query = f"SELECT * FROM advisory WHERE id = ?"
    advisory = pd.read_sql_query(query, conn, params=(advisory_id,))
    conn.close()
    return advisory.iloc[0] if not advisory.empty else None

# Layout of the app
def advisories_layout():
    layout = html.Div([
        html.Div([
            html.H2("Advisories"),
            dcc.Loading(id="loading-icon", children=[
                html.Div(id='timeline-container', children=[])
            ], type="circle"),
            html.Button('Load More', id='load-more-button', n_clicks=0, style={'float': 'right', 'margin': '20px'}),
            html.Div(id='scroll-end', style={'height': '20px'})  # Element to detect scrolling to the bottom
        ], style={'width': '35%', 'float': 'left', 'padding': '20px', 'height': '100vh', 'overflowY': 'scroll'}),

        html.Div([
            # html.H1(" "),
            html.Div(id='advisory-details')
        ], style={'width': '65%', 'float': 'right', 'padding': '20px', 'height': '100vh', 'overflowY': 'scroll'})
    ], style={'width': '100%', 'overflow': 'hidden'})

    return layout

# Function to format dates
def format_date(date_str):
    try:
        date_obj = datetime.fromisoformat(date_str)
        return date_obj.strftime("%B %d, %Y")
    except ValueError:
        return date_str
    
# Callback to update the timeline
@my_app.callback(
    Output('timeline-container', 'children'),
    [Input('load-more-button', 'n_clicks')],
    [State('timeline-container', 'children')]
)
def load_more_advisories(n_clicks, current_children):
    offset = n_clicks * 10
    advisories = fetch_advisories(offset=offset, limit=10)
    new_items = []
    
    for _, row in advisories.iterrows():
        new_items.append(html.Div([
            html.H4(row['title'], id={'type': 'advisory-title', 'index': row['id']}),
            html.P(f"By {row['author_name']} on {format_date(row['publication_date'])}"),
            # ellipsis beyond certain number of characters
            # html.P(row['content']),
            html.P(row['content'][:200] + '...'),
            html.Hr()
        ], style={'margin': '20px', 'cursor': 'pointer'}, id={'type': 'advisory-item', 'index': row['id']}))

    if current_children is None:
        current_children = []
    
    return current_children + new_items

# Callback to display advisory details
@my_app.callback(
    Output('advisory-details', 'children'),
    Output({'type': 'advisory-item', 'index': ALL}, 'n_clicks'),
    [Input({'type': 'advisory-item', 'index': ALL}, 'n_clicks')],
    [State({'type': 'advisory-item', 'index': ALL}, 'id')]
)
def display_advisory_details(n_clicks, ids):
    if not any(n_clicks):
        return "Click on an advisory to see details", [0] * len(n_clicks)
    
    clicked_id = [p['index'] for p, n in zip(ids, n_clicks) if n]
    if not clicked_id:
        return "Click on an advisory to see details", [0] * len(n_clicks)
    
    advisory = fetch_advisory_details(clicked_id[0])
    if advisory is None:
        return "Advisory not found", [0] * len(n_clicks)

    details = html.Div([
        html.H2(advisory['title']),
        html.P(f"By {advisory['author_name']} on {format_date(advisory['publication_date'])}"),
        html.P(advisory['content']),
        # Add more details as needed
    ])
    
    return details, [0] * len(n_clicks)