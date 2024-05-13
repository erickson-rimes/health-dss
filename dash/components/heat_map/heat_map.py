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
                    style={"display": "flex", "flex-direction": "column"},
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
                                        # dbc.Tab(
                                        #     label="Line Plot",
                                        #     tab_id=id_prefix+"analysis_line",
                                        # ),
                                        # dbc.Tab(
                                        #     label="Bar Plot",
                                        #     tab_id=id_prefix+"analysis_bar",
                                        # ),
                                        # dbc.Tab(
                                        #     label="Bar Plot 2",
                                        #     tab_id=id_prefix+"analysis_bar_2",
                                        # ),
                                        # dbc.Tab(
                                        #     label="Count Plot 1",
                                        #     tab_id=id_prefix+"analysis_count_1",
                                        # ),
                                        # dbc.Tab(
                                        #     label="Count Plot 2",
                                        #     tab_id=id_prefix+"analysis_count_2",
                                        # ),
                                        # dbc.Tab(
                                        #     label="Count Plot 3",
                                        #     tab_id=id_prefix+"analysis_count_3",
                                        # ),
                                        # dbc.Tab(
                                        #     label="Count Plot 4",
                                        #     tab_id=id_prefix+"analysis_count_4",
                                        # ),
                                        # dbc.Tab(
                                        #     label="Count Plot 5",
                                        #     tab_id=id_prefix+"analysis_count_5",
                                        # ),
                                        # dbc.Tab(
                                        #     label="Count Plot 6",
                                        #     tab_id=id_prefix+"analysis_count_6",
                                        # ),
                                        # dbc.Tab(
                                        #     label="Pie Chart",
                                        #     tab_id=id_prefix+"analysis_pie",
                                        # ),
                                        # dbc.Tab(
                                        #     label="Dist Plot",
                                        #     tab_id=id_prefix+"analysis_dist",
                                        # ),
                                        # dbc.Tab(
                                        #     label="Pair Plot",
                                        #     tab_id=id_prefix+"analysis_pair",
                                        # ),
                                        # dbc.Tab(
                                        #     label="QQ Plot",
                                        #     tab_id=id_prefix+"analysis_qq",
                                        # ),
                                        # dbc.Tab(
                                        #     label="Reg Plot 1",
                                        #     tab_id=id_prefix+"analysis_reg_1",
                                        # ),
                                        # dbc.Tab(
                                        #     label="Reg Plot 2",
                                        #     tab_id=id_prefix+"analysis_reg_2",
                                        # ),
                                        # dbc.Tab(
                                        #     label="Reg Plot 3",
                                        #     tab_id=id_prefix+"analysis_reg_3",
                                        # ),
                                        # dbc.Tab(
                                        #     label="Area Plot",
                                        #     tab_id=id_prefix+"analysis_area",
                                        # ),
                                        # dbc.Tab(
                                        #     label="Violin Plot",
                                        #     tab_id=id_prefix+"analysis_violin",
                                        # ),
                                        # dbc.Tab(
                                        #     label="Joint Plot 1",
                                        #     tab_id=id_prefix+"analysis_joint_1",
                                        # ),
                                        # dbc.Tab(
                                        #     label="Joint Plot 2",
                                        #     tab_id=id_prefix+"analysis_joint_2",
                                        # ),
                                        # dbc.Tab(
                                        #     label="3D Plot",
                                        #     tab_id=id_prefix+"analysis_3d",
                                        # ),
                                        # dbc.Tab(
                                        #     label="3D Contour Plot",
                                        #     tab_id=id_prefix+"analysis_3d_contour",
                                        # ),
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
