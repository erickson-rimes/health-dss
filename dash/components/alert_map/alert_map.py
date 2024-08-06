from dash import html
from dash import Input
from dash import Output
from dash import dcc
from dash import State
from dash import no_update
from dash import callback_context
import dash_bootstrap_components as dbc
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from shapely.geometry import Point
from dash.exceptions import PreventUpdate
from . import timeline
from dateutil import parser
from datetime import date

from maindash import my_app

import geopandas as gpd

# gdf = gpd.read_file("../shapefiles/tls_admbndl_admALL_who_ocha_itos_20200911.shp")
gdf_3 = gpd.read_file("../shapefiles/tls_admbnda_adm3_who_ocha_20200911.shp")
gdf_2 = gpd.read_file("../shapefiles/tls_admbnda_adm2_who_ocha_20200911.shp")
gdf_1 = gpd.read_file("../shapefiles/tls_admbnda_adm1_who_ocha_20200911.shp")
gdf_0 = gpd.read_file("../shapefiles/tls_admbnda_adm0_who_ocha_20200911.shp")

# print(gdf_3.columns)
# print(gdf_3.head())


# Ensure the GeoDataFrame is using a coordinate system that matches your alert coordinates (usually WGS84, EPSG:4326)
admin_regions_3 = gdf_3.to_crs(epsg=4326)
admin_regions_2 = gdf_2.to_crs(epsg=4326)
admin_regions_1 = gdf_1.to_crs(epsg=4326)
admin_regions_0 = gdf_0.to_crs(epsg=4326)

# print(admin_regions.columns)

header_title = "Alerts Listing"

color_discrete_map = {"Low": "#00CC96", "Moderate": "#FECB52", "High": "#FFA15A", "Critical": "#EF553B"}

hovertemplate = """
<b>%{hovertext}</b><br>
<br>
<b>Severity:</b> %{customdata[1]}<br>
<b>Administrative Level</b> %{customdata[2]}<br>
<b>Issued on:</b> %{customdata[3]}<br>
<b>Value:</b> %{customdata[4]} %{customdata[5]}<br>
<b>Details:</b> %{customdata[6]}<br>
<extra></extra>
"""

#######################################
# Layout
#######################################
def alert_map_layout():
    layout = html.Div(
        [
            dcc.Store(id="alerts-store"),
            dcc.Store(id='zoom-store', storage_type='session'),
            dcc.Store(id='hover-activity-store', data={'hoverActive': False}),

            # Container for map and side elements
            html.Div(
                className="map-and-side-container",
                children=[
                    # Map Display Area
                    html.Div(
                        dcc.Graph(id='alert_map_display', style={"height": "100%"}),
                        style={"flex": "9",},  # Map takes 60% of space
                    ),

                    # Timeline
                    html.Div(
                        className="timeline",
                        children=[
                            html.Ul(id="timeline-events")  # This is where the timeline will be rendered
                        ],
                        style={"flex": "3", "height": "100%", "overflow": "auto",  "padding-left": "12px", "padding-right": "18px", "padding-top": "12px"},  # Timeline takes 20% of space
                    ),

                    # Floating left_side() for filters
                    html.Div(
                        children=[left_side()],
                        style={"flex": "2", "padding-left": "12px", "padding-right": "12px", "padding-top": "12px"},  # Filter takes 20% of space
                    ),
                ],
                style={
                    "display": "flex",
                    "height": "100%",
                },
            ),
        ],
        style={"position": "relative", "width": "100%", "height": "100vh"}  # Container filling the viewport
    )

    return layout

