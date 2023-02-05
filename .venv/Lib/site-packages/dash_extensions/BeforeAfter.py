# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class BeforeAfter(Component):
    """A BeforeAfter component.
Before After Image Slider based on https://github.com/sneas/img-comparison-slider

Keyword arguments:

- id (string; optional):
    The ID used to identify this component in Dash callbacks.

- after (dict; optional):
    Props for the `after` Img component. eg {\"src\":
    \"/assets/lena_color.png\"}.

- before (dict; optional):
    Props for the `before` Img component. eg {\"src\":
    \"/assets/lena_bw.png\"}.

- direction (a value equal to: 'horizontal', 'vertical'; default 'horizontal'):
    Set slider direction.

- height (string; default 'auto'):
    Image height - default \"auto\" for responsive images.

- hover (boolean; default True):
    Automatic slide on mouse over.

- keyboard (a value equal to: 'enabled', 'disabled'; default 'enabled'):
    Enable/disable slider position control with the keyboard.

- value (number; default 50):
    The divider position can be specified as a percentage, i.e. 0 to
    100.

- width (string; default '100%'):
    Image width - default \"100%\" for responsive images."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_extensions'
    _type = 'BeforeAfter'
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, height=Component.UNDEFINED, width=Component.UNDEFINED, hover=Component.UNDEFINED, value=Component.UNDEFINED, direction=Component.UNDEFINED, keyboard=Component.UNDEFINED, before=Component.UNDEFINED, after=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'after', 'before', 'direction', 'height', 'hover', 'keyboard', 'value', 'width']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'after', 'before', 'direction', 'height', 'hover', 'keyboard', 'value', 'width']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(BeforeAfter, self).__init__(**args)
