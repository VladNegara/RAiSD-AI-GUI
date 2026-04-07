from re import Pattern
from typing import Generic, TypeVar

T = TypeVar("T")


class Constraint(Generic[T]):
    @property
    def hint(self) -> str:
        raise NotImplementedError()

    def valid(self, value: T) -> bool:
        raise NotImplementedError()


X = TypeVar("X", bound=float)


class IntervalConstraint(Constraint[X]):
    def __init__(
            self,
            lower_bound: X | None = None,
            lower_bound_inclusive: bool = True,
            upper_bound: X | None = None,
            upper_bound_inclusive: bool = True,
    ) -> None:
        """
        Initialize an `IntervalConstraint` object.

        At least one of the arguments `lower_bound` and `upper_bound`
        must not be `None`.

        :param lower_bound: the lower bound of the interval
        :type lower_bound: int | None

        :param lower_bound_inclusive: whether the lower bound is
        inclusive
        :type lower_bound_inclusive: bool

        :param upper_bound: the upper bound of the interval
        :type upper_bound: int | None

        :param upper_bound_inclusive: whether the upper bound is
        inclusive
        :type upper_bound_inclusive: bool
        """
        if lower_bound is None and upper_bound is None:
            raise ValueError("Both bounds None for interval constraint.")
        self._lower_bound = lower_bound
        self._lower_bound_inclusive = lower_bound_inclusive
        self._upper_bound = upper_bound
        self._upper_bound_inclusive = upper_bound_inclusive

    @property
    def hint(self) -> str:
        if self._lower_bound is None:
            if self._upper_bound_inclusive:
                return f"Less than or equal to {self._upper_bound}."
            return f"Less than {self._upper_bound}."
        if self._upper_bound is None:
            if self._lower_bound_inclusive:
                return f"Greater than or equal to {self._lower_bound}."
            return f"Greater than {self._lower_bound}."
        return (
            f"Between {self._lower_bound} "
            + f"({"in" if self._lower_bound_inclusive else "ex"}clusive) "
            + f"and {self._upper_bound} "
            + f"({"in" if self._upper_bound_inclusive else "ex"}clusive)."
        )

    def valid(self, value: X) -> bool:
        if self._lower_bound is not None:
            if self._lower_bound_inclusive:
                if value < self._lower_bound:
                    return False
            elif value <= self._lower_bound:
                return False
        if self._upper_bound is not None:
            if self._upper_bound_inclusive:
                if value > self._upper_bound:
                    return False
            elif value >= self._upper_bound:
                return False
        return True


class EvenConstraint(Constraint[int]):
    @property
    def hint(self) -> str:
        return "The value must be even."

    def valid(self, value: int) -> bool:
        return value % 2 == 0


class MaxLengthConstraint(Constraint[str]):
    def __init__(self, max_length: int) -> None:
        self._max_length = max_length

    @property
    def hint(self) -> str:
        return f"Maximum {self._max_length} characters."

    def valid(self, value: str) -> bool:
        return len(value) <= self._max_length


class RegexConstraint(Constraint[str]):
    def __init__(self, pattern: Pattern, hint: str) -> None:
        self._pattern = pattern
        self._hint = hint

    @property
    def hint(self) -> str:
        return self._hint

    def valid(self, value: str) -> bool:
        return self._pattern.fullmatch(value) is not None