@my_app.callback(
    Output('timeline-events', 'children'),
    Input('alerts-store', 'data')
)
def update_timeline(store_data):
    # Deserialize the JSON to a DataFrame
    filtered_df = pd.read_json(store_data, orient='split')

    # Ensure the dates are in datetime format
    filtered_df['time'] = pd.to_datetime(filtered_df['time'])

    # Create column "severityTitle" to display the severity as a string
    filtered_df["severityTitle"] = filtered_df["severity"].map({0: "Low", 1: "Moderate", 2: "High", 3: "Critical"})

    # Generate the timeline items from the DataFrame
    timeline_items = [
        html.Li(
            className='event',
            children=[
                html.Div(
                    className='event-date',
                    children=time.strftime('%B %d, %-I:%M %p') if not pd.isnull(time) else ''
                ),
                html.Div([
                    html.H3(
                        className="event-title",
                        children=title),
                    html.Span(severityTitle, style={
                        'background-color': color_discrete_map[severityTitle], # Bootstrap primary color
                        'color': 'white',
                        'border-radius': '12px', # Gives the chip-like rounded corners
                        'padding': '5px 10px', # Adjust padding to control the size of the chip
                        'font-size': '10px', # Adjust font size as needed
                        'margin-left': '10px', # Optional: adds space between the main text and the chip
                    }),
                ], style={'display': 'inline-flex', 'align-items': 'baseline'}),
                html.P(
                    className='event-details',
                    children=f"{round(caseValue)} {caseUnit}. {detail}"
                )
            ]
        ) for title, time, severityTitle, caseValue, caseUnit, detail in zip(filtered_df['alertType'], filtered_df['time'], filtered_df['severityTitle'], filtered_df["caseValue"], filtered_df["caseUnit"], filtered_df['details'])
    ]

    return timeline_items


def left_side():
    return html.Div(
        [
            # html.Div([html.H3("🚨 Alert Filters")]),
            html.Div(
                [
                    html.Label("Alert Type", style={"fontWeight": "bold"}),
                    dcc.Dropdown(
                        id="alert_type_filter",
                        options=[
                            {"label": "Extreme Heat", "value": "Extreme Heat"},
                            {"label": "Extreme Cold", "value": "Extreme Cold"},
                            {"label": "Heat Stroke Cases", "value": "Heat Stroke Cases"},
                            {"label": "Dengue Case", "value": "Dengue Case"},
                            {"label": "Diarrhea Case", "value": "Diarrhea Case"},
                        ],
                        value=[],
                        placeholder="Select Alert Type(s)",
                        multi=True,
                    ),
                    html.Br(),
                    html.Label("Severity", style={"fontWeight": "bold"}),
                    dcc.Dropdown(
                        id="severity_filter",
                        options=[
                            {"label": "Low", "value": 0},
                            {"label": "Moderate", "value": 1},
                            {"label": "High", "value": 2},
                            {"label": "Critical", "value": 3},
                        ],
                        value=[],
                        placeholder="Select Severity Level(s)",
                        multi=True,
                    ),
                    html.Br(),
                    html.Label("Administrative Level", style={"fontWeight": "bold"}),
                    dcc.Dropdown(
                        id="administrative_level_filter",
                        options=[
                            {"label": "Country", "value": 0},
                            {"label": "Municipality", "value": 1},
                            {"label": "Administrative Post", "value": 2},
                            {"label": "Suco", "value": 3},
                        ],
                        value=[],
                        placeholder="Select Administrative Level(s)",
                        multi=True,
                    ),
                    html.Br(),
                    html.Label("Time Range", style={"fontWeight": "bold"}),
                    dcc.DatePickerRange(
                        id="time_range_filter",
                        start_date_placeholder_text="Start Date",
                        end_date_placeholder_text="End Date",
                        start_date=date(2024,5,13),  # Optional: Set an initial start date
                        end_date=date.today(),  # Optional: Set an initial end date
                        min_date_allowed=None,  # Optional: Set the earliest selectable date
                        max_date_allowed=None,  # Optional: Set the latest selectable date
                    ),
                ],
                style={"display": "flex", "flexDirection": "column"},
            ),
        ]
    )


