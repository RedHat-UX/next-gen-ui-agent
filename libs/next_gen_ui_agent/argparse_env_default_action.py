import argparse
import os

"""
Helper class for configuration arguments loading from environment variables if not definrd in the commandline arguments.
Argparse action to set a default value from an environment variable if not defined in the commandline arguments.

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
