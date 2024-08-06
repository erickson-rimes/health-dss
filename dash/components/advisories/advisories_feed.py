from dash import dcc
from dash import html
from dash import Input, Output, State, ALL
import sqlite3
import pandas as pd
from datetime import datetime
import dash_bootstrap_components as dbc

from maindash import my_app, blueprint, keycloak_openid
import uuid

# Features:
# Can share to social media
# Can download as PDF

# Connect to the SQLite database
def fetch_advisories(offset=0, limit=10):
    conn = sqlite3.connect('advisories.db')
    query = f"SELECT * FROM advisory ORDER BY publication_date DESC LIMIT {limit} OFFSET {offset}"
    advisories = pd.read_sql_query(query, conn)
    # print(advisories)
    conn.close()
    return advisories

def fetch_advisory_details(advisory_id):
    conn = sqlite3.connect('advisories.db')
    query = f"SELECT * FROM advisory WHERE id = ?"
    advisory = pd.read_sql_query(query, conn, params=(advisory_id,))
    conn.close()
    return advisory.iloc[0] if not advisory.empty else None

# Layout of the app
# Layout of the app
def advisories_layout():
    layout = html.Div([
        html.Div([
            html.Div(id='advisory-details')
        ], style={'width': '70%', 'float': 'left', 'padding': '20px', 'height': '100vh', 'overflowY': 'scroll'}),
        html.Div([
            html.H2("Advisories", style={'display': 'inline'}),
            html.Button('+', id='add-advisory-button', n_clicks=0, style={'margin-left': '20px', 'display': 'inline'}),
            dcc.Loading(id="loading-icon", children=[
                html.Div(id='timeline-container', children=[])
            ], type="circle"),
            html.Button('Load More', id='load-more-button', n_clicks=0, style={'float': 'right', 'margin': '20px'}),
            html.Div(id='scroll-end', style={'height': '20px'})  # Element to detect scrolling to the bottom
        ], style={'width': '30%', 'float': 'right', 'padding': '20px', 'height': '100vh', 'overflowY': 'scroll'}),

        # Hidden div for storing advisory data
        html.Div(id='new-advisory-data', style={'display': 'none'}),
        
        # Add Advisory Modal
        dbc.Modal(
            [
                dbc.ModalHeader("Create New Advisory"),
                dbc.ModalBody([
                    dbc.Input(id="advisory-title", placeholder="Title", type="text"),
                    dbc.Textarea(id="advisory-content", placeholder="Advisory Content"),
                    dcc.Upload(
                        id='upload-media',
                        children=html.Div([
                            'Drag and Drop or ',
                            html.A('Select Files')
                        ]),
                        style={
                            'width': '100%',
                            'height': '60px',
                            'lineHeight': '60px',
                            'borderWidth': '1px',
                            'borderStyle': 'dashed',
                            'borderRadius': '5px',
                            'textAlign': 'center',
                            'margin': '10px'
                        },
                        multiple=True
                    ),
                    html.Div(id='uploaded-files', style={'margin': '10px'})
                ]),
                dbc.ModalFooter(
                    dbc.Button("Save", id="save-advisory-button", className="ml-auto")
                ),
            ],
            id="add-advisory-modal",
            is_open=False,
        )
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
    [Input('load-more-button', 'n_clicks'), Input('new-advisory-data', 'children')],
    [State('timeline-container', 'children')]
)
def load_more_advisories(n_clicks, new_advisory_data, current_children):
    offset = n_clicks * 10
    advisories = fetch_advisories(offset=offset, limit=10)
    new_items = []

    
    for _, row in advisories.iterrows():

        content = ""

        if row["content"] is not None:
            content = row["content"]

        title = "Public Health Advisory"

        if row["title"] is not None:
            title = row["title"]

        if len(content) > 150:
            content_preview = content[:150] + "..."

        new_items.append(html.Div([
            html.H4(title, id={'type': 'advisory-title', 'index': row['id']}),
            html.P(f"By {row['author_name']} on {format_date(row['publication_date'])}"),
            html.P(content_preview),
            html.Hr()
        ], style={'margin': '20px', 'cursor': 'pointer'}, id={'type': 'advisory-item', 'index': row['id']}))

    if current_children is None:
        current_children = []
    
    return current_children + new_items

def uuid_to_int(uuid_str):
    try:
        # Convert the UUID string to a UUID object
        uuid_obj = uuid.UUID(uuid_str)
        # Convert the UUID object to an integer
        uuid_int = uuid_obj.int
        return uuid_int
    except ValueError as e:
        # Handle the case where the UUID string is not valid
        print(f"Invalid UUID format: {e}")
        return None

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

    media_src = ""
    val = uuid_to_int(clicked_id[0]) % 3

    if val == 0:
        media_src = "https://as2.ftcdn.net/v2/jpg/02/66/38/15/1000_F_266381525_alVrbw15u5EjhIpoqqa1eI5ghSf7hpz7.jpg"
    elif val == 1:
        media_src = "https://as1.ftcdn.net/v2/jpg/05/55/23/32/1000_F_555233276_2cWJCmNtBsSt06OO5Ne5igMEf8mLwRY1.jpg"
    else:
        media_src = "https://as2.ftcdn.net/v2/jpg/02/49/81/85/1000_F_249818599_bHaVu7ATJUbPwNpNOhaebg1LO6Zf8VVa.jpg"

    details = html.Div([
        html.H2(advisory['title']),
        html.P(f"By {advisory['author_name']} on {format_date(advisory['publication_date'])}"),
        html.P(advisory['content']),
        html.Img(src=media_src, style={"width": "100%"})
        # Add more details as needed
    ])
    
    return details, [0] * len(n_clicks)

# Callback to toggle the add advisory modal
@my_app.callback(
    Output("add-advisory-modal", "is_open"),
    [Input("add-advisory-button", "n_clicks"), Input("save-advisory-button", "n_clicks")],
    [State("add-advisory-modal", "is_open")]
)
def toggle_add_advisory_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

# Callback to handle advisory creation
@my_app.callback(
    Output('new-advisory-data', 'children'),
    [Input("save-advisory-button", "n_clicks")],
    [State("advisory-title", "value"), State("advisory-content", "value"), State('upload-media', 'contents')]
)
def save_advisory(n_clicks, title, content, media_contents):
    if n_clicks is None:
        return ""
    
    token = blueprint.session.token["access_token"]
    userinfo = keycloak_openid.userinfo(token)
    print(userinfo)
    # author_name = userinfo['preferred_username']
    
    new_advisory = {
        'id': str(uuid.uuid4()),
        'title': title,
        'author_id': userinfo['sub'],  # Replace with actual author ID
        'author_name': userinfo['name'],  # Replace with actual author name
        'author_role': 'Author Role',  # Replace with actual author role
        'content': content,
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat(),
        'status': 'published',  # Set appropriate status
        'publication_date': datetime.now().isoformat()
    }

    print("Saving new advisory...")
    # print(new_advisory)

    conn = sqlite3.connect('advisories.db')
    
    insert_advisory(conn, new_advisory)

    # add handling of attachments here

    conn.commit()
    conn.close()

    print("Advisory saved successfully")
    
    return new_advisory['id']

# Callback to handle file uploads
@my_app.callback(
    Output('uploaded-files', 'children'),
    [Input('upload-media', 'filename')],
    [State('upload-media', 'contents')]
)
def update_output(uploaded_filenames, uploaded_file_contents):
    if uploaded_filenames is not None and uploaded_file_contents is not None:
        children = [
            html.Div(f'{filename}')
            for filename in uploaded_filenames
        ]
        return children

    return "No files uploaded."

# Insert functions for SQLite
def insert_advisory(c, advisory):
    result = c.execute('''
        INSERT INTO advisory (
            id, title, author_id, author_name, author_role, content, created_at, updated_at, status, publication_date
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        advisory['id'],
        advisory['title'],
        advisory['author_id'],
        advisory['author_name'],
        advisory['author_role'],
        advisory['content'],
        advisory['created_at'],
        advisory['updated_at'],
        advisory['status'],
        advisory['publication_date']
    ))

    print(result)