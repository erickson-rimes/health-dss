# dash imports
import plotly.express as px
from dash import html
from dash import Input
from dash import Output
from dash import dcc
import pandas as pd
import numpy as np
import dash_bootstrap_components as dbc
from dash import State
import sqlite3


# file imports
from maindash import my_app
from maindash import df
from utils.file_operation import read_file_as_str

# # read the data
# url = "https://raw.githubusercontent.com/mnguyen0226/two_sigma_property_listing/main/data/train.json"
# df = pd.read_json(url)

# create a dict for all the available 2-dimensional plotly graph types
available_plot_types = {
    "line": px.line,
    "bar": px.bar,
    "scatter": px.scatter,
    "box": px.box,
    "violin": px.violin,
    "histogram": px.histogram,
    "density_contour": px.density_contour,
    "density_heatmap": px.density_heatmap,
    "density_mapbox": px.density_mapbox,
    "funnel": px.funnel,
    "funnel_area": px.funnel_area,
    "pie": px.pie,
    "sunburst": px.sunburst,
    "treemap": px.treemap,
    "scatter_3d": px.scatter_3d,
    "scatter_ternary": px.scatter_ternary,
    "scatter_polar": px.scatter_polar,
}

def line_plot_layout():
    layout = html.Div(
        [
            dcc.Store(id="case-reports-store"),
            dcc.Loading(
                children=[
                    
                    # temporal granularity picker
                    dcc.Graph(id="analysis_line_price_graph"),
                ],
            )
        ]
    )
    return layout

@my_app.callback(
    Output("case-reports-store", "data"),
    [
        Input("analysis_line_plot_date", "start_date"),
        Input("analysis_line_plot_date", "end_date"),
        Input("case_type_filter", "value"),
        Input("reporting_entity_filter", "value")
    ]
)
def update_case_reports_store(start_date, end_date, case_type_filter, reporting_entity_filter):
    filters = {
        "start_date": start_date,
        "end_date": end_date,
        "case_type_filter": case_type_filter if case_type_filter else "",
        "reporting_entity_filter": reporting_entity_filter if reporting_entity_filter else ""
    }

    filtered_df = query_case_reports(filters)

    # Now sort the DataFrame by the 'date' column
    filtered_df = filtered_df.sort_values(by='reportingDate', ascending=False)

    # If you need to reset the index after sorting, you can do so with reset_index()
    filtered_df = filtered_df.reset_index(drop=True)

    return filtered_df.to_json(date_format="iso", orient="split")

def query_case_reports(filters):
    con = sqlite3.connect('case_reports.db')

    base_query = "SELECT * FROM case_reports"

    conditions = []
    params = []

    if filters["start_date"]:
        conditions.append("reportingDate >= ?")
        params.append(filters["start_date"])

    if filters["end_date"]:
        conditions.append("reportingDate <= ?")
        params.append(filters["end_date"])

    if filters["case_type_filter"]:
        conditions.append("caseType IN ({})".format(", ".join(["?"] * len(filters["case_type_filter"]))))
        params.extend(filters["case_type_filter"])

    if filters["reporting_entity_filter"]:
        conditions.append("reportingEntityType IN ({})".format(", ".join(["?"] * len(filters["reporting_entity_filter"]))))
        params.extend(filters["reporting_entity_filter"])

    if conditions:
        base_query += " WHERE " + " AND ".join(conditions)
    

    query_result = pd.read_sql_query(base_query, con, params=params)
    
    return query_result

