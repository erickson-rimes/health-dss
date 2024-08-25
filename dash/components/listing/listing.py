from dash import html
from dash import Input
from dash import Output
from dash import dcc
import dash_bootstrap_components as dbc
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import json

from maindash import my_app

header_title = "Facilities Listing"

hovertemplate = """
<b>%{hovertext}</b><br>
<br>
<b>Type:</b> %{customdata[0]}<br>
<b>Ownership:</b> %{customdata[1]}<br>
<b>Operating Hours:</b> %{customdata[3]}<br>
<b>Services Offered:</b> <br>%{customdata[2]}<br>
<extra></extra>
"""

#######################################
# Layout
#######################################
def listing_layout():
    layout = html.Div(
        [
            # Map Display Area as the base layer
            html.Div(
                dcc.Graph(id="listing_map_display", style={"height": "100%"}),  # Set map height to fill the viewport
                style={"position": "relative", "width": "80%", "height": "65%"},  # Set the parent div to fill the viewport
            ),
            # Floating left_side()
            html.Div(
                style={
                    "position": "absolute",
                    "top": "0",  # Align to the top of the viewport
                    "right": "0",  # Align to the left of the viewport
                    "height": "100%",  # Full height
                    "width": "20%",  # Adjust the width as necessary
                    "padding": "10px",
                    "background": "rgba(255, 255, 255, 0.8)",  # Semi-transparent background
                    "overflow": "auto",  # Add scroll for overflow content
                    "zIndex": "10",  # Ensure it's above the map
                },
                children=[
                    left_side(),
                ],
            ),
            # Floating right_side() at the bottom
            html.Div(
                id='tab',
                children='Facilities',
                style={'cursor': 'pointer', 'padding': '10px', 'border': '1px solid #ddd', 'max-width': '200px', 'position': 'absolute', 'bottom': '35%', "background": "rgba(255, 255, 255, 1)",}
            ),
            html.Div(
                style={
                    "position": "absolute",
                    "bottom": "0",  # Align to the bottom of the viewport
                    "left": "0",  # Align to the left of the viewport
                    "width": "80%",  # Full width
                    "height": "35%",
                    # "min-height": "24rem",  # Set minimum height to 40rem
                    "overflow": "auto",  # Add scroll for overflow content
                    "padding": "10px",
                    "background": "rgba(255, 255, 255, 1)", 
                    "zIndex": "10",  # Ensure it's above the map
                },
                children=[
                    
                    right_side(),
                ],
            ),
        ],
        style={"position": "relative", "width": "100%", "height": "100vh"}  # Container filling the viewport
    )

    return layout

def get_unique_values(column_name):
    conn = sqlite3.connect("health_facilities.db")
    query = f"SELECT DISTINCT [{column_name}] FROM Facility"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df[column_name].dropna().tolist()


def get_min_max_values(column_name):
    # Connect to the SQLite database
    conn = sqlite3.connect('health_facilities.db')
    cursor = conn.cursor()

    # Query to get the min and max values for the specified column
    query = f"SELECT MIN(`{column_name}`), MAX(`{column_name}`) FROM Facility"
    cursor.execute(query)
    
    # Fetch the result
    result = cursor.fetchone()
    conn.close()

    # Return the min and max values as a dictionary
    return {'min': int(result[0]), 'max': int(result[1])}

