# dash imports
import dash
from dash import html
from dash import Input
from dash import Output
from dash import dcc
import dash_bootstrap_components as dbc

# file imports
from maindash import my_app
from components.analysis.line_plot import line_plot_info
from components.analysis.bar_plot_1 import bar_plot_1_info
from components.analysis.bar_plot_2 import bar_plot_2_info
from components.analysis.count_plot_1 import count_plot_1_info
from components.analysis.count_plot_2 import count_plot_2_info
from components.analysis.count_plot_3 import count_plot_3_info
from components.analysis.count_plot_4 import count_plot_4_info
from components.analysis.count_plot_5 import count_plot_5_info
from components.analysis.count_plot_6 import count_plot_6_info
from components.analysis.pie_chart import pie_chart_info
from components.analysis.dist_plot import dist_plot_info
from components.analysis.pair_plot import pair_plot_info
from components.analysis.heatmap import heatmap_info
from components.analysis.qq_plot import qq_plot_info
from components.analysis.reg_plot_1 import reg_plot_1_info
from components.analysis.reg_plot_2 import reg_plot_2_info
from components.analysis.reg_plot_3 import reg_plot_3_info
from components.analysis.area_plot import area_plot_info
from components.analysis.violin_plot import violin_plot_info
from components.analysis.joint_plot_1 import joint_plot_1_info
from components.analysis.joint_plot_2 import joint_plot_2_info
from components.analysis.plot_3d import plot_3d_info
from components.analysis.plot_3d_contour import plot_3d_contour_info


