# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class EventListener(Component):
    """An EventListener component.
The EventListener component listens for events from the document object or children if provided.

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    The children of this component. If any children are provided, the
    component will listen for events from these      components. If no
    children are specified, the component will listen for events from
    the document object.

- id (string; optional):
    The ID used to identify this component in Dash callbacks.

- className (string; optional):
    A custom class name.

- event (dict; optional):
    The latest event fired.

- events (list of dicts; default [{"event": "keydown", "props": ["key", "altKey", "ctrlKey", "shiftKey","metaKey", "repeat"]}]):
    The event entry specifies which event to listen to, e.g. \"click\"
    for click events. The \"props\" entry specifies      what event
    properties to record, e.g. [\"x\", \"y\"] to get the cursor
    position.

    `events` is a list of dicts with keys:

    - event (string; optional)

    - props (list of strings; optional)

- logging (boolean; default False):
    If True, event information is logged to the javascript console.
    Useful if you can't remember events props.

- n_events (number; default 0):
    The number of events fired.

- style (dict; optional):
    The CSS style of the component."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_extensions'
    _type = 'EventListener'
    @_explicitize_args
    def __init__(self, children=None, id=Component.UNDEFINED, events=Component.UNDEFINED, logging=Component.UNDEFINED, style=Component.UNDEFINED, className=Component.UNDEFINED, event=Component.UNDEFINED, n_events=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'className', 'event', 'events', 'logging', 'n_events', 'style']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'className', 'event', 'events', 'logging', 'n_events', 'style']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        super(EventListener, self).__init__(children=children, **args)