# def right_side():
#     return html.Div(
#         [
#             dcc.Loading(
#                 id="loading-cards",
#                 children=[html.Div(id="alert_cards_container")],
#             )
#         ]
#     )

def query_alerts(filters, offset=0, limit=10):
    con = sqlite3.connect("alerts.db")  # Connect to the alerts database

    # Base query
    base_query = """
    SELECT * FROM alerts
    """

    # Initialize conditions list and parameters list
    conditions = []
    parameters = []

    # Check each filter and add condition and parameter if the filter is not empty
    if filters.get("alertType"):
        placeholders = ','.join('?' * len(filters["alertType"]))  # Create placeholders for query
        conditions.append(f"alertType IN ({placeholders})")
        parameters.extend(filters["alertType"])
    if filters.get("severity"):
        placeholders = ','.join('?' * len(filters["severity"]))  # Create placeholders for query
        conditions.append(f"severity IN ({placeholders})")
        parameters.extend(filters["severity"])
    if filters.get("administrativeLevel"):
        placeholders = ','.join('?' * len(filters["administrativeLevel"]))  # Create placeholders for query
        conditions.append(f"administrativeLevel IN ({placeholders})")
        parameters.extend(filters["administrativeLevel"])
    if "timeRange" in filters and filters["timeRange"] is not None:
        conditions.append("time BETWEEN ? AND ?")
        parameters.extend([filters["timeRange"]["start"], filters["timeRange"]["end"]])

    

    # Construct the final query
    if conditions:
        query = base_query + " WHERE " + " AND ".join(conditions)
    else:
        query = base_query  # No filters applied

    # Executing the query
    df = pd.read_sql_query(query, con, params=parameters)

    con.close()
    return df

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

@my_app.callback(
    Output('alerts-store', 'data'),
    [
        Input("alert_type_filter", "value"),
        Input("severity_filter", "value"),
        Input("administrative_level_filter", "value"),
        Input("time_range_filter", "start_date"),
        Input("time_range_filter", "end_date"),
        # Input("case_value_range_filter", "value"),
    ],
)
def update_alerts_store(alertType, severity, administrativeLevel, start_date, end_date):
    filters = {
        "alertType": alertType,
        "severity": severity,
        "administrativeLevel": administrativeLevel,
        "timeRange": {"start": start_date, "end": end_date} if start_date and end_date else None,
        # "caseValueRange": caseValueRange,
    }
    filtered_df = query_alerts(filters)

    # filtered_df['time'] = pd.to_datetime(filtered_df['time'])


    # Now sort the DataFrame by the 'date' column
    filtered_df = filtered_df.sort_values(by='time', ascending=False)

    # If you need to reset the index after sorting, you can do so with reset_index()
    filtered_df = filtered_df.reset_index(drop=True)
    
    # Consider using orient='split' for efficient serialization and later reconstruction
    return filtered_df.to_json(orient='split')

@my_app.callback(
    Output("alert_map_display", "figure"),
    [
        Input("alerts-store", "data"),
        Input('alert_map_display', 'hoverData'),  # Changed from 'hoverData' to 'hoverData'
    ],
    [
        State('alert_map_display', 'figure'),
        State('zoom-store', 'data'),
    ]
)
def update_map_figure(alerts_data, hoverData, current_figure_state, zoom_state):
    ctx = callback_context

    print("Triggered by: ", ctx.triggered[0]['prop_id'].split('.'))

    if alerts_data:
        filtered_df = pd.read_json(alerts_data, orient='split')
        fig = create_map_figure(filtered_df)
    else:
        fig = go.Figure(current_figure_state)

    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    # Apply updates based on hoverData or other inputs as needed
    if trigger_id == 'alert_map_display' and hoverData:
        # Here, you implement your logic to handle click events.
        # This might include updating the figure based on the clicked data point.
        # For example, you could highlight the clicked region, show custom information, etc.
        # Since you're implementing your own custom hover logic, this part can be adjusted as needed.
        # Example: fig = update_figure_on_click(hoverData, fig, admin_regions)
        print(hoverData.get('points')[0])
        admin_regions = admin_regions_0
        adm_level = hoverData['points'][0]['customdata'][2]
        if adm_level == 1:
            admin_regions = admin_regions_1
        elif adm_level == 2:
            admin_regions = admin_regions_2
        elif adm_level == 3:
            admin_regions = admin_regions_3

        fig = update_map_based_on_hover(hoverData, fig, admin_regions)

    # Apply zoom state if available and alerts_data is not None
    if zoom_state and alerts_data is not None:
        fig.update_layout(mapbox=dict(
            center=zoom_state.get('mapbox.center'),
            zoom=zoom_state.get('mapbox.zoom'),
            bearing=zoom_state.get('mapbox.bearing'),
            pitch=zoom_state.get('mapbox.pitch'),
        ))

    return fig