#######################################
# Layout
#######################################
def analysis_layout():
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
                                    id="analysis_selected_tab",
                                    children=[
                                        dbc.Tab(
                                            label="Line Plot",
                                            tab_id="analysis_line",
                                        ),
                                        dbc.Tab(
                                            label="Bar Plot 1",
                                            tab_id="analysis_bar_1",
                                        ),
                                        # dbc.Tab(
                                        #     label="Bar Plot 2",
                                        #     tab_id="analysis_bar_2",
                                        # ),
                                        dbc.Tab(
                                            label="Count Plot 1",
                                            tab_id="analysis_count_1",
                                        ),
                                        # dbc.Tab(
                                        #     label="Count Plot 2",
                                        #     tab_id="analysis_count_2",
                                        # ),
                                        # dbc.Tab(
                                        #     label="Count Plot 3",
                                        #     tab_id="analysis_count_3",
                                        # ),
                                        # dbc.Tab(
                                        #     label="Count Plot 4",
                                        #     tab_id="analysis_count_4",
                                        # ),
                                        # dbc.Tab(
                                        #     label="Count Plot 5",
                                        #     tab_id="analysis_count_5",
                                        # ),
                                        # dbc.Tab(
                                        #     label="Count Plot 6",
                                        #     tab_id="analysis_count_6",
                                        # ),
                                        dbc.Tab(
                                            label="Pie Chart",
                                            tab_id="analysis_pie",
                                        ),
                                        dbc.Tab(
                                            label="Dist Plot",
                                            tab_id="analysis_dist",
                                        ),
                                        dbc.Tab(
                                            label="Pair Plot",
                                            tab_id="analysis_pair",
                                        ),
                                        dbc.Tab(
                                            label="Heatmap",
                                            tab_id="analysis_heatmap",
                                        ),
                                        dbc.Tab(
                                            label="QQ Plot",
                                            tab_id="analysis_qq",
                                        ),
                                        dbc.Tab(
                                            label="Reg Plot 1",
                                            tab_id="analysis_reg_1",
                                        ),
                                        # dbc.Tab(
                                        #     label="Reg Plot 2",
                                        #     tab_id="analysis_reg_2",
                                        # ),
                                        # dbc.Tab(
                                        #     label="Reg Plot 3",
                                        #     tab_id="analysis_reg_3",
                                        # ),
                                        dbc.Tab(
                                            label="Area Plot",
                                            tab_id="analysis_area",
                                        ),
                                        dbc.Tab(
                                            label="Violin Plot",
                                            tab_id="analysis_violin",
                                        ),
                                        dbc.Tab(
                                            label="Joint Plot 1",
                                            tab_id="analysis_joint_1",
                                        ),
                                        # dbc.Tab(
                                        #     label="Joint Plot 2",
                                        #     tab_id="analysis_joint_2",
                                        # ),
                                        dbc.Tab(
                                            label="3D Plot",
                                            tab_id="analysis_3d",
                                        ),
                                        dbc.Tab(
                                            label="3D Contour Plot",
                                            tab_id="analysis_3d_contour",
                                        ),
                                    ],
                                    active_tab="analysis_line",
                                ),
                            ]
                        ),
                    ],
                ),
                html.Br(),
                html.Br(),
                html.Br(),
                # content: analysis & plot
                html.Div(
                    style={"display": "flex"},
                    children=[
                        # html.Div(
                        #     style={
                        #         "width": "30%",
                        #         "padding": "10px",
                        #     },
                        #     children=[
                        #         html.Div(id="analysis_tab_content_layout"),
                        #     ],
                        # ),
                        html.Div(
                            style={
                                "width": "100%",
                                "height": "100%",
                                "padding": "10px",
                            },
                            children=[
                                html.Div(id="analysis_tab_plot_layout"),
                            ],
                        ),
                    ],
                ),
                html.Br(),
                # download and view code
                html.Div(),
                # make invisible
                html.Div(id="analysis_code", style={"display": "none"}),
            ]), 
            html.Div(
                style={"display": "flex", "width": "25%", "padding": "12px"},
                children=[
                    html.Div(
                        style={
                            "width": "100%",
                        },
                        children=[
                            html.Div(id="analysis_tab_content_layout"),
                        ],
                    ),
                    # html.Div(
                    #     style={
                    #         "width": "30%",
                    #         "padding": "10px",
                    #     },
                    #     # children=[
                    #     #     html.Div(id="analysis_tab_plot_layout"),
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
        Output(component_id="analysis_tab_content_layout", component_property="children"),
        Output(component_id="analysis_tab_plot_layout", component_property="children"),
        Output(component_id="analysis_code", component_property="children"),
    ],
    [Input(component_id="analysis_selected_tab", component_property="active_tab")],
)
def render_tab(tab_choice):
    """Renders the selected subtab's layout

    Args:
        tab_choice (str): selected subtab

    Returns:
        selected subtab's layout
    """
    if tab_choice == "analysis_line":
        return line_plot_info()
    if tab_choice == "analysis_bar_1":
        return bar_plot_1_info()
    if tab_choice == "analysis_bar_2":
        return bar_plot_2_info()
    if tab_choice == "analysis_count_1":
        return count_plot_1_info()
    if tab_choice == "analysis_count_2":
        return count_plot_2_info()
    if tab_choice == "analysis_count_3":
        return count_plot_3_info()
    if tab_choice == "analysis_count_4":
        return count_plot_4_info()
    if tab_choice == "analysis_count_5":
        return count_plot_5_info()
    if tab_choice == "analysis_count_6":
        return count_plot_6_info()
    if tab_choice == "analysis_pie":
        return pie_chart_info()
    if tab_choice == "analysis_dist":
        return dist_plot_info()
    if tab_choice == "analysis_pair":
        return pair_plot_info()
    if tab_choice == "analysis_heatmap":
        return heatmap_info()
    if tab_choice == "analysis_qq":
        return qq_plot_info()
    if tab_choice == "analysis_reg_1":
        return reg_plot_1_info()
    if tab_choice == "analysis_reg_2":
        return reg_plot_2_info()
    if tab_choice == "analysis_reg_3":
        return reg_plot_3_info()
    if tab_choice == "analysis_area":
        return area_plot_info()
    if tab_choice == "analysis_violin":
        return violin_plot_info()
    if tab_choice == "analysis_joint_1":
        return joint_plot_1_info()
    if tab_choice == "analysis_joint_2":
        return joint_plot_2_info()
    if tab_choice == "analysis_3d":
        return plot_3d_info()
    if tab_choice == "analysis_3d_contour":
        return plot_3d_contour_info()
