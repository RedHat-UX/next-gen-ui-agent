import argparse
import os

"""
Helper classes for configuration arguments loading from environment variables if not defined in the commandline arguments.
Argparse actions to take a default value from an environment variable if not defined in the commandline arguments.

Example how to use:

```python
import argparse
from argparse_env_default_action import EnvDefault

parser=argparse.ArgumentParser()
parser.add_argument(
    "-u", "--url", action=EnvDefault, envvar='URL',
    help="Specify the URL to process (can also be specified using `URL` environment variable)")

args=parser.parse_args()

print(args.url)

```

"""


class EnvDefault(argparse.Action):
    """
    Argparse action to set a default value from an environment variable if not defined in the commandline arguments.

    New `envvar` argument is the name of the environment variable to use as default. If the environment variable is not set or is an empty string, the default value is used.

    """

    def __init__(self, envvar, required=True, default=None, **kwargs):
        if envvar:
            if envvar in os.environ and os.environ[envvar].strip() != "":
                default = os.environ[envvar]
        if required and default:
            required = False
        super(EnvDefault, self).__init__(default=default, required=required, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)


class EnvDefaultExtend(argparse.Action):
    """
    Argparse action that combines EnvDefault and `extend` behavior of argparse.
    Gets a default value from an environment variable if not defined in commandline arguments,
    and extends the list when the argument is provided multiple times.

    New `envvar` argument is the name of the environment variable to use as default.
    If the environment variable is not set or is an empty string, the default value is used.
    When the argument is provided multiple times, values are extended to the list.
    Commandline arguments override (replace) the default from environment variable.
    """

    def __init__(self, envvar, required=True, default=None, **kwargs):
        if envvar:
            if envvar in os.environ and os.environ[envvar].strip() != "":
                # Convert env var to list if it's a string (for nargs="+")
                env_value = os.environ[envvar]
                # Split by comma or space if it contains multiple values
                if "," in env_value:
                    default = [v.strip() for v in env_value.split(",") if v.strip()]
                else:
                    default = [env_value]
        if required and default:
            required = False
        # Ensure default is a list for extend behavior
        if default is not None and not isinstance(default, list):
            default = [default]
        # Store the default value so we can check if current value is still the default
        self._default_value = default
        super(EnvDefaultExtend, self).__init__(
            default=default, required=required, **kwargs
        )

    def __call__(self, parser, namespace, values, option_string=None):
        # Get existing value from namespace
        items = getattr(namespace, self.dest, None)

        # If the current value is still the default (from env var), replace it
        # instead of extending. This allows commandline args to override env vars.
        # If items is None (no default was set), start with empty list.
        if items == self._default_value or items is None:
            items = []

        # Extend with new values
        if isinstance(values, list):
            items.extend(values)
        else:
            items.append(values)
        setattr(namespace, self.dest, items)
