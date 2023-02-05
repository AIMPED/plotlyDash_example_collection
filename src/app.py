import dash
from dash import html
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
from dash_bootstrap_templates import ThemeSwitchAIO

meta_tags = [{"name": "viewport", "content": "width=device-width, initial-scale=1.0"}]

external_stylesheets = [
    # "https://use.fontawesome.com/releases/v5.10.2/css/all.css",
    dbc.themes.DARKLY,
    dbc.icons.BOOTSTRAP,
    "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.2/dbc.min.css"
]
# url_theme1 = dbc.themes.DARKLY
# template_theme1 = "darkly"
# url_theme2 = dbc.themes.FLATLY
# template_theme2 = "flatly"


app = dash.Dash(
    __name__,
    use_pages=True,
    external_stylesheets=external_stylesheets,
    meta_tags=meta_tags,
    suppress_callback_exceptions=True
)

# server
server = app.server

navbar = dbc.Navbar(
    [
        dbc.NavbarBrand(
            html.A(
                [
                    html.I(
                        className="bi bi-github d-inline",
                        style={'color': 'black', 'height': '50px'}
                    ),
                    html.H6(
                        'AIMPED',
                        style={"margin-left": "10px"},
                        className='d-inline'
                    )
                ],
                href="https://github.com/AIMPED",
                target="_blank",
                className='align-items-center text-decoration-none text-black',
            ),
            className="me-auto",  # me-auto pushes other elements to the right
            style={"margin-left": "10px"},

        ),
        # dbc.NavItem(
        #     ThemeSwitchAIO(
        #         aio_id="theme",
        #         themes=[url_theme1, url_theme2],
        #         icons={"right": "fa fa-moon", "left": "fa fa-sun"}
        #     ),
        #     style={"fontSize": 14, "paddingTop": 7},
        # ),
        dbc.DropdownMenu(
            [
                dbc.DropdownMenuItem(page["name"], href=page["path"])
                for page in dash.page_registry.values() if page['name'] != 'Not found 404'
            ],
            align_end=True,
            label="Menu",
            color='primary',
            style={"margin-left": "15px"},
        ),
    ],
    color="primary",
    style={'height': '50px'},
    className="d-flex align-items-center mb-3"
)

app.layout = html.Div(
    [
        navbar,
        dash.page_container
    ],
)

if __name__ == "__main__":
    app.run(debug=True)
