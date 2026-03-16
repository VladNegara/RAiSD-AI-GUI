from abc import ABC, abstractmethod
from typing import Any

from PySide6.QtCore import (
    QObject,
    Signal,
    Slot,
)

from gui.model.meta import AbstractQObjectMeta


class Dependency(QObject):
    """
    A dependency between parameters.

    A dependency connects a condition and an effect into an "If and only
    if [condition], then [effect]." relation. Its main use is to enable
    and disable a parameter based on the value of another.
    """

    class Condition(ABC, QObject, metaclass=AbstractQObjectMeta):
        """
        An abstract condition class to be used as part of a dependency.

        A condition tracks a certain property and exposes a boolean
        value, emitting a signal when that property changes.
        """

        changed = Signal(bool)

        def __init__(
                self,
                value: bool = False,
                parent: QObject | None = None
        ) -> None:
            """
            Initialize a `Condition` object.

            :param value: the initial value of the condition
            :type value: bool

            :param parent: the parent of this `QObject`
            :type parent: QObject | None
            """
            super().__init__(parent=parent)
            self._value = value

        @property
        def value(self) -> bool:
            """
            The boolean value of the condition.

            Setting this property will emit the `changed` signal.
            """
            return self._value

        @value.setter
        def value(self, new_value: bool) -> None:
            self._value = new_value
            self.changed.emit(self._value)

    class Effect(ABC, QObject, metaclass=AbstractQObjectMeta):
        """
        An abstract effect class to be used as part of a dependency.

        An effect's `condition_changed` method changes a specific
        property, such as the enabled status of a parameter.
        """

        @Slot(bool)
        @abstractmethod
        def condition_changed(self, value: bool) -> None:
            """
            Apply the new boolean value to the property affected by this
            effect.
            """
            pass

    def __init__(
            self,
            source: Condition,
            target: Effect,
            parent: QObject | None = None,
    ) -> None:
        """
        Initialize a `Dependency` object.

        The dependency will connect the condition `source` to the effect
        `target`, i.e. it ensures that when the condition's `value`
        changes, the effect's `condition_changed` method is called.

        :param source: the condition to connect from
        :type source: Condition

        :param target: the effect to connect to
        :type target: Effect

        :param parent: the parent of this `QObject`
        :type parent: QObject | None
        """
        super().__init__(parent=parent)
        self._source = source
        self._target = target

        self._target.condition_changed(self._source.value)
        self._source.changed.connect(self._target.condition_changed)


class AndCondition(Dependency.Condition):
    """
    A condition whose value is the conjunction of its child conditions'
    values.
    """

    def __init__(
            self,
            conditions: list[Dependency.Condition],
            parent: QObject | None = None,
    ) -> None:
        """
        Initialize an `AndCondition` object.

        :param conditions: the list of child conditions
        :type conditions: list[Dependency.Condition]

        :param parent: the parent of this `QObject`
        :type parent: QObject | None
        """
        self._conditions = conditions
        super().__init__(
            all([condition.value for condition in self._conditions]),
            parent,
        )

        for condition in self._conditions:
            condition.changed.connect(self._condition_changed)

    @Slot(bool)
    def _condition_changed(self, _: bool) -> None:
        self.value = all([condition.value for condition in self._conditions])


class OrCondition(Dependency.Condition):
    """
    A condition whose value is the disjunction of its child conditions'
    values.
    """

    def __init__(
            self,
            conditions: list[Dependency.Condition],
            parent: QObject | None = None,
    ) -> None:
        """
        Initialize an `OrCondition` object.

        :param conditions: the list of child conditions
        :type conditions: list[Dependency.Condition]

        :param parent: the parent of this `QObject`
        :type parent: QObject | None
        """
        self._conditions = conditions
        super().__init__(
            any([condition.value for condition in self._conditions]),
            parent=parent,
        )

        for condition in self._conditions:
            condition.changed.connect(self._condition_changed)

    @Slot(bool)
    def _condition_changed(self, _: bool) -> None:
        self.value = any([condition.value for condition in self._conditions])
