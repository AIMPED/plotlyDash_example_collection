# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Mermaid(Component):
    """A Mermaid component.


Keyword arguments:

- id (string; optional):
    The ID used to identify this component in Dash callbacks.

- chart (string; optional):
    The mermaid code of your chart. Check Mermaid js documentation for
    details.

- className (string; optional):
    The class of the component.

- config (dict; optional):
    On optional object with one of several Mermaid config parameters.
    Check Mermaid js documentation for details.

- name (string; default makeId(5)):
    On optional name of your mermaid diagram/flowchart/gantt etc."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_extensions'
    _type = 'Mermaid'
    @_explicitize_args
    def __init__(self, chart=Component.UNDEFINED, name=Component.UNDEFINED, config=Component.UNDEFINED, id=Component.UNDEFINED, className=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'chart', 'className', 'config', 'name']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'chart', 'className', 'config', 'name']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(Mermaid, self).__init__(**args)