def update_map_based_on_hover(hoverData, fig, admin_regions):
    # print("hoverData:", hoverData)
    # Check if hoverData is provided and valid
    if hoverData and 'points' in hoverData and len(hoverData['points']) > 0:
        # Extract latitude and longitude from hoverData
        try:
            hover_lat = hoverData['points'][0]['lat']
            hover_lon = hoverData['points'][0]['lon']
        except KeyError:
            return fig
        
        # Create a Point geometry from the hover data
        hover_point = Point(hover_lon, hover_lat)
        
        # Create a temporary GeoDataFrame for the hover point with the same CRS as admin_regions
        hover_point_gdf = gpd.GeoDataFrame([{'geometry': hover_point}], crs=admin_regions.crs)
        
        # Perform spatial join to find which region contains the hover point
        # This assumes admin_regions is a GeoDataFrame with a 'geometry' column of Polygon geometries
        joined = gpd.sjoin(admin_regions, hover_point_gdf, how='inner', op='contains')

        adm3_en_value = None
        adm2_en_value = None
        adm1_en_value = None
        adm0_en_value = None

        if 'ADM3_EN' in joined.columns:
            adm3_en_value = joined['ADM3_EN'].values[0] if not joined.empty else None
        
        if 'ADM2_EN' in joined.columns:
            adm2_en_value = joined['ADM2_EN'].values[0] if not joined.empty else None

        if 'ADM1_EN' in joined.columns:
            adm1_en_value = joined['ADM1_EN'].values[0] if not joined.empty else None

        if 'ADM0_EN' in joined.columns:
            adm0_en_value = joined['ADM0_EN'].values[0] if not joined.empty else None

        print (f"ADM3: {adm3_en_value}, ADM2: {adm2_en_value}, ADM1: {adm1_en_value}, ADM0: {adm0_en_value}")

        # join the adm_en_value in a single string
        # Do not include if value is None
        joined_en_values = ', '.join(filter(None, [adm3_en_value, adm2_en_value, adm1_en_value, adm0_en_value]))

    

        if not joined.empty:
            adm_level = hoverData['points'][0]['customdata'][2]
            column_name = f'ADM{adm_level}_PCODE'

            z_index = gdf_0.index 
            if adm_level == 1:
                z_index = gdf_1.index
            elif adm_level == 2:
                z_index = gdf_2.index
            elif adm_level == 3:
                z_index = gdf_3.index
                
            # Use 'ADM3_PCODE' as a unique identifier for the hovered region
            hovered_region_pcode = joined.iloc[0][column_name]
            
            # Filter the GeoDataFrame for the hovered region using the identified PCode
            hovered_region = admin_regions[admin_regions[column_name] == hovered_region_pcode]

            new_trace = go.Choroplethmapbox(
                geojson=hovered_region.geometry.__geo_interface__,
                locations=hovered_region.index,  # Use 'ADM3_PCODE' for locations
                featureidkey="id",
                z=[1]*len(z_index),  # Simple way to fill the region; adjust as needed
                hoverinfo='none',
                showscale=False,
                marker_opacity=0.5,
                marker_line_width=1,  # Increase line width for highlighting
                marker_line_color='gold',  # Change color to highlight; adjust as needed
            )

            fig.add_annotation(
                text=joined_en_values,  # Text to display
                xref="paper", yref="paper",
                x=0.01, y=0.99,  # Positioning: (0,0) is bottom left, (1,1) is top right
                showarrow=False,
                font=dict(size=14, color="white"),  # White font color
                align="left",
                bgcolor="black",  # Background color (black) to act as border
                bordercolor="black",  # Border color (black)
                borderwidth=2  # Border width
            )


            fig.add_trace(new_trace)

            fig.data = tuple([fig.data[-1]] + list(fig.data[:-1]))

    else:
        # Optional: Handle the case where no point is hovered over
        # This could involve resetting any highlights if applicable
        pass
        
    return fig

