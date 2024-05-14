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
import re

id_prefix="heatmap456"

# # read the data
# url = "https://raw.githubusercontent.com/mnguyen0226/two_sigma_property_listing/main/data/train.json"
# df = pd.read_json(url)

# create a dict for all the available 2-dimensional plotly graph types
available_plot_types = {
    "line": px.line,
    "heatmap": px.density_mapbox,
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

def get_plotting_zoom_level_and_center_coordinates_from_lonlat(longitudes=None, latitudes=None):
    """Function documentation:\n
    Basic framework adopted from Krichardson under the following thread:
    https://community.plotly.com/t/dynamic-zoom-for-mapbox/32658/7

    # NOTE:
    # THIS IS A TEMPORARY SOLUTION UNTIL THE DASH TEAM IMPLEMENTS DYNAMIC ZOOM
    # in their plotly-functions associated with mapbox, such as go.Densitymapbox() etc.

    Returns the appropriate zoom-level for these plotly-mapbox-graphics along with
    the center coordinate tuple of all provided coordinate tuples.
    """

    # Check whether both latitudes and longitudes have been passed,
    # or if the list lenghts don't match
    if ((latitudes is None or longitudes is None)
            or (len(latitudes) != len(longitudes))):
        # Otherwise, return the default values of 0 zoom and the coordinate origin as center point
        return 0, (0, 0)

    north = latitudes.max()
    south = latitudes.min()
    east = longitudes.max()
    west = longitudes.min()

    center_lat = (north + south) / 2
    center_lon = (east + west) / 2

    # Get the boundary-box 
    b_box = {} 
    b_box['height'] = north-south
    b_box['width'] = east-west
    b_box['center']= (center_lat, center_lon)

    # get the area of the bounding box in order to calculate a zoom-level
    area = b_box['height'] * b_box['width']

    # * 1D-linear interpolation with numpy:
    # - Pass the area as the only x-value and not as a list, in order to return a scalar as well
    # - The x-points "xp" should be in parts in comparable order of magnitude of the given area
    # - The zoom-levels are adapted to the areas, i.e. start with the smallest area possible of 0
    # which leads to the highest possible zoom value 20, and so forth decreasing with increasing areas
    # as these variables are antiproportional
    zoom = np.interp(x=area,
                     xp=[0, 5**-10, 4**-10, 3**-10, 2**-10, 1**-10, 1**-5],
                     fp=[14, 13,    12,     11,     10,     9,      8])

    # Finally, return the zoom level and the associated boundary-box center coordinates
    return zoom, b_box['center']

def heatmap_plot_layout():
    layout = html.Div(
        [
            dcc.Store(id=id_prefix+"heatmap-case-reports-store"),
            dcc.Loading(
                children=[
                    
                    # temporal granularity picker
                    dcc.Graph(id=id_prefix+"heatmap_graph"),
                ],
            )
        ]
    )
    return layout

@my_app.callback(
    Output(component_id=id_prefix+"heatmap-case-reports-store", component_property="data"),
    [
        Input(component_id=id_prefix+"analysis_heatmap_plot_date", component_property="start_date"),
        Input(component_id=id_prefix+"analysis_heatmap_plot_date", component_property="end_date"),
        Input(component_id=id_prefix+"heatmap_plot_case_type_filter", component_property="value"),
        Input(component_id=id_prefix+"heatmap_plot_reporting_entity_filter", component_property="value")
    ]
)
def update_case_reports_store(start_date, end_date, heatmap_plot_case_type_filter, heatmap_plot_reporting_entity_filter):
    filters = {
        "start_date": start_date,
        "end_date": end_date,
        "heatmap_plot_case_type_filter": heatmap_plot_case_type_filter if heatmap_plot_case_type_filter else "",
        "heatmap_plot_reporting_entity_filter": heatmap_plot_reporting_entity_filter if heatmap_plot_reporting_entity_filter else ""
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

    if filters["heatmap_plot_case_type_filter"]:
        conditions.append("caseType IN ({})".format(", ".join(["?"] * len(filters["heatmap_plot_case_type_filter"]))))
        params.extend(filters["heatmap_plot_case_type_filter"])

    if filters["heatmap_plot_reporting_entity_filter"]:
        conditions.append("reportingEntityType IN ({})".format(", ".join(["?"] * len(filters["heatmap_plot_reporting_entity_filter"]))))
        params.extend(filters["heatmap_plot_reporting_entity_filter"])

    if conditions:
        base_query += " WHERE " + " AND ".join(conditions)
    

    query_result = pd.read_sql_query(base_query, con, params=params)
    
    return query_result

@my_app.callback(
    Output(component_id=id_prefix+"heatmap_graph", component_property="figure"),
    [
        Input(component_id=id_prefix+"heatmap-case-reports-store", component_property="data"),
        # Input(component_id=id_prefix+"heatmap-plot-config-dropdown", "value"),
        Input(component_id=id_prefix+"heatmap-plot-temporal-granularity-dropdown", component_property="value"),
        Input(component_id=id_prefix+"heatmap_plot_reporting_entity_filter", component_property="value"),
        Input(component_id=id_prefix+"heatmap_plot_case_type_filter", component_property="value"),
    ],
    [
        State(component_id=id_prefix+"analysis_heatmap_plot_date", component_property="start_date"),
        State(component_id=id_prefix+"analysis_heatmap_plot_date", component_property="end_date"),
    ]
)
def update_graph(
    case_reports_data, 
    # plot_configuration, 
    temporal_granularity, 
    heatmap_plot_reporting_entity_filter, 
    heatmap_plot_case_type_filter, 
    start_date, 
    end_date):
    filtered_df = pd.read_json(case_reports_data, orient='split')

    fig = None

    title = " "
    # append Daily, Weekly, or Monthly to the title
    if temporal_granularity == "daily":
        title = "Daily"
    elif temporal_granularity == "weekly":
        title = "Weekly"
    elif temporal_granularity == "monthly":
        title = "Monthly"

    title += " Cases"

    
    # if plot_configuration == "cases_by_type":
    #     title += "Cases by Type"
    # elif plot_configuration == "cases_by_reporting_entity":
    #     title += "Cases by Reporting Entity"
    # elif plot_configuration == "cases_by_administrative_level":
    #     title += "Cases by Administrative Level"

    # Put the date range in the title in the format YYYY-MM-DD
    start_date_str = pd.to_datetime(start_date).strftime("%Y-%m-%d")
    end_date_str = pd.to_datetime(end_date).strftime("%Y-%m-%d")
    title += f" ({start_date_str} to {end_date_str})"

    # Create a subtitle based from the case type filter
    subtitle = ""
    if heatmap_plot_case_type_filter:
        subtitle = "<br><sub>Case Types: " + ", ".join(heatmap_plot_case_type_filter) + "</sub>" + \
            "<br><sup>Reporting Entities: " + ", ".join(heatmap_plot_reporting_entity_filter) + "</sup>"

    # if plot_configuration == "total_cases_over_time":
    #     fig = total_cases_over_time(filtered_df, temporal_granularity, title, subtitle)
    # elif plot_configuration == "cases_by_type":
    #     fig = cases_by_type(filtered_df, temporal_granularity, title, subtitle)
    # elif plot_configuration == "cases_by_reporting_entity":
    #     fig = cases_by_reporting_entity(filtered_df, temporal_granularity, title, subtitle)
    # elif plot_configuration == "cases_by_administrative_level":
    #     fig = cases_by_administrative_level(filtered_df, temporal_granularity, title, subtitle)
    # elif plot_configuration == "lag_time_analysis":
    #     fig = lag_time_analysis(filtered_df, temporal_granularity, title, subtitle)
    
    # fig.update_layout(title_x=0.5)

    fig = heatmap(filtered_df, temporal_granularity, title, subtitle)

    

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
    df_grouped = filtered_df.groupby(["date", "latitude", "longitude", "date"]).agg({"numberOfCases": "sum"}).reset_index()

    fig = px.line(df_grouped, animation_frame="date", animation_group="numberOfCases",  color_continuous_scale=px.colors.sequential.OrRd, height=800, title=f"<b>{title}</b>{subtitle}", labels={"date": "Reporting Date", "numberOfCases": "Number of Cases"})

    return fig

def heatmap(filtered_df, temporal_granularity, title, subtitle):
    create_date_columns(filtered_df, temporal_granularity)
    zoom, (center_lat, center_lon) = get_plotting_zoom_level_and_center_coordinates_from_lonlat(filtered_df['longitude'], filtered_df['latitude'])

    # group by case type and sum up the number of cases
    df_grouped = filtered_df.groupby(["date", "latitude", "longitude"]).agg({"numberOfCases": "sum"}).reset_index()

    print("filtered_df columns: ")
    print(filtered_df.columns)

    print("df_grouped columns: ")
    print(df_grouped.columns)

    # create a heatmap plot grouped by case type
    fig = px.density_mapbox(
        df_grouped,  
        range_color=[df_grouped["numberOfCases"].min(), 
                     df_grouped["numberOfCases"].max()], 
        animation_frame="date", 
        animation_group="numberOfCases",  
        color_continuous_scale=px.colors.sequential.OrRd, 
        height=800, 
        lat="latitude", 
        lon="longitude", 
        z="numberOfCases", 
        title=f"<b>{title}</b>{subtitle}", 
        zoom=zoom,
        center={"lat": center_lat, "lon": center_lon},
        mapbox_style="open-street-map", 
        # mapbox_style="carto-positron",
        labels={"numberOfCases": "Number of Cases", "caseType": "Case Type"}
        )
    
    return fig


# b. Cases by Type Over Time
# X-axis: Time (fromDateTime or reportingDate)
# Y-axis: Number of cases, segmented by caseType (e.g., Heat Stroke, Dengue Case, Diarrhea Case)
# Purpose: Compare trends across different types of cases to identify patterns or outbreaks.
def cases_by_type(filtered_df, temporal_granularity, title, subtitle):
    # create date columns based on the value of temporal granularity
    create_date_columns(filtered_df, temporal_granularity)
    zoom, (center_lat, center_lon) = get_plotting_zoom_level_and_center_coordinates_from_lonlat(filtered_df['longitude'], filtered_df['latitude'])

    # group by case type and sum up the number of cases
    df_grouped = filtered_df.groupby(["date", "latitude", "longitude", "caseType"]).agg({"numberOfCases": "sum"}).reset_index()

    print("filtered_df columns: ")
    print(filtered_df.columns)

    print("df_grouped columns: ")
    print(df_grouped.columns)

    # create a heatmap plot grouped by case type
    fig = px.density_mapbox(df_grouped,  range_color=[df_grouped["numberOfCases"].min(), df_grouped["numberOfCases"].max()], animation_frame="date", animation_group="numberOfCases",  color_continuous_scale=px.colors.sequential.OrRd, height=800, lat="latitude", lon="longitude", z="numberOfCases", title=f"<b>{title}</b>{subtitle}", zoom=zoom,
        center={"lat": center_lat, "lon": center_lon},
        mapbox_style="open-street-map", labels={"numberOfCases": "Number of Cases", "caseType": "Case Type"})

    return fig


# # d. Reporting Entity Trends
# X-axis: Time (fromDateTime or reportingDate)
# Y-axis: Number of reports, segmented by reportingEntityType (e.g., Individual, Health Facility, Automated System)
# Purpose: Understand the reporting behavior and possibly the reliability or focus of different reporting entities.
# create subplots for each caseType
def cases_by_reporting_entity(filtered_df, temporal_granularity, title, subtitle):
    # create date columns based on the value of temporal granularity
    create_date_columns(filtered_df, temporal_granularity)
    zoom, (center_lat, center_lon) = get_plotting_zoom_level_and_center_coordinates_from_lonlat(filtered_df['longitude'], filtered_df['latitude'])

    # group by reporting entity type and sum up the number of cases
    df_grouped = filtered_df.groupby(["date", "latitude", "longitude", "caseType", "reportingEntityType"]).agg({"numberOfCases": "sum"}).reset_index()

    # create a heatmap plot grouped by reporting entity type
    fig = px.density_mapbox(df_grouped,  range_color=[df_grouped["numberOfCases"].min(), df_grouped["numberOfCases"].max()], animation_frame="date", animation_group="numberOfCases",  color_continuous_scale=px.colors.sequential.OrRd, height=800, lat="latitude", lon="longitude", z="numberOfCases", category_orders={"caseType": ["Heat Stroke", "Dengue Case", "Diarrhea Case"]}, title=f"<b>{title}</b>{subtitle}", zoom=zoom, center={"lat": center_lat, "lon": center_lon},
        mapbox_style="open-street-map", labels={"numberOfCases": "Number of Cases", "reportingEntityType": "Reporting Entity Type", "caseType": "Case Type"})

    # fig.update_layout(heatmapmode="group")

    return fig

# e. Cases by Administrative Level Over Time
# X-axis: Time (fromDateTime or reportingDate)
# Y-axis: Number of cases, segmented by administrativeLevel (e.g., Country, State, District, City)
# Purpose: Observe how case trends differ across various administrative levels, which could indicate localized outbreaks or spread.
def cases_by_administrative_level(filtered_df, temporal_granularity, title, subtitle):
    # create date columns based on the value of temporal granularity
    create_date_columns(filtered_df, temporal_granularity)
    zoom, (center_lat, center_lon) = get_plotting_zoom_level_and_center_coordinates_from_lonlat(filtered_df['longitude'], filtered_df['latitude'])

    filtered_df["administrativeLevelText"] = filtered_df["administrativeLevel"].map({0: "Country", 1: "State", 2: "District", 3: "City"})

    df_grouped = filtered_df.groupby(["date", "latitude", "longitude", "caseType", "administrativeLevelText"]).agg({"numberOfCases": "sum"}).reset_index()

    # create a heatmap plot grouped by reporting entity type
    fig = px.density_mapbox(df_grouped,  range_color=[df_grouped["numberOfCases"].min(), df_grouped["numberOfCases"].max()], animation_frame="date", animation_group="numberOfCases",  color_continuous_scale=px.colors.sequential.OrRd, height=800, lat="latitude", lon="longitude", z="numberOfCases", category_orders={"caseType": ["Heat Stroke", "Dengue Case", "Diarrhea Case"]}, title=f"<b>{title}</b>{subtitle}", zoom=zoom, center={"lat": center_lat, "lon": center_lon},
        mapbox_style="open-street-map", labels={"numberOfCases": "Number of Cases", "administrativeLevelText": "Reporting Entity Type", "caseType": "Case Type"})

    # fig.update_layout(heatmapmode="group")

    return fig

# g. Lag Time Analysis
# X-axis: Time (reportingDate)
# Y-axis: Time lag (difference between reportingDate and fromDateTime or toDateTime)
# Purpose: Understand delays in reporting, which can be critical for real-time public health responses.
# def lag_time_analysis(filtered_df, temporal_granularity, title, subtitle):
#     # create new date columns
#     filtered_df["reportingDate"] = pd.to_datetime(filtered_df["reportingDate"])
#     filtered_df["fromDateTime"] = pd.to_datetime(filtered_df["fromDateTime"])

#     filtered_df["lagTime"] = (filtered_df["reportingDate"] - filtered_df["fromDateTime"]).dt.days

#     fig = px.scatter(filtered_df, title=f"<b>{title}</b>{subtitle}", labels={"reportingDate": "Reporting Date", "lagTime": "Lag Time (Days)"})

#     return fig

def heatmap_plot_content():
    return html.Div(
        [
            html.Div([html.H3("Heatmap Plot")]),
            html.Div(
                [
                    html.P(
                        "A heat map (or heatmap) is a 2-dimensional data visualization technique that represents the magnitude of individual values within a dataset as a color."
                    )
                ]
            ),
            html.Br(),
            html.H4("Configuration"),
            # html.Label("Analysis", style={"fontWeight": "bold"}),
            # dcc.Dropdown(
            #     id=id_prefix+'heatmap-plot-config-dropdown',
            #     options=[
            #         {'label': 'Cases by Type', 'value': 'cases_by_type'},
            #         {'label': 'Cases by Reporting Entity', 'value': 'cases_by_reporting_entity'},
            #         {'label': 'Cases by Administrative Level', 'value': 'cases_by_administrative_level'},
            #         # {'label': 'Lag Time Analysis', 'value': 'lag_time_analysis'},
            #         # {'label': 'Average Cases per Reporting Entity', 'value': 'average_cases_per_reporting_entity'},
            #     ],
            #     value="cases_by_type",
            #     placeholder="Select a plot configuration",
            # ),
            # html.Br(),
            html.Label("Granularity", style={"fontWeight": "bold"}),
            dcc.Dropdown(
                id=id_prefix+"heatmap-plot-temporal-granularity-dropdown",
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
                id=id_prefix+"analysis_heatmap_plot_date",
                start_date=pd.to_datetime("2024-03-01"),
                end_date=pd.to_datetime("2024-04-01"),
                display_format="YYYY-MM-DD",
            ),
            html.Br(),
            html.Br(),
            # choose case type
            html.Label("Case Type", style={"fontWeight": "bold"}),
            dcc.Dropdown(
                id=id_prefix+"heatmap_plot_case_type_filter",
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
                id=id_prefix+"heatmap_plot_reporting_entity_filter",
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
            # Add a download button to save the heatmap-case-reports-store as csv
            # align the button to the right
            dbc.Button("Download as .CSV", id=id_prefix+"heatmap-plot-download-data", color="primary", style={"width": "100%"}),
            dcc.Download(id=id_prefix+'heatmap-plot-download-csv')     
        ]
    )

# callback to download the heatmap-case-reports-store as csv
@my_app.callback(
    Output(component_id=id_prefix+'heatmap-plot-download-csv', component_property='data'),
    Input(component_id=id_prefix+"heatmap-plot-download-data", component_property="n_clicks"),
    State(component_id=id_prefix+"heatmap-case-reports-store", component_property="data"),
    prevent_initial_call=True
)
def download_data(n_clicks, case_reports_data):
    filtered_df = pd.read_json(case_reports_data, orient='split')
    return dcc.send_data_frame(filtered_df.to_csv, "case-reports.csv", index=False)

def heatmap_plot_code():
    return html.Div(
        [
            html.H3("💻 Source Code"),
            html.Br(),
            html.Div(
                [
                    dbc.Button(
                        "View Code",
                        id=id_prefix+"analysis_heatmap_plot_collapse_button",
                        className="mb-3",
                        color="primary",
                        n_clicks=0,
                    ),
                    dbc.Collapse(
                        dcc.Markdown(
                            children=read_file_as_str(
                                "./utils/markdown/analysis/heatmap.md"
                            ),
                            mathjax=True,
                        ),
                        id=id_prefix+"analysis_heatmap_plot_collapse",
                        is_open=False,
                    ),
                ]
            ),
            dbc.Button(
                "Download Code",
                color="success",
                className="me-1",
                id=id_prefix+"analysis_heatmap_plot_download_btn",
            ),
            dcc.Download(id=id_prefix+"analysis_heatmap_plot_download"),
        ]
    )


@my_app.callback(
    Output(component_id=id_prefix+"analysis_heatmap_plot_download", component_property="data"),
    Input(component_id=id_prefix+"analysis_heatmap_plot_download_btn", component_property="n_clicks"),
    prevent_initial_call=True,
)
def func(n_clicks):
    return dcc.send_file("./utils/download_codes/analysis/heatmap_plot_code.py")


def heatmap_plot_info():

    # make the html div hidden
    return (
        heatmap_plot_content(),
        heatmap_plot_layout(),
        heatmap_plot_code()
    )


@my_app.callback(
    Output(component_id=id_prefix+"analysis_heatmap_plot_collapse", component_property="is_open"),
    [Input(component_id=id_prefix+"analysis_heatmap_plot_collapse_button", component_property="n_clicks")],
    [State(component_id=id_prefix+"analysis_heatmap_plot_collapse", component_property="is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open