@my_app.callback(
    Output("analysis_line_price_graph", "figure"),
    [
        Input("case-reports-store", "data"),
        Input("plot-config-dropdown", "value"),
        Input("temporal-granularity-dropdown", "value"),
        Input("reporting_entity_filter", "value"),
        Input("case_type_filter", "value"),
    ],
)
def update_graph(case_reports_data, plot_configuration, temporal_granularity, reporting_entity_filter, case_type_filter):
    filtered_df = pd.read_json(case_reports_data, orient='split')

    fig = None

    title = ""
    #append Daily, Weekly, or Monthly to the title
    if temporal_granularity == "daily":
        title = "Daily"
    elif temporal_granularity == "weekly":
        title = "Weekly"
    elif temporal_granularity == "monthly":
        title = "Monthly"

    title += " "

    
    if plot_configuration == "cases_by_type":
        title += "Cases by Type"
    elif plot_configuration == "cases_by_reporting_entity":
        title += "Cases by Reporting Entity"
    elif plot_configuration == "cases_by_administrative_level":
        title += "Cases by Administrative Level"

    # Create a subtitle based from the case type filter
    subtitle = ""
    if case_type_filter:
        subtitle = "<br><sub>Case Types: " + ", ".join(case_type_filter) + "</sub>" + \
            "<br><sup>Reporting Entities: " + ", ".join(reporting_entity_filter) + "</sup>"

    if plot_configuration == "total_cases_over_time":
        fig = total_cases_over_time(filtered_df, temporal_granularity, title, subtitle)
    elif plot_configuration == "cases_by_type":
        fig = cases_by_type(filtered_df, temporal_granularity, title, subtitle)
    elif plot_configuration == "cases_by_reporting_entity":
        fig = cases_by_reporting_entity(filtered_df, temporal_granularity, title, subtitle)
    elif plot_configuration == "cases_by_administrative_level":
        fig = cases_by_administrative_level(filtered_df,  temporal_granularity, title, subtitle)
    # elif plot_configuration == "lag_time_analysis":
    #     fig = lag_time_analysis(filtered_df, temporal_granularity, title, subtitle)
    
    fig.update_layout(title_x=0.5)

    return fig

def create_date_columns(filtered_df, temporal_granularity):
    if temporal_granularity == "daily":
        filtered_df["reportingDate"] = pd.to_datetime(filtered_df["reportingDate"])
        filtered_df["date"] = filtered_df["reportingDate"].dt.date
    elif temporal_granularity == "weekly":
        filtered_df["reportingDate"] = pd.to_datetime(filtered_df["reportingDate"])
        filtered_df["date"] = filtered_df["reportingDate"].dt.to_period("W").dt.to_timestamp()
    elif temporal_granularity == "monthly":
        filtered_df["reportingDate"] = pd.to_datetime(filtered_df["reportingDate"])
        filtered_df["date"] = filtered_df["reportingDate"].dt.to_period("M").dt.to_timestamp()


# a. Total Cases Over Time
# X-axis: Time (fromDateTime or reportingDate)
# Y-axis: Total number of cases (numberOfCases aggregated)
# Purpose: Track the overall trend of cases reported over time.
def total_cases_over_time(filtered_df, temporal_granularity, title, subtitle):
    # create date columns based on the value of temporal granularity
    create_date_columns(filtered_df, temporal_granularity)

    # group by date
    df_grouped = filtered_df.groupby(["date"]).agg({"numberOfCases": "sum"}).reset_index()

    fig = px.line(df_grouped, x="date", y="numberOfCases", title=f"<b>{title}</b>{subtitle}", labels={"date": "Reporting Date", "numberOfCases": "Number of Cases"})

    return fig

# b. Cases by Type Over Time
# X-axis: Time (fromDateTime or reportingDate)
# Y-axis: Number of cases, segmented by caseType (e.g., Heat Stroke, Dengue Case, Diarrhea Case)
# Purpose: Compare trends across different types of cases to identify patterns or outbreaks.
def cases_by_type(filtered_df, temporal_granularity, title, subtitle):
    # create date columns based on the value of temporal granularity
    create_date_columns(filtered_df, temporal_granularity)

    # group by date and case type
    df_grouped = filtered_df.groupby(["date", "caseType"]).agg({"numberOfCases": "sum"}).reset_index()

    fig = px.line(df_grouped, x="date", y="numberOfCases", color="caseType", title=f"<b>{title}</b>{subtitle}", labels={"date": "Reporting Date", "numberOfCases": "Number of Cases", "caseType": "Case Type"})

    return fig

