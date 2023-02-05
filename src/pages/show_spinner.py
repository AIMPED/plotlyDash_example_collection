import dash
from dash import html, dcc, Input, Output, callback
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import time

dash.register_page(__name__, path="/spinner")

layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    dbc.Row(
                        dcc.Markdown(
                            """
                        ### What is this about?
                        This page of the app shows how to use a dbc.Spinner() component.
                        
                        The Spinner is shown for the children of the `dbc.Spinner()`,
                        in this case the component with the `id=spin_out`
                        
                        Instead of a `dbc.Spinner()` you could use a `dcc.Loading()` or
                        `dcc.Spinner()` component.
                        """
                        )
                    )
                ),
                dbc.Row(
                    dbc.Col(
                        dbc.Button(
                            'Click this button to show the spinner',
                            id='spin_btn'
                        ),
                    )
                ),
                dbc.Row(
                    dbc.Col(
                        dbc.Spinner(
                            id='spinner_1',
                            type='border',
                            color='rgb(181,137,0)',
                            spinner_style={'width': '8rem', 'height': '8rem'},
                            fullscreen=True,
                            fullscreen_style={'backgroundColor': 'rgba(0,0,0,0.4)'},
                            # the children ID defines the action for which the spinner is shown
                            # in this case it is the dummy output
                            children=html.Div(
                                id='spin_out',
                                className='pt-3'
                            )
                        )
                    )
                )
            ]
        ),

    ],
    fluid=True,
)


@callback(
    Output('spin_out', 'children'),
    Input('spin_btn', 'n_clicks'),
    prevent_initial_call=True
)
def update_output(click):
    if not click:
        raise PreventUpdate
    else:
        time.sleep(2)
        return dcc.Markdown(
            """
            Notice, that the page was blocked while the spinner was shown.  
             
           The spinner was shown for 2 seconds because I used  
           a timer of 2 seconds to simulate a callback which takes some time.
            """
        )