def create_map_figure(filtered_df):
    zoom, (center_lat, center_lon) = get_plotting_zoom_level_and_center_coordinates_from_lonlat(filtered_df['longitude'], filtered_df['latitude'])

    # Create column "severityTitle" to display the severity as a string
    filtered_df["severityTitle"] = filtered_df["severity"].map({0: "Low", 1: "Moderate", 2: "High", 3: "Critical"})

    # Get the name of the country, municipality, administrative post, or suco based on the administrative level




    fig = px.scatter_mapbox(
        filtered_df,
        lat="latitude",
        lon="longitude",
        hover_name="alertType",  # Display the alert type when hovering over a point
        color="severityTitle",  # Use the 'severity' column to determine point colors
        hover_data=["alertType", "severityTitle", "administrativeLevel", "time", "caseValue", "caseUnit", "details"],  # Additional data to display when hovering
        color_discrete_map=color_discrete_map,
        zoom=zoom,
        center={"lat": center_lat, "lon": center_lon},
        mapbox_style="open-street-map",
    )
    # Base map with administrative regions
    
    fig.update_traces(marker=dict(size=8))  # Set a constant marker size
    fig.update_traces(hovertemplate=hovertemplate)
    fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), showlegend=False, mapbox=dict(
        bearing=0,
        center=dict(
            lat=center_lat,
            lon=center_lon
        ),
        pitch=0,
    ))

    return fig

# def create_map_figure(filtered_df):
#     zoom, (center_lat, center_lon) = get_plotting_zoom_level_and_center_coordinates_from_lonlat(filtered_df['longitude'], filtered_df['latitude'])

#     # Create column "severityTitle" to display the severity as a string
#     filtered_df["severityTitle"] = filtered_df["severity"].map({0: "Low", 1: "Moderate", 2: "High", 3: "Critical"})

#     icon_map = {
#         'Extreme Heat': '☀',  # Sun symbol
#         'Extreme Cold': '❄',  # Snowflake symbol
#         'Heat Stroke Case': '😓',  # Face with sweat
#         'Dengue Case': '🦟',  # Mosquito (where supported, otherwise consider a simple dot or cross)
#         'Diarrhea Case': '⚕',  # Medical symbol
#     }

#     # Initialize a figure
#     fig = go.Figure()

#     # df_subset = filtered_df[filtered_df['alertType'] == alert_type]
        
#     # Add a scatter mapbox trace for the current alert type
#     fig.add_trace(go.Scattermapbox(
#         lat=filtered_df['latitude'],
#         lon=filtered_df['longitude'],
#         mode='markers+text',  # Use text mode to display icons
#         text=filtered_df['alertType'].map(icon_map),  # Use the mapped icon as the marker text
#         hoverinfo='text',
#         hovertext=filtered_df['alertType'],
#         customdata=filtered_df[["alertType", "severityTitle", "administrativeLevel", "time", "caseValue", "caseUnit", "details"]],
#         hovertemplate=hovertemplate,
#         textfont=dict(
#             # Use the severity color map to set text color based on the severity title
#             # color=filtered_df['severityTitle'].map(color_discrete_map),
#             size=12,
#         ),
#         marker=go.scattermapbox.Marker(size=10, color=filtered_df['severityTitle'].map(color_discrete_map), symbol=len(filtered_df)*["triangle"])
#     ))