def left_side():
    # Fetch unique values from the database for dropdowns and checklists
    facility_types = get_unique_values("Facility Type")
    properties = get_unique_values("Property")
    municipalities = get_unique_values("Municipality")
    administrative_posts = get_unique_values("Postu Administrative")
    sucos = get_unique_values("Suco")
    aldeias = get_unique_values("Aldeia")
    ambulance_range = get_min_max_values("Ambulance")
    maternity_bed_range = get_min_max_values("Maternity bed")
    total_bed_range = get_min_max_values("Total bed")
    operating_days = get_unique_values("Operating Days")
    operating_hours = get_unique_values("Operating Hours")

    # Sorting the options
    facility_types.sort()
    properties.sort()
    municipalities.sort()
    administrative_posts.sort()
    sucos.sort()
    aldeias.sort()
    operating_days.sort()
    operating_hours.sort()

    return html.Div(
        [
            html.Div([html.H3("🏥 Facility Filters")]),
            html.Div(
                [
                    html.Label("Facility Name", style={"fontWeight": "bold"}),
                    dcc.Input(
                        id="facility_name_filter",
                        type="text",
                        placeholder="Enter Facility Name",
                    ),
                    html.Br(),
                    html.Label("Facility Type", style={"fontWeight": "bold"}),
                    dcc.Dropdown(
                        id="facility_type_filter",
                        options=[{"label": ft, "value": ft} for ft in facility_types],
                        value=[],
                        placeholder="Select Facility Type(s)",
                        multi=True,
                    ),
                    html.Br(),
                    html.Label("Property", style={"fontWeight": "bold"}),
                    dcc.Dropdown(
                        id="property_filter",
                        options=[{"label": prop, "value": prop} for prop in properties],
                        value=[],
                        placeholder="Select Property Type(s)",
                        multi=True,
                    ),
                    html.Br(),
                    html.Label("Service Offerings", style={"fontWeight": "bold"}),
                    dcc.Input(
                        id="service_offerings_filter",
                        type="text",
                        placeholder="Enter Service Offering(s)",
                    ),
                    html.Br(),
                    html.Label("Municipality", style={"fontWeight": "bold"}),
                    dcc.Dropdown(
                        id="municipality_filter",
                        options=[{"label": muni, "value": muni} for muni in municipalities],
                        value=[],
                        placeholder="Select Municipality",
                        multi=True,
                    ),
                    html.Br(),
                    html.Label("Administrative Post", style={"fontWeight": "bold"}),
                    dcc.Dropdown(
                        id="administrative_post_filter",
                        options=[{"label": post, "value": post} for post in administrative_posts],
                        value=[],
                        placeholder="Select Administrative Post",
                        multi=True,
                    ),
                    html.Br(),
                    html.Label("Suco", style={"fontWeight": "bold"}),
                    dcc.Dropdown(
                        id="suco_filter",
                        options=[{"label": suco, "value": suco} for suco in sucos],
                        value=[],
                        placeholder="Select Suco",
                        multi=True,
                    ),
                    html.Br(),
                    html.Label("Aldeia", style={"fontWeight": "bold"}),
                    dcc.Dropdown(
                        id="aldeia_filter",
                        options=[{"label": aldeia, "value": aldeia} for aldeia in aldeias],
                        value=[],
                        placeholder="Select Aldeia",
                        multi=True,
                    ),
                    html.Br(),
                    html.Label("Ambulance Availability", style={"fontWeight": "bold"}),
                    dcc.RangeSlider(
                        id="ambulance_filter",
                        min=ambulance_range['min'],
                        max=ambulance_range['max'],
                        # step=5,
                        value=[ambulance_range['min'], ambulance_range['max']],
                        # marks={i: str(i) for i in range(ambulance_range['min'], ambulance_range['max'] + 1, 1)},
                        tooltip={"placement": "bottom", "always_visible": True},
                        allowCross=False
                    ),
                    html.Br(),
                    html.Label("Maternity Bed Count", style={"fontWeight": "bold"}),
                    dcc.RangeSlider(
                        id="maternity_bed_filter",
                        min=maternity_bed_range['min'],
                        max=maternity_bed_range['max'],
                        # step=max(int(maternity_bed_range['max']/10), 1),
                        value=[maternity_bed_range['min'], maternity_bed_range['max']],
                        # marks={i: str(i) for i in range(maternity_bed_range['min'], maternity_bed_range['max'] + 1, 1)},
                        tooltip={"placement": "bottom", "always_visible": True},
                        allowCross=False
                    ),
                    html.Br(),
                    html.Label("Total Bed Count", style={"fontWeight": "bold"}),
                    dcc.RangeSlider(
                        id="total_bed_filter",
                        min=total_bed_range['min'],
                        max=total_bed_range['max'],
                        # step=max(int(total_bed_range['max']/10), 1),
                        value=[total_bed_range['min'], total_bed_range['max']],
                        # marks={i: str(i) for i in range(total_bed_range['min'], total_bed_range['max'] + 1, 1)},
                        tooltip={"placement": "bottom", "always_visible": True},
                        allowCross=False
                    ),
                    html.Br(),
                    html.Label("Operating Days", style={"fontWeight": "bold"}),
                    dcc.Dropdown(
                        id="operating_days_filter",
                        options=[{"label": day, "value": day} for day in operating_days],
                        value=[],
                        placeholder="Select Operating Days",
                        multi=True,
                    ),
                    html.Br(),
                    html.Label("Operating Hours", style={"fontWeight": "bold"}),
                    dcc.Dropdown(
                        id="operating_hours_filter",
                        options=[{"label": hour, "value": hour} for hour in operating_hours],
                        value=[],
                        placeholder="Select Operating Hours",
                        multi=True,
                    ),
                    html.Br(),
                    html.Label("Color By", style={"fontWeight": "bold"}),
                    dcc.Dropdown(
                        id="color_by_configuration",
                        options=[
                            {"label": "Facility Type", "value": "Facility Type"},
                            {"label": "Property", "value": "Property"},
                            {"label": "Municipality", "value": "Municipality"},
                            {"label": "Administrative Post", "value": "Postu Administrative"},
                            {"label": "Ambulance Availability", "value": "Ambulance"}
                        ],
                        value="Facility Type",
                        placeholder="Select Dimension",
                    ),
                ],
                style={"display": "flex", "flexDirection": "column", "padding": "10px"},
            ),
        ]
    )

