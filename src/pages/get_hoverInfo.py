import dash
from dash import Input, Output, dcc, html, clientside_callback
import dash_bootstrap_components as dbc
import plotly.express as px
from PIL import Image
# imports for server callback
# from dash.exceptions import PreventUpdate
# import json

dash.register_page(__name__, path="/hover_info")

# open image and create plotly figure
img = Image.open('assets/stars_1.jpg')
fig = px.imshow(
    img=img,
    binary_string=True
)

# update figure layout
fig.update_layout(
    {
        'width': img.width * 0.4,
        'height': img.height * 0.4,
        'xaxis': {'showgrid': False,
                  'showticklabels': False
                  },
        'yaxis': {'showgrid': False,
                  'showticklabels': False
                  },
        'margin': {
            't': 0,
            'b': 0,
            'l': 0,
            'r': 0,
        }
    }
)

layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Graph(
                            id='hover_graph',
                            figure=fig
                        ),
                        html.H6(
                            html.A(
                                'photo credit',
                                href='https://pixabay.com/users/jo_swiss-13562631/',
                                className='text-decoration-none text-primary',
                            )
                        )
                    ],
                    width={'size': 4}
                ),
                dbc.Col(
                    [
                        dbc.Row(
                            dcc.Markdown(
                                """
                                ### What is this about?

                                A clientside callback returns the hoverinfo    
                                when hovering over the image
                                """
                            )
                        ),
                        dbc.Row(
                            [
                                html.H5('Hoverinfo:'),
                                html.Div(id='hover_show')
                            ]
                        )
                    ],
                    width={'size': 8}
                )
            ]
        )
    ],
    fluid=True,
    className='dbc'
)


# layout = dbc.Container([
#     dbc.Row([
#         dbc.Col([
#             dcc.Graph(id='graph', figure=fig),
#         ], width={'size': 10}
#         ),
#         dbc.Col([
#             html.H4('Hoverinfo'),
#             html.Pre(id='hover'),
#         ], width={'size': 2}
#         )
#     ])
# ], fluid=True)


# whenever possible, use clientside callbacks as they are much faster than server callbacks
# these callbacks have to be written in JS whereas the server callbacks can be written in python
clientside_callback(
    """
    function(hoverData) {
        if (hoverData == undefined) {
            throw window.dash_clientside.PreventUpdate;
        } else {
            var jsonstr = JSON.stringify(hoverData, null, 2);
        }
        return [jsonstr];
    }
     """,
    Output('hover_show', 'children'),
    Input('hover_graph', 'hoverData')
)

# serverside callback (python)
# @app.callback(Output('hover', 'children'),
#               Input('graph', 'hoverData'),
#               )
# def get_hover(hoverData):
#     if not hoverData:
#         raise PreventUpdate
#     else:
#         dump_hover = json.dumps(hoverData, indent=2)
#     return dump_hover
