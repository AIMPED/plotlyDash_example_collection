# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Lottie(Component):
    """A Lottie component.


Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    The children of this component.

- id (string; optional):
    The ID used to identify this component in Dash callbacks.

- ariaLabel (string; optional)

- ariaRole (string; optional)

- className (string; optional):
    The class of the component.

- direction (number; optional)

- height (string; optional):
    Pixel value for containers height.

- isClickToPauseDisabled (boolean; optional)

- isPaused (boolean; optional)

- isStopped (boolean; optional)

- options (dict; optional):
    Options passed to the Lottie animation (see
    https://www.npmjs.com/package/react-lottie for details).

- segments (list of numbers; optional)

- speed (number; optional)

- style (string; optional)

- title (string; optional)

- url (string; optional):
    If set, data will be downloaded from this url.

- width (string; optional):
    Pixel value for containers width."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_extensions'
    _type = 'Lottie'
    @_explicitize_args
    def __init__(self, children=None, id=Component.UNDEFINED, className=Component.UNDEFINED, options=Component.UNDEFINED, url=Component.UNDEFINED, width=Component.UNDEFINED, height=Component.UNDEFINED, isStopped=Component.UNDEFINED, isPaused=Component.UNDEFINED, speed=Component.UNDEFINED, segments=Component.UNDEFINED, direction=Component.UNDEFINED, ariaRole=Component.UNDEFINED, ariaLabel=Component.UNDEFINED, isClickToPauseDisabled=Component.UNDEFINED, title=Component.UNDEFINED, style=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'ariaLabel', 'ariaRole', 'className', 'direction', 'height', 'isClickToPauseDisabled', 'isPaused', 'isStopped', 'options', 'segments', 'speed', 'style', 'title', 'url', 'width']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'ariaLabel', 'ariaRole', 'className', 'direction', 'height', 'isClickToPauseDisabled', 'isPaused', 'isStopped', 'options', 'segments', 'speed', 'style', 'title', 'url', 'width']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        super(Lottie, self).__init__(children=children, **args)