def right_side():
    return html.Div(
        [
            dcc.Loading(
                id="loading-cards",
                children=[html.Div(id="listing_cards_container")],
                # type="circle",
            )
        ]
    )

def query_facilities(filters):
    con = sqlite3.connect("health_facilities.db")

    # Base query
    base_query = """
    SELECT * FROM Facility
    """

    # Initialize conditions list and parameters list
    conditions = []
    parameters = []

    # Facility Name filter
    if filters.get("facilityName"):
        conditions.append("Facility.`Facility Name` LIKE ?")
        parameters.append(f"%{filters['facilityName']}%")

    # Handling multiple facilityType values
    if filters.get("facilityType"):
        placeholders = ','.join('?' * len(filters["facilityType"]))  # Create placeholders for query
        conditions.append(f"Facility.`Facility Type` IN ({placeholders})")
        parameters.extend(filters["facilityType"])
    
    # Property filter
    if filters.get("property"):
        placeholders = ','.join('?' * len(filters["property"]))  # Create placeholders for query
        conditions.append(f"Facility.Property IN ({placeholders})")
        parameters.extend(filters["property"])
    
    # Municipality filter
    if filters.get("municipality"):
        placeholders = ','.join('?' * len(filters["municipality"]))  # Create placeholders for query
        conditions.append(f"Facility.Municipality IN ({placeholders})")
        parameters.extend(filters["municipality"])
    
    # Administrative Post filter
    if filters.get("administrativePost"):
        placeholders = ','.join('?' * len(filters["administrativePost"]))  # Create placeholders for query
        conditions.append(f"Facility.`Postu Administrative` IN ({placeholders})")
        parameters.extend(filters["administrativePost"])
    
    # Suco filter
    if filters.get("suco"):
        placeholders = ','.join('?' * len(filters["suco"]))  # Create placeholders for query
        conditions.append(f"Facility.Suco IN ({placeholders})")
        parameters.extend(filters["suco"])
    
    # Aldeia filter
    if filters.get("aldeia"):
        placeholders = ','.join('?' * len(filters["aldeia"]))  # Create placeholders for query
        conditions.append(f"Facility.Aldeia IN ({placeholders})")
        parameters.extend(filters["aldeia"])

    # Service Offerings filter
    if filters.get("serviceOfferings"):
        conditions.append("Facility.`Services Offer` LIKE ?")
        parameters.append(f"%{filters['serviceOfferings']}%")

    # Ambulance range filter
    if filters.get("ambulanceRange"):
        min_val, max_val = filters["ambulanceRange"]
        if min_val is not None:
            conditions.append("Facility.Ambulance >= ?")
            parameters.append(min_val)
        if max_val is not None:
            conditions.append("Facility.Ambulance <= ?")
            parameters.append(max_val)

    # Maternity Bed range filter
    if filters.get("maternityBedRange"):
        min_val, max_val = filters["maternityBedRange"]
        if min_val is not None:
            conditions.append("Facility.`Maternity bed` >= ?")
            parameters.append(min_val)
        if max_val is not None:
            conditions.append("Facility.`Maternity bed` <= ?")
            parameters.append(max_val)

    # Total Bed range filter
    if filters.get("totalBedRange"):
        min_val, max_val = filters["totalBedRange"]
        if min_val is not None:
            conditions.append("Facility.`Total bed` >= ?")
            parameters.append(min_val)
        if max_val is not None:
            conditions.append("Facility.`Total bed` <= ?")
            parameters.append(max_val)

    # Operating Days filter
    if filters.get("operatingDays"):
        placeholders = ','.join('?' * len(filters["operatingDays"]))  # Create placeholders for query
        conditions.append(f"Facility.`Operating Days` IN ({placeholders})")
        parameters.extend(filters["operatingDays"])

    # Operating Hours filter
    if filters.get("operatingHours"):
        placeholders = ','.join('?' * len(filters["operatingHours"]))  # Create placeholders for query
        conditions.append(f"Facility.`Operating Hours` IN ({placeholders})")
        parameters.extend(filters["operatingHours"])

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
    [
        Output("listing_cards_container", "children"),
        Output("listing_map_display", "figure"),
    ],
    [
        Input("facility_name_filter", "value"),
        Input("facility_type_filter", "value"),
        Input("property_filter", "value"),
        Input("service_offerings_filter", "value"),
        Input("municipality_filter", "value"),
        Input("administrative_post_filter", "value"),
        Input("suco_filter", "value"),
        Input("aldeia_filter", "value"),
        Input("ambulance_filter", "value"),
        Input("maternity_bed_filter", "value"),
        Input("total_bed_filter", "value"),
        Input("operating_days_filter", "value"),
        Input("operating_hours_filter", "value"),
        Input("color_by_configuration", "value")
    ],
)
def update_facility_content(
    facilityName, facilityType, property, serviceOfferings, municipality, administrativePost, suco, aldeia,
    ambulanceRange, maternityBedRange, totalBedRange, operatingDays, operatingHours, colorConfiguration
):
    filters = {
        "facilityName": facilityName if facilityName else None,
        "facilityType": facilityType if facilityType else None,
        "property": property if property else None,
        "serviceOfferings": serviceOfferings if serviceOfferings else [],
        "municipality": municipality if municipality else None,
        "administrativePost": administrativePost if administrativePost else None,
        "suco": suco if suco else None,
        "aldeia": aldeia if aldeia else None,
        "ambulanceRange": ambulanceRange if ambulanceRange else [None, None],
        "maternityBedRange": maternityBedRange if maternityBedRange else [None, None],
        "totalBedRange": totalBedRange if totalBedRange else [None, None],
        "operatingDays": operatingDays if operatingDays else None,
        "operatingHours": operatingHours if operatingHours else None
    }
    
    filtered_df = query_facilities(filters)
    
    # Format the 'Services Offer' column
    filtered_df['formattedServices'] = filtered_df['Services Offer'].apply(
        lambda x: x.replace('[', '').replace(']', '').replace('\"', '').replace(',', ', ').replace("_", " ").title() if x else "Not available"
    )
    
    # Format the 'Property' column
    filtered_df['formattedProperty'] = filtered_df['Property'].apply(lambda x: x.title() if x else "Unknown")

    # Format the 'Facility Type' column
    filtered_df['formattedFacilityType'] = filtered_df['Facility Type'].apply(lambda x: x.title() if x else "Unknown")

    

    filtered_df['formattedServices_html'] = filtered_df['Services Offer'].apply(
        lambda x: x.replace('\n', '<br>') if x else "Not available"
    )

    if filtered_df.empty:
        # Create a figure with a textual message instead of a map
        fig = go.Figure()
        # Add text in the middle of the figure
        fig.add_trace(go.Scatter(x=[0.5], y=[0.5], text=["No result found for the filter."], mode="text", 
                                textposition="middle center", textfont=dict(size=20)))
        # Remove axis labels and ticks
        fig.update_layout(xaxis=dict(showgrid=False, zeroline=False, visible=False), 
                        yaxis=dict(showgrid=False, zeroline=False, visible=False), 
                        plot_bgcolor="white", 
                        margin=dict(t=0, b=0, l=0, r=0))
    else:
        zoom, (center_lat, center_lon) = get_plotting_zoom_level_and_center_coordinates_from_lonlat(filtered_df['Longitude'], filtered_df['Latitude'])

        fig = px.scatter_mapbox(
            filtered_df,
            lat="Latitude",
            lon="Longitude",
            hover_name="Facility Name",  # Display the facility name when hovering over a point
            custom_data=[
                "formattedFacilityType", 
                "formattedProperty", 
                "formattedServices_html", 
                "Operating Hours"
            ],
            color=colorConfiguration,  # Use the 'Property' column to determine point colors
            # color_discrete_map={  # Optional: Define specific colors for each property type
            #     "Government": "darkgreen",
            #     "Private": "darkblue",
            # },
            zoom=zoom,
            center={"lat": center_lat, "lon": center_lon},
            mapbox_style="open-street-map",
        )
        fig.update_traces(marker=dict(size=8))  # Set a constant marker size
        fig.update_traces(hovertemplate=hovertemplate)
        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), mapbox=dict(
            bearing=0,
            center=dict(
                lat=center_lat,
                lon=center_lon
            ),
            pitch=0,
        ))

    # Extract the color mappings
    color_mapping = {point['name']: point['marker']['color'] for point in fig.data}

    print(color_mapping)

    cards_content = html.Div(
        create_facility_cards(filtered_df, color_mapping, colorConfiguration), style={"display": "flex", "flexWrap": "wrap"}
    )

    return cards_content, fig

