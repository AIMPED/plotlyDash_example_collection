# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class DeferScript(Component):
    """A DeferScript component.
Used to delay import of js resources until after React had been loaded. Typically used to apply js to dynamic
content. Based on https://github.com/Grasia/grasia-dash-components/blob/master/src/components/Import.react.js

Keyword arguments:

- id (string; optional):
    The ID used to identify this component in Dash callbacks.

- src (string; optional):
    Local or external source of the javascript to import."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_extensions'
    _type = 'DeferScript'
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, src=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'src']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'src']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(DeferScript, self).__init__(**args)