# # d. Reporting Entity Trends
# X-axis: Time (fromDateTime or reportingDate)
# Y-axis: Number of reports, segmented by reportingEntityType (e.g., Individual, Health Facility, Automated System)
# Purpose: Understand the reporting behavior and possibly the reliability or focus of different reporting entities.
# create subplots for each caseType
def cases_by_reporting_entity(filtered_df, temporal_granularity, title, subtitle):
    # create date columns based on the value of temporal granularity
    create_date_columns(filtered_df, temporal_granularity)

    # group by date and case type
    df_grouped = filtered_df.groupby(["date", "reportingEntityType"]).agg({"numberOfCases": "sum"}).reset_index()

    fig = px.line(df_grouped, x="date", y="numberOfCases", color="reportingEntityType", title=f"<b>{title}</b>{subtitle}", labels={"date": "Reporting Date", "numberOfCases": "Number of Cases", "reportingEntityType": "Reporting Entity Type"})

    return fig

# e. Cases by Administrative Level Over Time
# X-axis: Time (fromDateTime or reportingDate)
# Y-axis: Number of cases, segmented by administrativeLevel (e.g., Country, Municipality, Administrative Post, Suco)
# Purpose: Observe how case trends differ across various administrative levels, which could indicate localized outbreaks or spread.
def cases_by_administrative_level(filtered_df, temporal_granularity, title, subtitle):
    # create date columns based on the value of temporal granularity
    create_date_columns(filtered_df, temporal_granularity)

    filtered_df["administrativeLevelText"] = filtered_df["administrativeLevel"].map({0: "Country", 1: "Municipality", 2: "Administrative Post", 3: "Suco"})

    # group by date and case type
    df_grouped = filtered_df.groupby(["date", "administrativeLevelText"]).agg({"numberOfCases": "sum"}).reset_index()

    fig = px.line(df_grouped, x="date", y="numberOfCases", color="administrativeLevelText", title=f"<b>{title}</b>{subtitle}", labels={"date": "Reporting Date", "numberOfCases": "Number of Cases", "administrativeLevelText": "Administrative Level"})

    return fig

# g. Lag Time Analysis
# X-axis: Time (reportingDate)
# Y-axis: Time lag (difference between reportingDate and fromDateTime or toDateTime)
# Purpose: Understand delays in reporting, which can be critical for real-time public health responses.
def lag_time_analysis(filtered_df, temporal_granularity, title, subtitle):
    # create new date columns
    filtered_df["reportingDate"] = pd.to_datetime(filtered_df["reportingDate"])
    filtered_df["fromDateTime"] = pd.to_datetime(filtered_df["fromDateTime"])

    filtered_df["lagTime"] = (filtered_df["reportingDate"] - filtered_df["fromDateTime"]).dt.days

    fig = px.scatter(filtered_df, x="reportingDate", y="lagTime", title=f"<b>{title}</b>{subtitle}", labels={"reportingDate": "Reporting Date", "lagTime": "Lag Time (Days)"})

    return fig

