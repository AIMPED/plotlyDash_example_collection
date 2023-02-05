# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Purify(Component):
    """A Purify component.
The Html component makes it possible to render html sanitized via DOMPurify.

Keyword arguments:

- id (string; optional):
    The ID used to identify this component in Dash callbacks.

- className (string; optional):
    The class of the component.

- config (dict; optional):
    Configuration (optional) of DOMPurify, see the docs
    https://github.com/cure53/DOMPurify.

- html (string; optional):
    Html string."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_extensions'
    _type = 'Purify'
    @_explicitize_args
    def __init__(self, html=Component.UNDEFINED, config=Component.UNDEFINED, id=Component.UNDEFINED, className=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'className', 'config', 'html']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'className', 'config', 'html']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(Purify, self).__init__(**args)
