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
<b>Accreditation:</b> %{customdata[2]}<br>
<b>Services Offered:</b> %{customdata[3]}<br>
<b>Operating Hours:</b> %{customdata[4]}<br>
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



def left_side():
    return html.Div(
        [
            html.Div([html.H3("🏥 Facility Filters")]),
            html.Div(
                [
                    html.Label("Facility Type", style={"fontWeight": "bold"}),
                    dcc.Dropdown(
                        id="facility_type_filter",
                        options=[
                            {"label": "Hospital", "value": "hospital"},
                            {"label": "Clinic", "value": "clinic"},
                            {"label": "Specialized Hospital", "value": "specialized_hospital"},
                            {"label": "Primary Care Clinic", "value": "primary_care_clinic"},
                            {"label": "Diagnostic Lab", "value": "diagnostic_lab"},
                            {"label": "Other", "value": "other"},
                        ],
                        value=[],  # Use an empty list as the default value for multiple selections
                        placeholder="Select Facility Type(s)",
                        multi=True,
                    ),
                    html.Br(),
                    html.Label("Ownership", style={"fontWeight": "bold"}),
                    dcc.Dropdown(
                        id="ownership_filter",
                        options=[
                            {"label": "Government", "value": "government"},
                            {"label": "Private", "value": "private"},
                            {"label": "Non-profit", "value": "non_profit"},
                            {"label": "Public-private Partnership", "value": "public_private_partnership"},
                        ],
                        value=[],
                        placeholder="Select Ownership Type(s)",
                        multi=True,
                    ),
                    html.Br(),
                    html.Label("Accreditation Status", style={"fontWeight": "bold"}),
                    dcc.RadioItems(
                        id="accreditation_status_filter",
                        options=[
                            {"label": "Accredited", "value": True},
                            {"label": "Not Accredited", "value": False},
                        ],
                        value="",
                    ),
                    html.Br(),
                    html.Label("Service Offerings", style={"fontWeight": "bold"}),
                    dcc.Checklist(
                        id="service_offerings_filter",
                        options=[
                            {"label": "Emergency Services", "value": "emergency_services"},
                            {"label": "Outpatient Services", "value": "outpatient_services"},
                            {"label": "Surgical Services", "value": "surgical_services"},
                            {"label": "Diagnostic Services", "value": "diagnostic_services"},
                            {"label": "Other", "value": "other"},
                        ],
                        value=[],
                    ),
                    html.Br(),
                    html.Label("Municipality", style={"fontWeight": "bold"}),
                    dcc.Input(
                        id="municipality_filter",
                        type="text",
                        placeholder="Enter Municipality",
                    ),
                    html.Br(),
                    html.Label("Sub-District", style={"fontWeight": "bold"}),
                    dcc.Input(
                        id="sub_district_filter",
                        type="text",
                        placeholder="Enter Sub-District",
                    ),
                    html.Br(),
                    html.Label("Village", style={"fontWeight": "bold"}),
                    dcc.Input(
                        id="village_filter",
                        type="text",
                        placeholder="Enter Village",
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
    con = sqlite3.connect("facilities.db")

    # Base query
    base_query = """
    SELECT Facility.*, Address.* FROM Facility
    INNER JOIN Address ON Facility.addressId = Address.id
    """

    # Initialize conditions list and parameters list
    conditions = []
    parameters = []

    # Check each filter and add condition and parameter if the filter is not empty
    # Handling multiple facilityType values
    if filters.get("facilityType"):
        placeholders = ','.join('?' * len(filters["facilityType"]))  # Create placeholders for query
        conditions.append(f"Facility.facilityType IN ({placeholders})")
        parameters.extend(filters["facilityType"])
    if filters.get("ownership"):
        placeholders = ','.join('?' * len(filters["ownership"]))  # Create placeholders for query
        conditions.append(f"Facility.ownership IN ({placeholders})")
        parameters.extend(filters["ownership"])
    if "accreditationStatus" in filters and filters["accreditationStatus"] is not None:  # Assuming True or False
        conditions.append("Facility.accreditationStatus = ?")
        parameters.append(filters["accreditationStatus"])
    if filters.get("municipality"):
        conditions.append("Address.municipality = ?")
        parameters.append(filters["municipality"])
    if filters.get("subDistrict"):
        conditions.append("Address.subDistrict = ?")
        parameters.append(filters["subDistrict"])
    if filters.get("village"):
        conditions.append("Address.village = ?")
        parameters.append(filters["village"])
    
    # Handling service offerings as a special case
    if filters.get("serviceOfferings"):
        for service in filters["serviceOfferings"]:
            conditions.append("Facility.serviceOfferings LIKE ?")
            parameters.append(f"%{service}%")

    # Construct the final query
    if conditions:
        query = base_query + " WHERE " + " AND ".join(conditions)
    else:
        query = base_query  # No filters applied

    print("Query:", query)
    print("Parameters:", parameters)
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
        Input("facility_type_filter", "value"),
        Input("ownership_filter", "value"),
        Input("accreditation_status_filter", "value"),
        Input("service_offerings_filter", "value"),
        Input("municipality_filter", "value"),
        Input("sub_district_filter", "value"),
        Input("village_filter", "value"),
        # Assuming you have inputs for each of these filters in your Dash app
    ],
)
def update_facility_content(facilityType, ownership, accreditationStatus, serviceOfferings, municipality, subDistrict, village):
    filters = {
        "facilityType": facilityType if facilityType else None,
        "ownership": ownership if ownership else None,
        "accreditationStatus": accreditationStatus if accreditationStatus else None,
        "serviceOfferings": serviceOfferings if serviceOfferings else [],
        "municipality": municipality if municipality else None,
        "subDistrict": subDistrict if subDistrict else None,
        "village": village if village else None,
    }
    print("Filters:", filters)
    filtered_df = query_facilities(filters)
    print(filtered_df.columns)

    filtered_df['formattedServices'] = filtered_df['serviceOfferings'].apply(
    lambda x: x.replace('[', '').replace(']', '').replace('\"', '').replace(',', ', ').replace("_", " ").title() if x else "Not available")
    
    # format the ownership column
    filtered_df['formattedOwnership'] = filtered_df['ownership'].apply(lambda x: x.replace('_', ' ').title() if x else "Unknown")

    # format the facility type column
    filtered_df['formattedFacilityType'] = filtered_df['facilityType'].apply(lambda x: x.replace('_', ' ').title() if x else "Unknown")

    # tranform accreditationStatus value of 0 or 1 to Yes or No
    filtered_df['formattedAccreditationStatus'] = filtered_df['accreditationStatus'].apply(lambda x: "Yes" if x else "No")

    cards_content = html.Div(
        create_facility_cards(filtered_df), style={"display": "flex", "flexWrap": "wrap"}
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
        zoom, (center_lat, center_lon) = get_plotting_zoom_level_and_center_coordinates_from_lonlat(filtered_df['longitude'], filtered_df['latitude'])
        print("zoom:", zoom)

        fig = px.scatter_mapbox(
            filtered_df,
            lat="latitude",
            lon="longitude",
            hover_name="facilityName",  # Display the facility name when hovering over a point
            # hover_data=["facilityType", "ownership"],  # Additional data to show on hover
            custom_data=[
                "formattedFacilityType", 
                "formattedOwnership", 
                "formattedAccreditationStatus", 
                "formattedServices", 
                "operatingHours"
            ],
            color="ownership",  # Use the 'ownership' column to determine point colors
            color_discrete_map={  # Optional: Define specific colors for each ownership type
                "government": "darkgreen",
                "private": "darkblue",
                "non_profit": "red",
                "public_private_partnership": "grey"
            },
            zoom=zoom,
            center={"lat": center_lat, "lon": center_lon},
            mapbox_style="open-street-map",
        )
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

    return cards_content, fig

def create_facility_cards(df):
    cards = []
    for _, row in df.iterrows():
        # Define background color based on ownership
        header_color = {
            "government": "lightgreen",
            "private": "lightblue",
            "non_profit": "salmon",
            "public_private_partnership": "lightgrey",
        }.get(row.get("ownership", ""), "lightgrey")

        header_style = {"backgroundColor": header_color}

        if row.get('serviceOfferings'):
            # Deserialize the JSON string into a Python list
            retrieved_list = json.loads(row.get('serviceOfferings'))
        else:
            # If 'serviceOfferings' is empty or not present, use an empty list
            retrieved_list = []

        # Convert the list into a comma-separated string, or use "Not available" if the list is empty
        services_offered = ', '.join([item.replace('_', ' ').title() for item in retrieved_list]) if retrieved_list else "Not available"
        facility_type = row.get('facilityType', 'Unknown').replace('_', ' ').title()

        card_content = [
            dbc.CardHeader(
                [
                    html.H6(row.get('facilityName', "Unknown Facility"), className="card-header", style={
                        **header_style,  # Presuming header_style is a dictionary with other styles
                        "display": "-webkit-box",
                        # "line-height": "1.2",  # Adjust based on your font size to fit two lines
                        "min-height": "3em",  # Line height * number of lines you want (1.2em * 2 lines here)
                        "overflow": "hidden",
                        "text-overflow": "ellipsis",
                        "-webkit-line-clamp": 2,
                        "-webkit-box-orient": "vertical",
                        "white-space": "normal",  # Ensure text wraps
                    }),
                    # Put a margin of 16px on top of the type text
                    html.Span(f"{facility_type}", style={"marginLeft": "12px", 'fontSize': '12px', 'lineHeight': '1.2'}),
                ]
            ),
            dbc.CardBody(
                [
                    html.P([html.Strong("Ownership: "), row.get('formattedOwnership', 'Unknown')]),
                    html.P([html.Strong("Accreditation: "), row.get('formattedAccreditation', 'No')]),
                    html.P([html.Strong("Operating Hours: "), row.get('operatingHours', 'Unknown')]),
                    html.P([html.Strong("Emergency Services: "), "Yes" if row.get('emergencyServices', False) else "No"]),
                    html.P([html.Strong("Technology Integration: "), "Yes" if row.get('technologyIntegration', False) else "No"]),
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