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

def get_unique_values(column_name):
    conn = sqlite3.connect('sqlite_dbs/case_reports.db')
    query = f"SELECT DISTINCT [{column_name}] FROM case_reports"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df[column_name].dropna().tolist()

def bar_plot_layout():
    layout = html.Div(
        [
            dcc.Store(id="bar-case-reports-store"),
            dcc.Loading(
                children=[
                    dcc.Dropdown(
                        id='bar-plot-mode-dropdown',
                        options=[
                            {'label': 'Group', 'value': 'group'},
                            {'label': 'Stack', 'value': 'stack'},
                            {'label': 'Overlay', 'value': 'overlay'},
                            {'label': 'Relative', 'value': 'relative'}
                        ],
                        value="group",
                        placeholder="Select a bar plot mode",
                    ),
                    # temporal granularity picker
                    dcc.Graph(id="bar_graph"),
                ],
            )
        ]
    )
    return layout

@my_app.callback(
    Output("bar-case-reports-store", "data"),
    [
        Input("analysis_bar_plot_date", "start_date"),
        Input("analysis_bar_plot_date", "end_date"),
        Input("bar_plot_case_type_filter", "value"),
        Input("bar_plot_reporting_entity_filter", "value")
    ]
)
def update_case_reports_store(start_date, end_date, bar_plot_case_type_filter, bar_plot_reporting_entity_filter):
    filters = {
        "start_date": start_date,
        "end_date": end_date,
        "bar_plot_case_type_filter": bar_plot_case_type_filter if bar_plot_case_type_filter else "",
        "bar_plot_reporting_entity_filter": bar_plot_reporting_entity_filter if bar_plot_reporting_entity_filter else ""
    }

    filtered_df = query_case_reports(filters)

    # Now sort the DataFrame by the 'date' column
    filtered_df = filtered_df.sort_values(by='reportingDate', ascending=False)

    # If you need to reset the index after sorting, you can do so with reset_index()
    filtered_df = filtered_df.reset_index(drop=True)

    return filtered_df.to_json(date_format="iso", orient="split")

def query_case_reports(filters):
    con = sqlite3.connect('sqlite_dbs/case_reports.db')

    base_query = "SELECT * FROM case_reports"

    conditions = []
    params = []

    if filters["start_date"]:
        conditions.append("reportingDate >= ?")
        params.append(filters["start_date"])

    if filters["end_date"]:
        conditions.append("reportingDate <= ?")
        params.append(filters["end_date"])

    if filters["bar_plot_case_type_filter"]:
        conditions.append("caseType IN ({})".format(", ".join(["?"] * len(filters["bar_plot_case_type_filter"]))))
        params.extend(filters["bar_plot_case_type_filter"])

    if filters["bar_plot_reporting_entity_filter"]:
        conditions.append("reportingEntityType IN ({})".format(", ".join(["?"] * len(filters["bar_plot_reporting_entity_filter"]))))
        params.extend(filters["bar_plot_reporting_entity_filter"])

    if conditions:
        base_query += " WHERE " + " AND ".join(conditions)
    

    query_result = pd.read_sql_query(base_query, con, params=params)
    
    return query_result

@my_app.callback(
    Output("bar_graph", "figure"),
    [
        Input("bar-case-reports-store", "data"),
        Input("bar-plot-config-dropdown", "value"),
        Input("bar-plot-mode-dropdown", "value"),
        Input("bar_plot_reporting_entity_filter", "value"),
        Input("bar_plot_case_type_filter", "value"),
    ],
    [
        State("analysis_bar_plot_date", "start_date"),
        State("analysis_bar_plot_date", "end_date"),
    ]
)
def update_graph(
    case_reports_data, 
    plot_configuration, 
    bar_plot_mode,
    bar_plot_reporting_entity_filter, 
    bar_plot_case_type_filter, 
    start_date, 
    end_date):
    filtered_df = pd.read_json(case_reports_data, orient='split')

    fig = None

    title = " "
    #append Daily, Weekly, or Monthly to the title
    # if temporal_granularity == "daily":
    #     title = "Daily"
    # elif temporal_granularity == "weekly":
    #     title = "Weekly"
    # elif temporal_granularity == "monthly":
    #     title = "Monthly"

    # title += " "

    
    if plot_configuration == "cases_by_type":
        title += "Cases by Type"
    elif plot_configuration == "cases_by_reporting_entity":
        title += "Cases by Reporting Entity"
    elif plot_configuration == "cases_by_administrative_level":
        title += "Cases by Administrative Level"
    elif plot_configuration == "cases_by_age_group":
        title += "Cases by Age Group"
    elif plot_configuration == "cases_by_sex_group":
        title += "Cases by Sex Group"

    # Put the date range in the title in the format YYYY-MM-DD
    start_date_str = pd.to_datetime(start_date).strftime("%Y-%m-%d")
    end_date_str = pd.to_datetime(end_date).strftime("%Y-%m-%d")
    title += f" ({start_date_str} to {end_date_str})"

    # Create a subtitle based from the case type filter
    subtitle = ""
    if bar_plot_case_type_filter:
        subtitle = "<br><sub>Case Types: " + ", ".join(bar_plot_case_type_filter) + "</sub>" + \
            "<br><sup>Reporting Entities: " + ", ".join(bar_plot_reporting_entity_filter) + "</sup>"

    if plot_configuration == "total_cases_over_time":
        fig = total_cases_over_time(filtered_df, title, subtitle)
    elif plot_configuration == "cases_by_type":
        fig = cases_by_type(filtered_df, title, subtitle)
    elif plot_configuration == "cases_by_reporting_entity":
        fig = cases_by_reporting_entity(filtered_df, title, subtitle)
    elif plot_configuration == "cases_by_administrative_level":
        fig = cases_by_administrative_level(filtered_df, title, subtitle)
    elif plot_configuration == "cases_by_age_group":
        fig = cases_by_age_group(filtered_df, title, subtitle)
    elif plot_configuration == "cases_by_sex_group":
        fig = cases_by_sex_group(filtered_df, title, subtitle)
    # elif plot_configuration == "lag_time_analysis":
    #     fig = lag_time_analysis(filtered_df, title, subtitle)
    
    fig.update_layout(title_x=0.5, barmode=bar_plot_mode)

    return fig

