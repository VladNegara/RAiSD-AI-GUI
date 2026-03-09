from abc import ABC, abstractmethod
from numbers import Real
from typing import Generic, TypeVar
from re import Pattern, compile

from PySide6.QtCore import QObject, Signal

T = TypeVar("T")


class AbstractQObjectMeta(type(ABC), type(QObject)):
    """
    Metaclass for an abstract base QObject class.
    """

    pass


class Parameter(ABC, QObject, Generic[T], metaclass=AbstractQObjectMeta):
    """
    A base class for parameters to be filled in using the GUI.

    The class inherits from `ABC` to make it abstract, from `QObject`
    to use the signal mechanism and from `Generic` to add type hints
    based on the type of value that the parameter stores.
    """

    value_changed: Signal

    def __init__(
            self,
            name: str, description: str, flag: str,
            default_value: T,
    ) -> None:
        """
        Initialize a `Parameter` object.

        :param name: the name of the parameter
        :type name: str

        :param description: a longer description of the parameter
        :type description: str

        :param flag: the command-line flag of the parameter
        :type flag: str

        :param default_value: the default value of the parameter
        :type default_value: T
        """
        super().__init__(self)
        self.name = name
        self.description = description
        self.default_value = default_value
        self._value = default_value
        self.flag = flag

    @property
    def value(self) -> T:
        """
        The current value of the parameter.
        """
        return self._value

    @value.setter
    def value(self, new_value: T) -> None:
        self._value = new_value
        self.value_changed.emit(self.value, self.valid)

    def reset_value(self) -> None:
        """
        Reset the value of the parameter to the default value.
        """
        self.value = self.default_value

    @property
    def valid(self) -> bool:
        """
        Whether the current value of the parameter is valid.
        """
        return True

    @abstractmethod
    def to_cli(self) -> str:
        """
        Represent the parameter for the command line, taking into
        account its current value.

        :return: the command-line representation
        :rtype: str
        """
        pass


class BoolParameter(Parameter[bool]):
    """
    A boolean parameter in the GUI.

    The value of a boolean parameter is always valid.
    """

    value_changed = Signal(bool, bool)

    def to_cli(self) -> str:
        # A boolean parameter is represented in the command line by the
        # presence or absence of its flag.
        if self.value:
            return self.flag
        else:
            return ""
    
    def __str__(self) -> str:
        return (
            f'BoolParameter('
            + f'name: "{self.name}", '
            + f'description: "{self.description})", '
            + f'value: {self.value}, '
            + f'valid: {self.valid})'
        )


X = TypeVar("X", bound=float)


class NumberParameter(Parameter[X]):
    """
    A numeric parameter in the GUI.

    The value of a numeric parameter is valid if it is greater than the
    lower bound and lower than the upper bound, when provided.
    """

    def __init__(
            self,
            name: str, description: str, flag: str,
            default_value: X,
            lower_bound: X | None = None,
            upper_bound: X | None = None,
    ) -> None:
        """
        Initialize a `NumberParameter[X]` object.

        :param name: the name of the parameter
        :type name: str

        :param description: a longer description of the parameter
        :type description: str

        :param flag: the command-line flag of the parameter
        :type flag: str

        :param default_value: the default value of the parameter
        :type default_value: X

        :param lower_bound: the lower bound of the parameter (optional)
        :type lower_bound: X | None

        :param upper_bound: the upper bound of the parameter (optional)
        :type upper_bound: X | None
        """
        super().__init__(name, description, flag, default_value)
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

    @property
    def valid(self):
        if self.lower_bound is not None and self.value < self.lower_bound:
            return False
        if self.upper_bound is not None and self.value > self.upper_bound:
            return False
        return True

    def to_cli(self) -> str:
        # A numeric parameter is represented in the command line by
        # its flag and its value.
        return f"{self.flag} {self.value}"   


class IntParameter(NumberParameter[int]):
    """
    An integer parameter in the GUI.
    """

    value_changed = Signal(int, bool)

    def __str__(self) -> str:
        return (
            f'IntParameter('
            + f'name: "{self.name}", '
            + f'description: "{self.description})", '
            + f'lower bound: "{self.lower_bound}", ' 
            + f'upper bound: "{self.upper_bound}", '
            + f'value: {self.value}, '
            + f'valid: {self.valid})'
        )


class FloatParameter(NumberParameter[float]):
    """
    A floating-point parameter in the GUI.
    """

    value_changed = Signal(float, bool)

    def __str__(self) -> str:
        return (
            f'FloatParameter('
            + f'name: "{self.name}", '
            + f'description: "{self.description})", '
            + f'lower bound: "{self.lower_bound}", ' 
            + f'upper bound: "{self.upper_bound}", '
            + f'value: {self.value}, '
            + f'valid: {self.valid})'
        )


class StringParameter(Parameter[str]):
    """
    A string parameter in the GUI.

    The parameter may optionally contain a maximum length and/or a
    regex pattern the input must match.

    The value is considered valid when both of the following hold:
    - If a maximum length was specified, the value does not exceed it.
    - If a regex pattern was specified, the value matches it.

    If neither constraint is given, the value is always valid.
    """

    value_changed = Signal(str, bool)

    def __init__(
            self,
            name: str, description: str, flag: str, default_value: str,
            max_length: int | None = None,
            pattern: Pattern | None = None,
    ) -> None:
        """
        Initialize a `StringParameter` object.

        :param name: the name of the parameter
        :type name: str

        :param description: a longer description of the parameter
        :type description: str

        :param flag: the command-line flag of the parameter
        :type flag: str

        :param default_value: the default value of the parameter
        :type default_value: str

        :param max_length: the maximum length of the string (optional)
        :type max_length: int | None

        :param pattern: the pattern the string must match (optional)
        :type pattern: Pattern | None
        """
        super().__init__(name, description, flag, default_value)
        self.max_length = max_length
        self._pattern = pattern

    @property
    def valid(self) -> bool:
        if self.max_length is not None and len(self.value) > self.max_length:
            return False
        if self._pattern is not None and not self._pattern.match(self.value):
            return False
        return True

    def to_cli(self) -> str:
        return f"{self.flag} {self.value}"

    def __str__(self) -> str:
        return (
            f'String('
            + f'name: "{self.name}", '
            + f'description: "{self.description})", '
            + f'max length: {self.max_length}, '
            + f'pattern: {self._pattern}, '
            + f'value: {self.value}, '
            + f'valid: {self.valid})'
        )
