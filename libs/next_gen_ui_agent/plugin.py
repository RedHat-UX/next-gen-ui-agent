import abc


class FormatterBase(metaclass=abc.ABCMeta):
    """Base class for example plugin used in the tutorial."""

    def __init__(self, max_width=60):
        self.max_width = max_width

    @abc.abstractmethod
    def format(self, data):
        """Format the data and return unicode text.

        :param data: A dictionary with string keys and simple types as
                     values.
        :type data: dict(str:?)
        :returns: Iterable producing the formatted text.
        """


class Simple(FormatterBase):
    """A very basic formatter."""

    def format(self, data):
        """Format the data and return unicode text.

        :param data: A dictionary with string keys and simple types as
                     values.
        :type data: dict(str:?)
        """
        for name, value in sorted(data.items()):
            line = "{name} = {value}\n".format(
                name=name,
                value=value,
            )
            yield line