# def create_date_columns(filtered_df, temporal_granularity):
#     if temporal_granularity == "daily":
#         filtered_df["reportingDate"] = pd.to_datetime(filtered_df["reportingDate"])
#         filtered_df["date"] = filtered_df["reportingDate"].dt.date
#     elif temporal_granularity == "weekly":
#         filtered_df["reportingDate"] = pd.to_datetime(filtered_df["reportingDate"])
#         filtered_df["date"] = filtered_df["reportingDate"].dt.to_period("W").dt.to_timestamp()
#     elif temporal_granularity == "monthly":
#         filtered_df["reportingDate"] = pd.to_datetime(filtered_df["reportingDate"])
#         filtered_df["date"] = filtered_df["reportingDate"].dt.to_period("M").dt.to_timestamp()


# a. Total Cases Over Time
# X-axis: Time (fromDateTime or reportingDate)
# Y-axis: Total number of cases (numberOfCases aggregated)
# Purpose: Track the overall trend of cases reported over time.
def total_cases_over_time(filtered_df, title, subtitle):
    # create date columns based on the value of temporal granularity
    # create_date_columns(filtered_df, temporal_granularity)

    # group by date
    df_grouped = filtered_df.groupby(["date"]).agg({"numberOfCases": "sum"}).reset_index()

    fig = px.line(df_grouped, x="date", y="numberOfCases", title=f"<b>{title}</b>{subtitle}", labels={"date": "Reporting Date", "numberOfCases": "Number of Cases"})

    return fig

# b. Cases by Type Over Time
# X-axis: Time (fromDateTime or reportingDate)
# Y-axis: Number of cases, segmented by caseType (e.g., Heat Stroke, Dengue Case, Diarrhea Case)
# Purpose: Compare trends across different types of cases to identify patterns or outbreaks.
def cases_by_type(filtered_df, title, subtitle):
    # create date columns based on the value of temporal granularity
    # create_date_columns(filtered_df, temporal_granularity)

    # group by case type and sum up the number of cases
    df_grouped = filtered_df.groupby("caseType").agg({"numberOfCases": "sum"}).reset_index()

    # create a bar plot grouped by case type
    fig = px.bar(df_grouped, x="caseType", y="numberOfCases", title=f"<b>{title}</b>{subtitle}", labels={"numberOfCases": "Number of Cases", "caseType": "Case Type"})

    return fig


# # d. Reporting Entity Trends
# X-axis: Time (fromDateTime or reportingDate)
# Y-axis: Number of reports, segmented by reportingEntityType (e.g., Individual, Health Facility, Automated System)
# Purpose: Understand the reporting behavior and possibly the reliability or focus of different reporting entities.
# create subplots for each caseType
def cases_by_reporting_entity(filtered_df, title, subtitle):
    # create date columns based on the value of temporal granularity
    # create_date_columns(filtered_df, temporal_granularity)

    # group by reporting entity type and sum up the number of cases
    df_grouped = filtered_df.groupby(["caseType", "reportingEntityType"]).agg({"numberOfCases": "sum"}).reset_index()

    # create a bar plot grouped by reporting entity type
    fig = px.bar(df_grouped, x="reportingEntityType", y="numberOfCases", color="caseType", category_orders={"caseType": ["Heat Stroke", "Dengue Case", "Diarrhea Case"]}, title=f"<b>{title}</b>{subtitle}", labels={"numberOfCases": "Number of Cases", "reportingEntityType": "Reporting Entity Type", "caseType": "Case Type"})

    return fig

