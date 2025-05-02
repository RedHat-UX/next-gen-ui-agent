# See https://github.com/streamlit/component-template/blob/master/template-reactless/my_component/__init__.py

import os

import streamlit.components.v1 as components

# When we're distributing a production version of the component, we'll
# replace the `url` param with `path`, and point it to the component's
# build directory:
parent_dir = os.path.dirname(os.path.abspath(__file__))
# build_dir = os.path.join(parent_dir, "frontend/build")
_component_func = components.declare_component("ngui_rhds_component", path=parent_dir)


# Create a wrapper function for the component. This is an optional
# best practice - we could simply expose the component function returned by
# `declare_component` and call it done. The wrapper allows us to customize
# our component's API: we can pre-process its input args, post-process its
# output value, and add a docstring for users.
def ngui_rhds_component(input_value, key=None):
    """Create a new instance of "ngui_rhds_component".

    Parameters
    ----------
    input_value: str
        RHDS Component
    key: str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.

    Returns
    -------
    None

    """
    # Call through to our private component function. Arguments we pass here
    # will be sent to the frontend, where they'll be available in an "args"
    # dictionary.
    _component_func(my_input_value=input_value, key=key)