def create_facility_cards(df, color_mapping, color_configuration):
    cards = []
    for _, row in df.iterrows():
        # Define background color based on property (ownership)
        header_color = color_mapping.get(row.get(color_configuration, ""), "lightgrey")

        header_style = {"backgroundColor": header_color}

        # if row.get('Services Offer'):
        #     # Deserialize the JSON string into a Python list
        #     retrieved_list = json.loads(row.get('Services Offer'))
        # else:
        #     # If 'Services Offer' is empty or not present, use an empty list
        #     retrieved_list = []

        # Convert the list into a comma-separated string, or use "Not available" if the list is empty
        # services_offered = ', '.join([item.replace('_', ' ').title() for item in retrieved_list]) if retrieved_list else "Not available"
        services_offered = row.get("Services Offer")
        facility_type = row.get('Facility Type', 'Unknown').replace('_', ' ').title()

        card_content = [
            dbc.CardHeader(
                [
                    html.H6(row.get('Facility Name', "Unknown Facility"), className="card-header", style={
                        **header_style,  # Presuming header_style is a dictionary with other styles
                        "display": "-webkit-box",
                        "min-height": "3em",  # Line height * number of lines you want (1.2em * 2 lines here)
                        "overflow": "hidden",
                        "text-overflow": "ellipsis",
                        "-webkit-line-clamp": 2,
                        "-webkit-box-orient": "vertical",
                        "white-space": "normal",  # Ensure text wraps
                    }),
                    # Put a margin on the left of the facility type text
                    html.Span(f"{facility_type}", style={"marginLeft": "12px", 'fontSize': '12px', 'lineHeight': '1.2'}),
                ]
            ),
            dbc.CardBody(
                [
                    html.P([html.Strong("Property: "), row.get('formattedProperty', 'Unknown')]),
                    html.P([html.Strong("Operating Hours: "), row.get('Operating Hours', 'Unknown')]),
                    html.P([html.Strong("Services Offered: "), services_offered]),
                ],
                style={'fontSize': '12px', 'lineHeight': '1.2'}
            ),
        ]
        cards.append(dbc.Card(card_content, style={"width": "16rem", "margin": "8px"}))
    return cards

# @my_app.callback(
#     Output('facility_details', 'children'),
#     [Input('listing_map_display', 'hoverData')]
# )
# def display_hover_data(hoverData):
#     if hoverData is not None:
#         print("Hover data:", hoverData)
#         # Assuming hoverData contains the facility name and other details
#         details = hoverData['points'][0]
#         facility_name = details['hovertext']  # or 'text' depending on how you set it up
#         # Construct the details display. You might need to adjust keys based on your setup.
#         return html.Div([
#             html.H4(facility_name),
#             html.P(f"Type: {details['customdata'][0]}"),
#             html.P(f"Ownership: {details['customdata'][1]}"),
#             # Add more details as needed
#         ])
#     return "Hover over a facility"