def line_plot_content():
    return html.Div(
        [
            html.Div([html.H3("Line Plot")]),
            html.Div(
                [
                    html.P(
                        "Line plots are widely used in various fields for visualizing data trends over time. Their primary purpose is to show the continuous change of data points over a period, making them an excellent tool for observing trends, patterns, fluctuations, and comparing multiple data series within the same context."
                    )
                ]
            ),
            html.Br(),
            html.H4("Configuration"),
            html.Label("Analysis", style={"fontWeight": "bold"}),
            dcc.Dropdown(
                id='plot-config-dropdown',
                options=[
                    {'label': 'Cases by Type', 'value': 'cases_by_type'},
                    {'label': 'Cases by Reporting Entity', 'value': 'cases_by_reporting_entity'},
                    {'label': 'Cases by Administrative Level', 'value': 'cases_by_administrative_level'},
                    # {'label': 'Lag Time Analysis', 'value': 'lag_time_analysis'},
                    # {'label': 'Average Cases per Reporting Entity', 'value': 'average_cases_per_reporting_entity'},
                ],
                value="cases_by_type",
                placeholder="Select a plot configuration",
            ),
            html.Br(),
            html.Label("Granularity", style={"fontWeight": "bold"}),
            dcc.Dropdown(
                id="temporal-granularity-dropdown",
                options=[
                    {"label": "Daily", "value": "daily"},
                    {"label": "Weekly", "value": "weekly"},
                    {"label": "Monthly", "value": "monthly"},
                ],
                value="daily",
            ),
            html.Br(),
            html.Br(),
            html.H4("Filters"),
            html.Label("Date Range", style={"fontWeight": "bold", "width": "100%"}),
            html.Br(),
            dcc.DatePickerRange(
                id="analysis_line_plot_date",
                start_date=pd.to_datetime("2024-03-01"),
                end_date=pd.to_datetime("2024-04-01"),
                display_format="YYYY-MM-DD",
            ),
            html.Br(),
            html.Br(),
            # choose case type
            html.Label("Case Type", style={"fontWeight": "bold"}),
            dcc.Dropdown(
                id="case_type_filter",
                options=[
                    {"label": "Heat Stroke", "value": "Heat Stroke"},
                    {"label": "Dengue Case", "value": "Dengue Case"},
                    {"label": "Diarrhea Case", "value": "Diarrhea Case"},
                ],
                multi=True,
                value=["Diarrhea Case"],
            ),
            html.Br(),
            # choose reporting entity
            html.Label("Reporting Entity", style={"fontWeight": "bold"}),
            dcc.Dropdown(
                id="reporting_entity_filter",
                options=[
                    {"label": "Individual", "value": "Individual"},
                    {"label": "Health Facility", "value": "Health Facility"},
                    {"label": "Automated System", "value": "Automated System"},
                ],
                multi=True,
                value=["Individual", "Health Facility", "Automated System"],
            ),
            html.Br(),
            html.Br(),
            html.Br(),
            # Add a download button to save the case-reports-store as csv
            # align the button to the right
            dbc.Button("Download as .CSV", id="download-data", color="primary", style={"width": "100%"}),
            dcc.Download(id='download-csv')     
        ]
    )

# callback to download the case-reports-store as csv
@my_app.callback(
    Output('download-csv', 'data'),
    Input("download-data", "n_clicks"),
    State("case-reports-store", "data"),
    prevent_initial_call=True
)
def download_data(n_clicks, case_reports_data):
    filtered_df = pd.read_json(case_reports_data, orient='split')
    return dcc.send_data_frame(filtered_df.to_csv, "case-reports.csv", index=False)

def line_plot_code():
    return html.Div(
        [
            html.H3("💻 Source Code"),
            html.Br(),
            html.Div(
                [
                    dbc.Button(
                        "View Code",
                        id="analysis_line_plot_collapse_button",
                        className="mb-3",
                        color="primary",
                        n_clicks=0,
                    ),
                    dbc.Collapse(
                        dcc.Markdown(
                            children=read_file_as_str(
                                "./utils/markdown/analysis/line_plot.md"
                            ),
                            mathjax=True,
                        ),
                        id="analysis_line_plot_collapse",
                        is_open=False,
                    ),
                ]
            ),
            dbc.Button(
                "Download Code",
                color="success",
                className="me-1",
                id="analysis_line_plot_download_btn",
            ),
            dcc.Download(id="analysis_line_plot_download"),
        ]
    )


@my_app.callback(
    Output("analysis_line_plot_download", "data"),
    Input("analysis_line_plot_download_btn", "n_clicks"),
    prevent_initial_call=True,
)
def func(n_clicks):
    return dcc.send_file("./utils/download_codes/analysis/line_plot_code.py")


def line_plot_info():

    # make the html div hidden
    return (
        line_plot_content(),
        line_plot_layout(),
        line_plot_code()
    )


@my_app.callback(
    Output("analysis_line_plot_collapse", "is_open"),
    [Input("analysis_line_plot_collapse_button", "n_clicks")],
    [State("analysis_line_plot_collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open
