# file imports
from maindash import my_app, blueprint, server, is_authenticated, keycloak_openid
from components.overview import overview
from components.analysis import analysis
from components.visualization import visualization
from components.interest_level_prediction import interest_level_prediction
from components.price_prediction import price_prediction
from components.virtual_assistant import virtual_assistant
from components.listing import listing
from components.heat_map import heat_map
from components.alert_map import alert_map
from components.about import about
from components.advisories import advisories_feed
from components.weather import weather
import dash
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc

sidebar = html.Div(
    [
        html.Div(
            html.Div(
                [
                    html.I(className="fas fa-solid fa-virus px-2 fa-2xl mr-4", style={"color": "white"}),
                    html.Span(my_app.title, style={"color": "white", "fontSize": "2rem"}),
                ],
                style={"display": "flex", "align-items": "center"},
            ),
            className="sidebar-header",
        ),
        html.Br(),
        html.Br(),
        dbc.Nav(
            [
                dbc.NavLink([html.I(className="fas fa-solid fa-newspaper me-2"), html.Span("Advisories")],
                            href="/", active="exact", className="sidebar-item"),
                dbc.NavLink([html.I(className="fas fa-solid fa-warning me-2"), html.Span("Alerts")],
                            href="/alert_map", active="exact", className="sidebar-item"),
                dbc.NavLink([html.I(className="fas fa-home me-2"), html.Span("Facilities Listing")],
                            href="/listing", active="exact", className="sidebar-item"),
                dbc.NavLink([html.I(className="fas fa-fire me-2"), html.Span("Heat Map")],
                            href="/heat_map", active="exact", className="sidebar-item"),
                dbc.NavLink([html.I(className="fas fa-cloud me-2"), html.Span("Weather")],
                            href="/weather", active="exact", className="sidebar-item"),
                dbc.NavLink([html.I(className="fas fa-solid fa-chart-simple me-2"), html.Span("Data Analysis")],
                            href="/analysis", active="exact", className="sidebar-item"),
                # dbc.DropdownMenu(
                #     id="user-dropdown",
                #     children=[
                #         dbc.DropdownMenuItem("Settings", href="/settings"),
                #         dbc.DropdownMenuItem("Logout", href="/logout"),
                #     ],
                #     nav=True,
                #     className="sidebar-item",
                #     label=[
                #         html.I(className="fas fa-user-alt me-2"),
                #         html.Span("Not logged in")
                #     ],  # Default label with logo
                # )
            ],
            vertical=True,
            pills=True,
        ),
        dbc.Nav(
            [
                dbc.NavItem(
                    dbc.DropdownMenu(
                        children=[
                            dbc.DropdownMenuItem("Settings", href="/settings"),
                            dbc.DropdownMenuItem("Logout", href="/logout"),
                        ],
                        nav=True,
                        in_navbar=True,
                        className="sidebar-item",
                        label=[
                            html.I(className="fas fa-user-alt me-2"),
                            html.Span("Not logged in", id="user-dropdown")
                        ],  # Default label with logo
                    ),
                ),
               
            ],
            vertical=True,
            pills=True,
            # className="user-menu-nav",
            style={"position": "absolute", "bottom": "12px"},
        ),
    ],
    className="sidebar",
)

# Main app layout
my_app.layout = html.Div(
    [
        dcc.Location(id="url"),
        sidebar,
        # html.H1('Hello, Keycloak Authenticated User!'),
        html.Div(id='user-info', style={"display": "none"}),
        html.Div(
            [
                dash.page_container,
            ],
            className="content",
            style={"transition": "margin-left .1s"},
            id="page-content",
        ),
    ]
)

# Display user info callback
@my_app.callback(
    Output('user-info', 'children'),
    [Input('url', 'pathname')]
)
def display_user_info(pathname):
    if is_authenticated():
        # print(blueprint.session)
        token = blueprint.session.token["access_token"]
        userinfo = keycloak_openid.userinfo(token)
        return f"Logged in as: {userinfo['preferred_username']}"
    return "Not logged in"

# Display user info callback
@my_app.callback(
    Output('user-dropdown', 'children'),
    [Input('url', 'pathname')]
)
def display_user_info(pathname):
    if is_authenticated():
        # print(blueprint.session)
        token = blueprint.session.token["access_token"]
        userinfo = keycloak_openid.userinfo(token)
        return userinfo['preferred_username']
    return "Not logged in"

# Render page content callback
@my_app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    # print(pathname)
    if pathname == "/":
        return advisories_feed.advisories_layout()
    elif pathname == "/alert_map":
        return alert_map.alert_map_layout()
    elif pathname == "/weather":
        return weather.weather_layout()
    elif pathname == "/listing":
        return listing.listing_layout()
    elif pathname == "/analysis":
        return analysis.analysis_layout()
    elif pathname == "/visualization":
        return visualization.visualization_layout()
    elif pathname == "/interest_level_prediction":
        return interest_level_prediction.interest_level_prediction_layout()
    elif pathname == "/price_prediction":
        return price_prediction.price_prediction_layout()
    elif pathname == "/heat_map":
        return heat_map.heatmap_layout()
    elif pathname == "/virtual_assistant":
        return virtual_assistant.virtual_assistant_layout()
    elif pathname == "/about":
        return about.about_layout()
    # elif pathname == "/logout":
    #     logout()
    return dbc.Container(
        children=[
            html.H1("404 Error: Page Not found", style={"textAlign": "center", "color": "#082446"}),
            html.Br(),
            html.P(f"Oh no! The pathname '{pathname}' was not recognised...", style={"textAlign": "center"}),
            html.Div(
                style={"display": "flex", "justifyContent": "center"},
                children=[html.Img(src="https://elephant.art/wp-content/uploads/2020/02/gu_announcement_01-1.jpg", alt="hokie", style={"width": "400px"})],
            ),
        ]
    )

# Run the app
if __name__ == "__main__":
    my_app.run_server(debug=True, host="0.0.0.0", port=80)