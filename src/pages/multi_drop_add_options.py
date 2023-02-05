import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, html, dcc, ctx, MATCH
import dash

dash.register_page(__name__, path="/multi_drop_options")

# design of the modal
modal = html.Div(
    [
        dbc.Modal(
            [
                dbc.ModalHeader(
                    dbc.ModalTitle("Introduce new option")
                ),
                dbc.ModalBody(
                    dcc.Input(
                        id={'type': 'input', 'index': idx},
                        type='text'
                    )
                ),
                dbc.ModalFooter(
                    children=[
                        dbc.Row(
                            dbc.Col(
                                dbc.ButtonGroup(
                                    [
                                        dbc.Button(
                                            "OK",
                                            id={'type': 'ok', 'index': idx},
                                            className="me-1",
                                            n_clicks=0
                                        ),
                                        dbc.Button(
                                            "Cancel",
                                            id={'type': 'cancel', 'index': idx},
                                            className="me-1",
                                            n_clicks=0
                                        ),
                                    ],
                                )
                            )
                        )
                    ]
                )
            ],
            id={'type': 'modal', 'index': idx},
            is_open=False,
            centered=True
        ) for idx in range(3)
    ],
    className='dbc'
)

layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Dropdown(
                            id={'type': 'drop', 'index': idx},
                            options=[1, 2, 3, 'create new'],
                            multi=True,
                            className=['', 'mt-3'][idx > 0]
                        ) for idx in range(3)
                    ],
                    width=3
                ),
                dbc.Col(
                    dcc.Markdown(
                        """
                        ### What is this about?
                        By selection the drop- down item 'create new' a `dbc.Modal()` pops up.
                        A new drop- down option can be introduced in the `dcc.Input`.   
                        By clicking OK, the new drop- down option is aggregated to the 
                        corresponding drop- down menu.  
                        
                        Pattern matching callbacks are used.
                        """,
                        className='ms-5'
                    ),
                    width=9,
                )
            ]
        ),
        dbc.Row(
            modal
        )
    ],
    fluid=True,
    className='dbc'
)


@callback(
    Output({'type': 'modal', 'index': MATCH}, "is_open"),
    Output({'type': 'drop', 'index': MATCH}, 'options'),
    Output({'type': 'drop', 'index': MATCH}, 'value'),
    Input({'type': 'ok', 'index': MATCH}, "n_clicks"),
    Input({'type': 'cancel', 'index': MATCH}, "n_clicks"),
    Input({'type': 'drop', 'index': MATCH}, "value"),
    State({'type': 'drop', 'index': MATCH}, "options"),
    State({'type': 'input', 'index': MATCH}, 'value'),
    State({'type': 'modal', 'index': MATCH}, "is_open"),
    prevent_initial_call=True
)
def toggle_modal(ok, cancel, drop_value, drop_options, input_value, is_open):
    # which component has triggered the callback?
    trigger = ctx.triggered_id['type']

    # change of drop down value triggered
    if trigger == 'drop':
        if 'create new' in drop_value:
            # if 'create new', open modal
            return not is_open, drop_options, drop_value
        else:
            # if not 'create new', do nothing
            return is_open, drop_options, drop_value

    # ok button has been clicked
    if trigger == 'ok':
        # ok has been clicked, update the drop-down options
        new_options = [opt for opt in drop_options]
        new_options.insert(-1, input_value)
        new_values = [val for val in drop_value if val != 'create new']
        new_values.append(input_value)
        return not is_open, new_options, new_values

    # cancel button has been clicked
    if trigger == 'cancel':
        # cancel has been clicked, do not change options but return already selected to drop down value
        existing_values = [val for val in drop_value if val != 'create new']
        return not is_open, drop_options, existing_values
