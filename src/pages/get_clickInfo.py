import dash
from dash import Input, Output, dcc, html, clientside_callback
import dash_bootstrap_components as dbc
import plotly.express as px
from PIL import Image
# imports for server callback
# from dash.exceptions import PreventUpdate
# import json

dash.register_page(__name__, path="/click_info")

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
                            id='click_graph',
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
                                
                                A clientside callback returns the coordinates when the user clicks
                                on the image
                                """
                            )
                        ),
                        dbc.Row(
                            [
                                html.H5('Coordinates of click:'),
                                html.Div(id='click_show')
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

# whenever possible, use clientside callbacks as they are much faster than server callbacks
# these callbacks have to be written in JS whereas the server callbacks can be written in python
clientside_callback(
    """
    function(clickData) {
        if (clickData == undefined) {
            throw window.dash_clientside.PreventUpdate;
        } else {
            var points = clickData.points[0]
            var x = points.x
            var y = points.y
            //var jsonstr = JSON.stringify(clickData, null, 2);
        }
        return [`x: ${x}, y: ${y}`];
    }
     """,
    Output('click_show', 'children'),
    Input('click_graph', 'clickData')
)

# serverside callback (python)
# @app.callback(Output('click', 'children'),
#               Input('graph', 'clickData')
#               )
# def get_click(clickData):
#     if not clickData:
#         raise PreventUpdate
#     else:
#         points = clickData.get('points')[0]
#         x = points.get('x')
#         y = points.get('y')

#     return f'x: {x}\ny: {y}'