# e. Cases by Administrative Level Over Time
# X-axis: Time (fromDateTime or reportingDate)
# Y-axis: Number of cases, segmented by administrativeLevel (e.g., Country, Municipality, Administrative Post, Suco)
# Purpose: Observe how case trends differ across various administrative levels, which could indicate localized outbreaks or spread.
def cases_by_administrative_level(filtered_df, title, subtitle):
    # create date columns based on the value of temporal granularity
    # create_date_columns(filtered_df, temporal_granularity)

    filtered_df["administrativeLevelText"] = filtered_df["administrativeLevel"].map({0: "Country", 1: "Municipality", 2: "Administrative Post", 3: "Suco"})

    df_grouped = filtered_df.groupby(["caseType", "administrativeLevelText"]).agg({"numberOfCases": "sum"}).reset_index()

    # create a bar plot grouped by reporting entity type
    fig = px.bar(df_grouped, x="administrativeLevelText", y="numberOfCases", color="caseType", category_orders={"caseType": ["Heat Stroke", "Dengue Case", "Diarrhea Case"]}, title=f"<b>{title}</b>{subtitle}", labels={"numberOfCases": "Number of Cases", "administrativeLevelText": "Reporting Entity Type", "caseType": "Case Type"})

    return fig

def cases_by_age_group(filtered_df, title, subtitle):
    # Prepare data for plotting
    age_groups = ['ageGroup0To4Cases', 'ageGroup5To18Cases', 'ageGroup19To59Cases', 'ageGroup60PlusCases', 'ageGroupUnknownCases']

    # Melt the DataFrame to have a single column for age groups
    df_melted = filtered_df.melt(id_vars=['caseType'], value_vars=age_groups, var_name='Age Group', value_name='Number of Cases')

    # Rename age groups for better readability
    df_melted['Age Group'] = df_melted['Age Group'].str.replace('ageGroup', '').str.replace('Cases', '')

    df_grouped = df_melted.groupby(["caseType", "Age Group"]).agg({"Number of Cases": "sum"}).reset_index()

    # print(df_melted.head())

    # Plotting using Plotly
    fig = px.bar(df_grouped, x='caseType', y='Number of Cases', color='Age Group',
                title=f"<b>{title}</b>{subtitle}",
                labels={'caseType': 'Case Type', 'Number of Cases': 'Number of Cases', 'Age Group': 'Age Group'})

    return fig


def cases_by_sex_group(filtered_df, title, subtitle):
    # Prepare data for plotting
    sex_groups = ['sexGroupMaleCases', 'sexGroupFemaleCases', 'sexGroupUnknownCases']

    # Melt the DataFrame to have a single column for sex groups
    df_melted = filtered_df.melt(id_vars=['caseType'], value_vars=sex_groups, var_name='Sex Group', value_name='Number of Cases')

    # Rename sex groups for better readability
    df_melted['Sex Group'] = df_melted['Sex Group'].str.replace('sexGroup', '').str.replace('Cases', '')

    df_grouped = df_melted.groupby(["caseType", "Sex Group"]).agg({"Number of Cases": "sum"}).reset_index()

    # Plotting using Plotly
    fig = px.bar(df_grouped, x='caseType', y='Number of Cases', color='Sex Group', 
                title=f"<b>{title}</b>{subtitle}",
                labels={'caseType': 'Case Type', 'Number of Cases': 'Number of Cases', 'Sex Group': 'Sex Group'})

    return fig

# g. Lag Time Analysis
# X-axis: Time (reportingDate)
# Y-axis: Time lag (difference between reportingDate and fromDateTime or toDateTime)
# Purpose: Understand delays in reporting, which can be critical for real-time public health responses.
def lag_time_analysis(filtered_df, title, subtitle):
    # create new date columns
    filtered_df["reportingDate"] = pd.to_datetime(filtered_df["reportingDate"])
    filtered_df["fromDateTime"] = pd.to_datetime(filtered_df["fromDateTime"])

    filtered_df["lagTime"] = (filtered_df["reportingDate"] - filtered_df["fromDateTime"]).dt.days

    fig = px.scatter(filtered_df, x="reportingDate", y="lagTime", title=f"<b>{title}</b>{subtitle}", labels={"reportingDate": "Reporting Date", "lagTime": "Lag Time (Days)"})

    return fig

