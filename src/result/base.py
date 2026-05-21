from typing import Literal, Iterator, Generic, NoReturn, TypeVar
from dataclasses import dataclass
from abc import ABC, abstractmethod

S = TypeVar("S", covariant=True)
F = TypeVar("F", covariant=True)
T = TypeVar("T", covariant=True)


class _Result(ABC, Generic[T]):
    """
    Abstract base class representing a Result type.

    A Result is a container that represents either:
    - a successful value (Ok), or
    - a failure value (Fail).

    This base class defines the required interface for Result variants.
    """

    value: T

    @abstractmethod
    def is_fail(self) -> bool:
        """
        Return True if this Result is a Fail.

        Returns:
            bool: True if Fail, False otherwise.
        """
        ...

    @abstractmethod
    def is_ok(self) -> bool:
        """
        Return True if this Result is an Ok.

        Returns:
            bool: True if Ok, False otherwise.
        """
        ...

    @abstractmethod
    def __eq__(self, other: object) -> bool:
        """
        Compare this Result to another object for equality.

        Equality should be based on:
        - the Result variant (Ok vs Fail)
        - the contained value

        Args:
            other (object): The object to compare against.

        Returns:
            bool: True if equal, False otherwise.
        """
        ...

    @abstractmethod
    def __ne__(self, other: object) -> bool:
        """
        Compare this Result to another object for inequality.

        Inequality should be based on:
        - the Result variant (Ok vs Fail)
        - the contained value

        Args:
            other (object): The object to compare against.
        Returns:
            bool: True if unequal, False otherwise.
        """
        ...

    @abstractmethod
    def __repr__(self) -> str:
        """
        Return a developer-friendly string representation of the Result.

        Returns:
            str: A string representation of the Result.
        """
        ...


@dataclass(frozen=True, slots=True)
class Ok(_Result[S], Generic[S]):
    """
    Represents a successful Result.

    This variant stores a success value and provides helper behavior such as:
    - type guards via is_ok / is_fail
    - iterable unpacking support
    - value fallback via value_or
    """

    value: S
    __match_args__ = ("value",)

    def __iter__(self) -> Iterator[S]:
        """
        Yield the contained value to support unpacking and iteration.

        Example:
            ok = Ok(10)
            val, = ok

        Yields:
            Iterator[S]: The contained success value.
        """
        yield self.value

    def __eq__(self, other: object) -> bool:
        """
        Return True if the other object is an Ok with the same value.

        Args:
            other (object): The object to compare against.

        Returns:
            bool: True if both are Ok and values are equal.
        """
        return isinstance(other, Ok) and self.value == other.value

    def __ne__(self, other: object) -> bool:
        """
        Return True if the other object is an Ok with a different value.

        Args:
            other (object): The object to compare against.

        Returns:
            bool: True if both are Ok and values differ, otherwise NotImplemented.
        """
        if isinstance(other, Ok):
            return not (self.value == other.value)
        return NotImplemented

    def __hash__(self) -> int:
        """
        Return a hash for this Ok result.

        The hash is based on the variant and the contained value so Ok and Fail
        with the same value do not collide.

        Returns:
            int: Hash of the Ok result.
        """
        return hash((True, self.value))

    def __repr__(self) -> str:
        """
        Return a developer-friendly string representation of Ok.

        Returns:
            str: A string representation of the Ok result.
        """
        return f"<Ok ({(self.value)})>"

    def is_fail(self) -> Literal[False]:
        """
        Type guard indicating this Result is not a Fail.

        Returns:
            Literal[False]: Always False for Ok.
        """
        return False

    def is_ok(self) -> Literal[True]:
        """
        Type guard indicating this Result is an Ok.

        Returns:
            Literal[True]: Always True for Ok.
        """
        return True

    def value_or[T](self, result: T) -> T | S:
        """
        Return the contained value if it is not None, otherwise return a fallback.

        This is useful when Ok may contain None and you want a default.

        Args:
            result (T): The fallback value to return when Ok.value is None.

        Returns:
            T | S: The Ok value if not None, otherwise the fallback.
        """
        if self.value is not None:
            return self.value
        return result

    def unwrap_or_raise(self) -> S:
        """
        Return the contained value since this is an Ok.

        Returns:
            S: The contained success value.
        """
        return self.value


@dataclass(frozen=True, slots=True)
class Fail(_Result[F], Generic[F]):
    """
    Represents a failed Result.

    This variant stores an error value and provides helper behavior such as:
    - type guards via is_fail / is_ok
    - iterable unpacking support
    """

    value: F
    __match_args__ = ("value",)

    def __iter__(self) -> Iterator[F]:
        """
        Yield the contained failure value to support unpacking and iteration.

        Example:
            fail = Fail("error")
            err, = fail

        Yields:
            Iterator[F]: The contained error value.
        """
        yield self.value

    def __eq__(self, other: object) -> bool:
        """
        Return True if the other object is a Fail with the same error value.

        Args:
            other (object): The object to compare against.

        Returns:
            bool: True if both are Fail and values are equal.
        """
        return isinstance(other, Fail) and self.value == other.value

    def __ne__(self, other: object) -> bool:
        """
        Return True if the other object is a Fail with a different error value.

        Args:
            other (object): The object to compare against.

        Returns:
            bool: True if both are Fail and values differ, otherwise NotImplemented.
        """
        if isinstance(other, Fail):
            return not (self.value == other.value)
        return NotImplemented

    def __hash__(self) -> int:
        """
        Return a hash for this Fail result.

        The hash is based on the variant and the contained value so Ok and Fail
        with the same value do not collide.

        Returns:
            int: Hash of the Fail result.
        """
        return hash((True, self.value))

    def __repr__(self) -> str:
        """
        Return a developer-friendly string representation of Fail.

        Returns:
            str: A string representation of the Fail result.
        """
        return f"<Fail ({(self.value)})>"

    def is_fail(self) -> Literal[True]:
        """
        Type guard indicating this Result is a Fail.

        Returns:
            Literal[True]: Always True for Fail.
        """
        return True

    def is_ok(self) -> Literal[False]:
        """
        Type guard indicating this Result is not an Ok.

        Returns:
            Literal[False]: Always False for Fail.
        """
        return False

    def value_or[T](self, result: T) -> T:
        """Return the fallback value since this is a Fail.
        Args:
            result (T): The fallback value to return.
        Returns:
            T: The fallback value.
        """
        return result

    def unwrap_or_raise(self) -> NoReturn:
        """Return the contained error value since this is a Fail.
        Raises:
            Exception: The contained error value if it is an Exception.
            TypeError: If the contained error value is not an Exception.
        Returns:
            F: The contained error value.
        """
        if isinstance(self.value, Exception):
            raise self.value

        raise Exception(self.value)
        # raise TypeError(f"Cannot unwrap Fail with non-Exception value: {self.value}")


Result = _Result
