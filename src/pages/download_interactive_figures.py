import dash
from dash import Input, Output, callback, State, dcc, html
from dash_bootstrap_templates import load_figure_template
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import numpy as np
import zipfile
import io

dash.register_page(__name__, path="/download_figures")

layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Row(
                            dcc.Graph(
                                id='int_fig_graph1',
                                figure=go.Figure(
                                    data=go.Scatter(
                                        x=np.random.randint(0, 10, 100),
                                        y=np.random.randint(0, 10, 100),
                                        marker={'color': 'crimson'},
                                        mode='markers',
                                        name='fig1',
                                    ),
                                    layout={
                                        'template': load_figure_template("darkly"),
                                        'height': 400,
                                        'width': 600,
                                        'title': {'text': 'Graph 1'}
                                    }
                                )
                            ),
                        ),
                        dbc.Row(
                            dcc.Graph(
                                id='int_fig_graph2',
                                figure=go.Figure(
                                    data=go.Scatter(
                                        x=np.random.randint(0, 10, 100),
                                        y=np.random.randint(0, 10, 100),
                                        marker={'color': 'gold'},
                                        mode='markers',
                                        name='fig2'
                                    ),
                                    layout={
                                        'template': load_figure_template("darkly"),
                                        'height': 400,
                                        'width': 600,
                                        'title': {'text': 'Graph 2'}
                                    }
                                )
                            ),
                        )
                    ],
                    width=4,
                    align='center',
                ),
                dbc.Col(
                    [
                        dbc.Row(
                            [
                                dcc.Download(id='int_fig_down'),
                                html.Br(),
                                dcc.Markdown(
                                    """
                                    ### What is this about?
                                    Select the figures to download via the drop-down, then press the download button. 

                                    Internally, the drop- down selection is compared to  the 
                                    `name` argument of the `go.Scatter()`. If matched, the figure is added to a 
                                    zip archive and then downloaded. 
                                    """,
                                )
                            ],
                        ),
                        dbc.Row(
                            [
                                dcc.Dropdown(
                                    id='int_fig_drop',
                                    options=[
                                        {'label': 'Graph 1', 'value': 'fig1'},
                                        {'label': 'Graph 2', 'value': 'fig2'}
                                    ],
                                    multi=True,
                                    style={'width': '250px'},
                                ),
                                dbc.Button(
                                    id='int_fig_btn',
                                    children=html.Div('Download selection', className='text-center'),
                                    style={'width': '250px'},
                                    className='ms-5'
                                ),
                            ],
                            align='start',
                            className='mt-5'
                        ),
                    ],
                    width=8,
                    align='start'
                )
            ]
        )
    ],
    fluid=True,
    className="dbc"
)


@callback(
    Output('int_fig_down', 'data'),
    Input('int_fig_btn', 'n_clicks'),
    State('int_fig_drop', 'value'),
    State('int_fig_graph1', 'figure'),
    State('int_fig_graph2', 'figure'),
    prevent_initial_call=True
)
# adapted from: https://stackoverflow.com/questions/67917360/plotly-dash-download-bytes-stream/67918580#67918580
def func(_, selection, *figures):
    to_download = check_state(selection, figures)

    def write_archive(bytes_io):
        with zipfile.ZipFile(bytes_io, mode="w") as zf:
            for idx, fig in enumerate(to_download):
                go_fig = go.Figure(fig)
                buf = io.StringIO()
                go_fig.write_html(buf)
                img_name = f'fig_{idx}.html'
                zf.writestr(img_name, buf.getvalue())

    return dcc.send_bytes(write_archive, "app_download.zip")


def check_state(selection, figures):
    return [fig for fig in figures if extract_name(fig) in selection]


def extract_name(figure):
    return figure.get('data', [])[0].get('name')
