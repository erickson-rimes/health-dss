# dash imports
import dash
from dash import html
from dash import Input
from dash import Output
from dash import dcc
import dash_bootstrap_components as dbc

# file imports
from maindash import my_app

from components.heat_map.heatmap_info import heatmap_plot_info

id_prefix="heatmap123"

#######################################
# Layout
#######################################
def heatmap_layout():
    layout = html.Div(
            # split horizontally
        style={"display": "flex"},
        children = [
            html.Div(
                style={"width": "75%", "padding": "12px"},
                children=
                [
                html.Div(
                    # stack vertically
                    style={"display": "flex", "flex-direction": "column", "display": "none"},
                    children=[
                        html.Div(
                            [
                                dbc.Tabs(
                                    id=id_prefix+"analysis_selected_tab",
                                    children=[
                                        dbc.Tab(
                                            label="Heatmap",
                                            tab_id=id_prefix+"analysis_heatmap",
                                        ),
                                    ],
                                    active_tab=id_prefix+"analysis_heatmap",
                                ),
                            ]
                        ),
                    ],
                ),
                html.Br(),
                html.Div(
                    style={"display": "flex"},
                    children=[
                        # html.Div(
                        #     style={
                        #         "width": "30%",
                        #         "padding": "10px",
                        #     },
                        #     children=[
                        #         html.Div(id=id_prefix+"analysis_tab_content_layout"),
                        #     ],
                        # ),
                        html.Div(
                            # set background color to gray
                            style={
                                "background-color": "#f9f9f9",
                                "width": "100%",
                                "height": "100%",
                            },
                            children=[
                                html.Div(id=id_prefix+"analysis_tab_plot_layout"),
                            ],
                        ),
                    ],
                ),
                html.Br(),
                # download and view code
                html.Div(),
                # make invisible
                html.Div(id=id_prefix+"analysis_code", style={"display": "none"}),
            ]), 
            html.Div(
                style={"display": "flex", "width": "25%", "padding": "12px"},
                children=[
                    html.Div(
                        style={
                            "width": "100%",
                        },
                        children=[
                            html.Div(id=id_prefix+"analysis_tab_content_layout"),
                        ],
                    ),
                    # html.Div(
                    #     style={
                    #         "width": "30%",
                    #         "padding": "10px",
                    #     },
                    #     # children=[
                    #     #     html.Div(id=id_prefix+"analysis_tab_plot_layout"),
                    #     # ],
                    # ),
                ],
            )
        ])
        

    return layout


#######################################
# Callbacks
#######################################
@my_app.callback(
    [
        Output(component_id=id_prefix+"analysis_tab_content_layout", component_property="children"),
        Output(component_id=id_prefix+"analysis_tab_plot_layout", component_property="children"),
        Output(component_id=id_prefix+"analysis_code", component_property="children"),
    ],
    [Input(component_id=id_prefix+"analysis_selected_tab", component_property="active_tab")],
)
def render_tab(tab_choice):
    """Renders the selected subtab's layout

    Args:
        tab_choice (str): selected subtab

    Returns:
        selected subtab's layout
    """
    return heatmap_plot_info()
