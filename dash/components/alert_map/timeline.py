from dash import html
from datetime import datetime

# Example data set of alerts
alerts = [
    {'date': datetime(2022, 3, 1), 'detail': 'Marketing UI design in Figma'},
    {'date': datetime(2022, 4, 1), 'detail': 'E-Commerce UI code in Tailwind CSS'}
]

def timeline_layout():
    return html.Div(
        className='timeline',
        children=[
            html.Ul(
                children=[
                    html.Li(
                        className='event',
                        children=[
                            html.Div(
                                className='event-date',
                                children=alert['date'].strftime('%B %Y')
                            ),
                            html.Div(
                                className='event-details',
                                children=alert['detail']
                            )
                        ]
                    ) for alert in alerts
                ]
            )
        ]
    )