#     fig.update_layout(
#         mapbox_style="open-street-map",
#         mapbox_zoom=zoom,
#         mapbox_center={"lat": center_lat, "lon": center_lon},
#         margin=dict(t=0, b=0, l=0, r=0),
#         showlegend=False
#     )

#     return fig


@my_app.callback(
    Output('zoom-store', 'data'),
    Input('alert_map_display', 'relayoutData'),
    State('zoom-store', 'data'),
    prevent_initial_call=True
)
def capture_zoom_state(relayoutData, current_zoom_state):
    if not relayoutData:
        raise PreventUpdate

    # Check for zoom-related properties in relayoutData
    zoom_properties = ['mapbox.center', 'mapbox.zoom', 'mapbox.bearing', 'mapbox.pitch']
    updated_zoom_state = {prop: relayoutData[prop] for prop in zoom_properties if prop in relayoutData}
    
    # Optionally merge with current state to preserve other values
    if current_zoom_state:
        current_zoom_state.update(updated_zoom_state)
        return current_zoom_state
    return updated_zoom_state


# @my_app.callback(
#     Output('alert_cards_container', 'children'),
#     [
#         Input("alerts-store", "data"),
#     ],
# )
# def update_alert_cards(data):
#     # print("Update Alert Cards: ", "exists" if data else "does not exist")

#     if data is None:
#         return "No alerts found for the selected filters."

#     # print("Update alert cards: reconstructing the DataFrame from the stored JSON...")

#     # Reconstruct the DataFrame from the stored JSON
#     filtered_df = pd.read_json(data, orient='split')

#     cards_content = html.Div(
#             create_alert_cards(filtered_df), style={"display": "flex", "flexWrap": "wrap"}
#         )
#     return cards_content


# def create_alert_cards(df):
#     cards = []
#     for _, row in df.iterrows():
#         # Define background color based on severity
#         severity_color = {
#             0: "lightgreen",  # Low
#             1: "yellow",      # Moderate
#             2: "orange",      # High
#             3: "red",         # Critical
#         }.get(row.get("severity", 0), "lightgrey")

#         severity_title = {
#             0: "Low",
#             1: "Moderate",
#             2: "High",
#             3: "Critical",
#         }.get(row.get("severity", 0), "Unknown")
        

#         header_style = {"backgroundColor": severity_color, "color": "black" if row.get("severity", 0) < 3 else "white"}

#         alert_type = row.get('alertType', 'Unknown').replace('_', ' ').title()
#         administrative_level = {
#             0: "Country",
#             1: "Municipality",
#             2: "Administrative Post",
#             3: "Suco",
#         }.get(row.get("administrativeLevel", 0), "Unknown")

#         card_content = [
#             dbc.CardHeader(
#                 html.H5(alert_type, className="card-header", style=header_style)
#             ),
#             dbc.CardBody(
#                 [
#                     html.P([html.Strong("Severity: "), severity_title]),
#                     html.P([html.Strong("Administrative Level: "), administrative_level]),
#                     html.P([html.Strong("Time: "), row.get('time', 'Unknown')]),
#                     html.P([html.Strong("Case Value: "), str(row.get('caseValue', 'N/A')) + " " + str(row.get('caseUnit', ''))]),
#                     html.P([html.Strong("Details: "), row.get('details', 'No details provided.')]),
                    
#                 ]
#             ),
#         ]
#         cards.append(dbc.Card(card_content, style={"width": "18rem", "margin": "10px", "borderColor": severity_color}))
#     return cards
