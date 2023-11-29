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


#######################################
# Layout
#######################################
def analysis_layout():
    layout = html.Div(
        [
            # image
            html.Div(
                [
                    html.Div(
                        [
                            html.Img(
                                src="https://images.unsplash.com/photo-1534477675274-cd511de4be22?q=80&w=1170&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
                                style={
                                    "width": "100%",
                                    "height": "auto",
                                    "position": "relative",
                                },
                            ),
                        ],
                        style={
                            "height": "300px",
                            "overflow": "hidden",
                            "position": "relative",
                        },
                    ),
                    html.H1(
                        "Data Analysis",
                        style={
                            "position": "absolute",
                            "top": "80%",
                            "left": "50%",
                            "transform": "translate(-50%, -50%)",
                            "color": "white",
                            "text-align": "center",
                            "width": "100%",
                        },
                    ),
                ],
                style={
                    "position": "relative",
                    "text-align": "center",
                    "color": "white",
                },
            ),
            # tab
            html.Div(
                style={"display": "flex"},
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
                                    dbc.Tab(
                                        label="Bar Plot 2",
                                        tab_id="analysis_bar_2",
                                    ),
                                    dbc.Tab(
                                        label="Count Plot 1",
                                        tab_id="analysis_count_1",
                                    ),
                                    dbc.Tab(
                                        label="Count Plot 2",
                                        tab_id="analysis_count_2",
                                    ),
                                    dbc.Tab(
                                        label="Count Plot 3",
                                        tab_id="analysis_count_3",
                                    ),
                                    dbc.Tab(
                                        label="Count Plot 4",
                                        tab_id="analysis_count_4",
                                    ),
                                    dbc.Tab(
                                        label="Count Plot 5",
                                        tab_id="analysis_count_5",
                                    ),
                                    dbc.Tab(
                                        label="Count Plot 6",
                                        tab_id="analysis_count_6",
                                    ),
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
                                    dbc.Tab(
                                        label="Reg Plot 2",
                                        tab_id="analysis_reg_2",
                                    ),
                                    dbc.Tab(
                                        label="Reg Plot 3",
                                        tab_id="analysis_reg_3",
                                    ),
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
                                    dbc.Tab(
                                        label="Joint Plot 2",
                                        tab_id="analysis_joint_2",
                                    ),
                                    dbc.Tab(
                                        label="Rug Plot",
                                        tab_id="analysis_rug",
                                    ),
                                    dbc.Tab(
                                        label="3D Plot",
                                        tab_id="analysis_3d",
                                    ),
                                    dbc.Tab(
                                        label="Contour Plot",
                                        tab_id="analysis_contour",
                                    ),
                                    dbc.Tab(
                                        label="3D Contour Plot",
                                        tab_id="analysis_3d_contour",
                                    ),
                                    dbc.Tab(
                                        label="Cluster Plot",
                                        tab_id="analysis_cluster",
                                    ),
                                    dbc.Tab(
                                        label="Hexbin Plot",
                                        tab_id="analysis_hexbin",
                                    ),
                                    dbc.Tab(
                                        label="Strip Plot 1",
                                        tab_id="analysis_strip_1",
                                    ),
                                    dbc.Tab(
                                        label="Strip Plot 2",
                                        tab_id="analysis_strip_2",
                                    ),
                                    dbc.Tab(
                                        label="Strip Plot 3",
                                        tab_id="analysis_strip_3",
                                    ),
                                    dbc.Tab(
                                        label="Swarm Plot",
                                        tab_id="analysis_swarm",
                                    ),
                                    dbc.Tab(
                                        label="Story Plot 1",
                                        tab_id="analysis_story_1",
                                    ),
                                    dbc.Tab(
                                        label="Story Plot 2",
                                        tab_id="analysis_story_2",
                                    ),
                                    dbc.Tab(
                                        label="Story Plot 3",
                                        tab_id="analysis_story_3",
                                    ),
                                    dbc.Tab(
                                        label="Story Plot 4",
                                        tab_id="analysis_story_4",
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
            # content: analysis & plot
            html.Div(
                style={"display": "flex"},
                children=[
                    html.Div(
                        style={
                            "width": "50%",
                            "padding": "10px",
                        },
                        children=[
                            html.Div(id="analysis_tab_content_layout"),
                        ],
                    ),
                    html.Div(
                        style={
                            "width": "50%",
                            "padding": "10px",
                        },
                        children=[
                            html.Div(id="analysis_tab_plot_layout"),
                        ],
                    ),
                ],
            ),
            html.Br(),
            html.Br(),
            # download and view code
            html.Div(id="analysis_code"),
        ]
    )

    return layout


#######################################
# Callbacks
#######################################
@my_app.callback(
    [
        Output(
            component_id="analysis_tab_content_layout", component_property="children"
        ),
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
        return (html.P("analysis_reg_2"), html.P("analysis_reg_2"))
    if tab_choice == "analysis_reg_3":
        return (html.P("analysis_reg_3"), html.P("analysis_reg_3"))
    if tab_choice == "analysis_area":
        return (html.P("analysis_area"), html.P("analysis_area"))
    if tab_choice == "analysis_violin":
        return (html.P("analysis_violin"), html.P("analysis_violin"))
    if tab_choice == "analysis_joint_1":
        return (html.P("analysis_joint_1"), html.P("analysis_joint_1"))
    if tab_choice == "analysis_joint_2":
        return (html.P("analysis_joint_2"), html.P("analysis_joint_2"))
    if tab_choice == "analysis_rug":
        return (html.P("analysis_rug"), html.P("analysis_rug"))
    if tab_choice == "analysis_3d":
        return (html.P("analysis_3d"), html.P("analysis_3d"))
    if tab_choice == "analysis_contour":
        return (html.P("analysis_contour"), html.P("analysis_contour"))
    if tab_choice == "analysis_3d_contour":
        return (html.P("analysis_3d_contour"), html.P("analysis_3d_contour"))
    if tab_choice == "analysis_cluster":
        return (html.P("analysis_cluster"), html.P("analysis_cluster"))
    if tab_choice == "analysis_hexbin":
        return (html.P("analysis_hexbin"), html.P("analysis_hexbin"))
    if tab_choice == "analysis_strip_1":
        return (html.P("analysis_strip_1"), html.P("analysis_strip_1"))
    if tab_choice == "analysis_strip_2":
        return (html.P("analysis_strip_2"), html.P("analysis_strip_2"))
    if tab_choice == "analysis_strip_3":
        return (html.P("analysis_strip_3"), html.P("analysis_strip_3"))
    if tab_choice == "analysis_swarm":
        return (html.P("analysis_swarm"), html.P("analysis_swarm"))
    if tab_choice == "analysis_story_1":
        return (html.P("analysis_story_1"), html.P("analysis_story_1"))
    if tab_choice == "analysis_story_2":
        return (html.P("analysis_story_2"), html.P("analysis_story_2"))
    if tab_choice == "analysis_story_3":
        return (html.P("analysis_story_3"), html.P("analysis_story_3"))
    if tab_choice == "analysis_story_4":
        return (html.P("analysis_story_4"), html.P("analysis_story_4"))
