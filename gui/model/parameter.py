from abc import ABC, abstractmethod
from numbers import Real
from typing import Generic, TypeVar
from re import Pattern, compile
from pathlib import Path
import os

from PySide6.QtCore import QObject, Signal

from gui.model.meta import AbstractQObjectMeta

T = TypeVar("T")


class Parameter(ABC, QObject, Generic[T], metaclass=AbstractQObjectMeta):
    """
    A base class for parameters to be filled in using the GUI.

    The class inherits from `ABC` to make it abstract, from `QObject`
    to use the signal mechanism and from `Generic` to add type hints
    based on the type of value that the parameter stores.
    """

    value_changed: Signal
    enabled_changed = Signal(bool)

    def __init__(
            self,
            name: str, description: str, flag: str,
            default_value: T,
            enabled: bool = True,
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
        self._enabled = enabled

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

    @property
    def enabled(self) -> bool:
        """
        Whether the parameter is enabled.
        """
        return self._enabled

    @enabled.setter
    def enabled(self, new_enabled: bool) -> None:
        self._enabled = new_enabled
        self.enabled_changed.emit(self._enabled)

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

    The value of a numeric parameter is valid if it is greater than or equal to the
    lower bound and lower than or equal to the upper bound, when provided.
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


class EnumParameter(Parameter[int]):
    """
    A parameter with enumerated values in the GUI.
    """

    value_changed = Signal(int, bool)

    def __init__(
            self,
            name: str, description: str, flag: str,
            options: list[tuple[str, str]],
            default_value: int,
    ) -> None:
        """
        Initialize an `EnumParameter` object.

        The `options` argument is a list of the options offered by the
        enum parameter. Each option is a 2-tuple where the first element
        is the name to be displayed to the user, and the second is the
        form to be used in the command-line representation.

        :param name: the name of the parameter
        :type name: str

        :param description: a longer description of the parameter
        :type description: str

        :param flag: the command-line flag of the parameter
        :type flag: str

        :param options: the options of the parameter
        :type options: list[tuple[str, str]]

        :param default_value: the index of the default option
        :type default_value: int
        """
        super().__init__(name, description, flag, default_value)
        self._options = options

    @property
    def options(self) -> list[str]:
        return [option[0] for option in self._options]

    @property
    def option(self) -> str | None:
        try:
            return self.options[self.value]
        except IndexError:
            return None

    @property
    def valid(self) -> bool:
        return self.value in range(len(self.options))

    def to_cli(self) -> str:
        return f"{self.flag} {self._options[self.value][1]}"

    def __str__(self) -> str:
        return (
            "EnumParameter"
            + f'name: "{self.name}", '
            + f'description: "{self.description}", '
            + f'options: {self.options}, '
            + f'selected option: {self.option})'
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
        if self._pattern is not None and not self._pattern.fullmatch(self.value):
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


X = TypeVar("X", bound=float)


class NumberParameter(Parameter[X]):
    """
    A numeric parameter in the GUI.

    The value of a numeric parameter is valid if it is greater than or equal to the
    lower bound and lower than or equal to the upper bound, when provided.
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


class EnumParameter(Parameter[int]):
    """
    A parameter with enumerated values in the GUI.
    """

    value_changed = Signal(int, bool)

    def __init__(
            self,
            name: str, description: str, flag: str,
            options: list[tuple[str, str]],
            default_value: int,
    ) -> None:
        """
        Initialize an `EnumParameter` object.

        The `options` argument is a list of the options offered by the
        enum parameter. Each option is a 2-tuple where the first element
        is the name to be displayed to the user, and the second is the
        form to be used in the command-line representation.

        :param name: the name of the parameter
        :type name: str

        :param description: a longer description of the parameter
        :type description: str

        :param flag: the command-line flag of the parameter
        :type flag: str

        :param options: the options of the parameter
        :type options: list[tuple[str, str]]

        :param default_value: the index of the default option
        :type default_value: int
        """
        super().__init__(name, description, flag, default_value)
        self._options = options

    @property
    def options(self) -> list[str]:
        return [option[0] for option in self._options]

    @property
    def option(self) -> str | None:
        try:
            return self.options[self.value]
        except IndexError:
            return None

    @property
    def valid(self) -> bool:
        return self.value in range(len(self.options))

    def to_cli(self) -> str:
        return f"{self.flag} {self._options[self.value][1]}"

    def __str__(self) -> str:
        return (
            "EnumParameter"
            + f'name: "{self.name}", '
            + f'description: "{self.description}", '
            + f'options: {self.options}, '
            + f'selected option: {self.option})'
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
        if self._pattern is not None and not self._pattern.fullmatch(self.value):
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


class FileParameter(Parameter[list[str]]):
    """
    A file path parameter in the GUI

    Stores the list of file paths selected by the user. The file
    parameter accepts a list of file parameters, and it has the option
    to allow single or multiple file inputs.

    The value is valid when all the following holds:
    - The value list is not empty.
    - If it is not a multiple-file parameter, (`multiple` = False),
    there should only be a single file in the list.
    - Every file in the list exists and readable, and their file
    extension is in `accepted_formats`.

    There are three different levels of strictness for file types:

    1. If `accepted_formats` is given and `strict` is `True`, the user
    is only able to select files that match the types in
    `accepted_formats`.
    2. If `accepted_formats` is given and `strict` is `True`, the user
    can select any file, but a warning is displayed if the file type
    does not match the ones in `accepted_formats`.
    3. If `accepted_formats` is `None`, the user can select any file.
    The value of `strict` is expected to be `False`.
    """

    value_changed = Signal(list, bool)

    def __init__(
        self,
        name: str,
        description: str,
        flag: str,
        accepted_formats: list[str] | None = None,
        strict: bool = False,
        multiple: bool = False,
        default_value: list[str] | None = None,
    ) -> None:
        self.strict = strict
        if strict:
            self.accepted_formats = (
                [ext if ext.startswith(".") else f".{ext}"
                    for ext in accepted_formats]
                if accepted_formats is not None else None
            )
            self.expected_formats = None
        if not strict:
            self.expected_formats = (
                [ext if ext.startswith(".") else f".{ext}"
                    for ext in accepted_formats]
                if accepted_formats is not None else None
            )
            self.accepted_formats = None
        self.multiple = multiple
        super().__init__(name, description, flag, default_value or [])

    @property
    def valid(self) -> bool:
        if not self.value:
            return False
        if not self.multiple and len(self.value) > 1:
            return False
        return all(
            Path(f).is_file()
            and os.access(Path(f), os.R_OK)
            and (self.accepted_formats is None
                 or Path(f).suffix.lower() in self.accepted_formats
                 or Path(f).suffix.lower() in self.expected_formats)
            for f in self.value)

    @property
    def file_extensions(self) -> list[str]:
        return [Path(f).suffix.lower() for f in self.value if f]

    @property
    def matches_expected(self) -> bool:
        if not self.value or self.expected_formats is None:
            return True
        return all(
            Path(f).suffix.lower() in self.expected_formats
            for f in self.value
        )

    @Parameter.value.setter
    def value(self, new_value: list[str]) -> None:
        self._value = new_value
        self.value_changed.emit(self.value, self.valid)

    def __str__(self) -> str:
        return (
            f'FileParameter('
            f'name: "{self.name}", '
            f'description: "{self.description}", '
            f'accepted_formats: {self.accepted_formats}, '
            f'value: "{self.value}", '
            f'valid: {self.valid})'
        )

    def to_cli(self) -> str:
        if self.valid:
            return " ".join(f"{self.flag} {f}" for f in self.value)
        return ""
