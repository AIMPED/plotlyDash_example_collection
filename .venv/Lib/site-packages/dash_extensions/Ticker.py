# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Ticker(Component):
    """A Ticker component.
A light wrapper of ReactTicker.

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    The children of this component.

- id (string; optional):
    The ID used to identify this component in Dash callbacks.

- className (string; optional):
    The class of the component.

- direction (a value equal to: "toRight", "toLeft"; optional)

- height (number | string; optional)

- mode (a value equal to: "chain", "await", "smooth"; optional)

- move (boolean; optional)

- offset (number | string; optional)

- speed (number; optional)"""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_extensions'
    _type = 'Ticker'
    @_explicitize_args
    def __init__(self, children=None, direction=Component.UNDEFINED, mode=Component.UNDEFINED, move=Component.UNDEFINED, offset=Component.UNDEFINED, speed=Component.UNDEFINED, height=Component.UNDEFINED, id=Component.UNDEFINED, className=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'className', 'direction', 'height', 'mode', 'move', 'offset', 'speed']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'className', 'direction', 'height', 'mode', 'move', 'offset', 'speed']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        super(Ticker, self).__init__(children=children, **args)
