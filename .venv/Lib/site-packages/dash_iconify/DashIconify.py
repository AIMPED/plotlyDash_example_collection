# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class DashIconify(Component):
    """A DashIconify component.
Iconify for Plotly Dash. Visit this site to browse all the available icons: https://icon-sets.iconify.design/

Keyword arguments:

- id (string; optional):
    The ID used to identify this component in Dash callbacks.

- className (string; optional):
    Often used with CSS to style elements with common properties.

- color (string; optional):
    Color.

- flip (a value equal to: "horizontal", "vertical"; optional):
    Flip the icon horizontally or vertically.

- height (number; optional):
    Icon height.

- icon (string; required):
    Icon name is a string, which has 3 parts: @api-provider :
    icon-prefix : icon-name provider points to API source. Starts with
    \"@\", can be empty (empty value is used for public Iconify API).
    prefix is name of icon set. name is name of icon.

- inline (boolean; optional):
    Toggles inline or block mode.

- rotate (a value equal to: 0, 1, 2, 3; optional):
    Rotates icon, 0: 0 deg, 1: 90 deg, 2: 180 deg, 3: 270 deg.

- style (dict; optional):
    Inline style.

- width (number; optional):
    Icon width."""
    @_explicitize_args
    def __init__(self, className=Component.UNDEFINED, color=Component.UNDEFINED, flip=Component.UNDEFINED, height=Component.UNDEFINED, icon=Component.REQUIRED, id=Component.UNDEFINED, inline=Component.UNDEFINED, rotate=Component.UNDEFINED, style=Component.UNDEFINED, width=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'className', 'color', 'flip', 'height', 'icon', 'inline', 'rotate', 'style', 'width']
        self._type = 'DashIconify'
        self._namespace = 'dash_iconify'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'className', 'color', 'flip', 'height', 'icon', 'inline', 'rotate', 'style', 'width']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in ['icon']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(DashIconify, self).__init__(**args)