def bar_plot_content():

    case_types = get_unique_values('caseType')

    return html.Div(
        [
            html.Div([html.H3("Bar Plot")]),
            html.Div(
                [
                    html.P(
                        "Bar plots are commonly used to compare categorical data or to show the distribution of a single categorical variable. They consist of rectangular bars with lengths proportional to the values they represent. Bar plots are effective for visualizing data across different categories and identifying patterns or trends."
                    )
                ]
            ),
            html.Br(),
            html.H4("Configuration"),
            html.Label("Analysis", style={"fontWeight": "bold"}),
            dcc.Dropdown(
                id='bar-plot-config-dropdown',
                options=[
                    {'label': 'Cases by Type', 'value': 'cases_by_type'},
                    {'label': 'Cases by Reporting Entity', 'value': 'cases_by_reporting_entity'},
                    {'label': 'Cases by Administrative Level', 'value': 'cases_by_administrative_level'},
                    {'label': 'Cases by Age Group', 'value': 'cases_by_age_group'},
                    {'label': 'Cases by Sex Group', 'value': 'cases_by_sex_group'},
                    # {'label': 'Lag Time Analysis', 'value': 'lag_time_analysis'},
                    # {'label': 'Average Cases per Reporting Entity', 'value': 'average_cases_per_reporting_entity'},
                ],
                value="cases_by_type",
                placeholder="Select a plot configuration",
            ),
            # html.Br(),
            # html.Label("Granularity", style={"fontWeight": "bold"}),
            # dcc.Dropdown(
            #     id="bar-plot-temporal-granularity-dropdown",
            #     options=[
            #         {"label": "Daily", "value": "daily"},
            #         {"label": "Weekly", "value": "weekly"},
            #         {"label": "Monthly", "value": "monthly"},
            #     ],
            #     value="daily",
            # ),
            html.Br(),
            html.Br(),
            html.H4("Filters"),
            html.Label("Date Range", style={"fontWeight": "bold", "width": "100%"}),
            html.Br(),
            dcc.DatePickerRange(
                id="analysis_bar_plot_date",
                start_date=pd.to_datetime("2024-03-01"),
                end_date=pd.to_datetime("2024-04-01"),
                display_format="YYYY-MM-DD",
            ),
            html.Br(),
            html.Br(),
            # choose case type
            html.Label("Case Type", style={"fontWeight": "bold"}),
            dcc.Dropdown(
                id="bar_plot_case_type_filter",
                options=[{"label": ft, "value": ft} for ft in case_types],
                multi=True,
                value=[],
            ),
            html.Br(),
            # choose reporting entity
            html.Label("Reporting Entity", style={"fontWeight": "bold"}),
            dcc.Dropdown(
                id="bar_plot_reporting_entity_filter",
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
            # Add a download button to save the bar-case-reports-store as csv
            # align the button to the right
            dbc.Button("Download as .CSV", id="bar-plot-download-data", color="primary", style={"width": "100%"}),
            dcc.Download(id='bar-plot-download-csv')     
        ]
    )

# callback to download the bar-case-reports-store as csv
@my_app.callback(
    Output('bar-plot-download-csv', 'data'),
    Input("bar-plot-download-data", "n_clicks"),
    State("bar-case-reports-store", "data"),
    prevent_initial_call=True
)
def download_data(n_clicks, case_reports_data):
    filtered_df = pd.read_json(case_reports_data, orient='split')
    return dcc.send_data_frame(filtered_df.to_csv, "case-reports.csv", index=False)

def bar_plot_code():
    return html.Div(
        [
            html.H3("💻 Source Code"),
            html.Br(),
            html.Div(
                [
                    dbc.Button(
                        "View Code",
                        id="analysis_bar_plot_collapse_button",
                        className="mb-3",
                        color="primary",
                        n_clicks=0,
                    ),
                    dbc.Collapse(
                        dcc.Markdown(
                            children=read_file_as_str(
                                "./utils/markdown/analysis/bar_plot_1.md"
                            ),
                            mathjax=True,
                        ),
                        id="analysis_bar_plot_collapse",
                        is_open=False,
                    ),
                ]
            ),
            dbc.Button(
                "Download Code",
                color="success",
                className="me-1",
                id="analysis_bar_plot_download_btn",
            ),
            dcc.Download(id="analysis_bar_plot_download"),
        ]
    )


@my_app.callback(
    Output("analysis_bar_plot_download", "data"),
    Input("analysis_bar_plot_download_btn", "n_clicks"),
    prevent_initial_call=True,
)
def func(n_clicks):
    return dcc.send_file("./utils/download_codes/analysis/bar_plot_code.py")


def bar_plot_info():

    # make the html div hidden
    return (
        bar_plot_content(),
        bar_plot_layout(),
        bar_plot_code()
    )


@my_app.callback(
    Output("analysis_bar_plot_collapse", "is_open"),
    [Input("analysis_bar_plot_collapse_button", "n_clicks")],
    [State("analysis_bar_plot_collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open
