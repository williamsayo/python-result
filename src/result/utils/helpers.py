from inspect import isclass
from result.base import Ok as OkClass, Fail as FailClass, Result as ResultClass
from result.types.base import Either, Ok, Fail, ResultCombine
from result.guards import is_fail
from typing import List, Sequence, Callable, Any
from functools import wraps, partial


def result_equality(result: object, otherResult: object) -> bool:
    """
    Compare two Result objects for equality.

    This function returns True only when:
    - both inputs are Ok results and their values are equal, OR
    - both inputs are Fail results and their values are equal.

    If the two inputs are not both Results, or they are different variants
    (Ok vs Fail), the function returns False.

    Args:
        result (T): The first object to compare.
        otherResult (K): The second object to compare.

    Returns:
        bool: True if both are the same Result variant and their values match,
        otherwise False.
    """

    if (
        isinstance(result, OkClass)
        and isinstance(otherResult, OkClass)
        or isinstance(result, FailClass)
        and isinstance(otherResult, FailClass)
    ):
        return result.value == otherResult.value
    return False


def result_ok[S](value: S = None) -> Ok[S]:
    """
    Create an Ok result containing the provided value.

    If no value is passed, the Ok result will contain None.

    Args:
        value (S | None, optional): The value to wrap in an Ok result.
            Defaults to None.

    Returns:
        Ok[S]: An Ok result containing the provided value.
    """
    return OkClass(value)


def result_fail[F](value: F) -> Fail[F]:
    """
    Create a Fail result containing the provided error value.

    Args:
        value (F): The error value to wrap in a Fail result.

    Returns:
        Fail[F]: A Fail result containing the provided error value.
    """
    return FailClass(value)


def result_combine[S, F](
    results: Sequence[Either[S, F]],
) -> ResultCombine[S, F]:
    """
    Combine a sequence of Result objects into a single Result.

    Behavior:
    - If all results are Ok, returns Ok([...]) containing all Ok values in order.
    - If any result is Fail, returns Fail(error) using the first Fail encountered.

    Args:
        results (Sequence[Either[S, F]]): A sequence of Ok/Fail results.

    Returns:
        Ok[List[S | None]] | Fail[F]:
            - Ok(list_of_values) if all are Ok
            - Fail(error) if any Fail is found
    """
    validResults: List[S] = []

    for result in results:
        if is_fail(result):
            return result_fail(result.value)
        validResults.append(result.value)
    return result_ok(validResults)


def value_or[T, K](result: Either[T, T], default: K) -> T | K:
    """
    Return the contained value from an Ok result, or a default value if Fail.

    This function enforces that the first argument must be a Result instance
    (Ok or Fail). If a non-result is passed, a TypeError is raised.

    Args:
        result (Either[T, T]): The Result (Ok/Fail) to extract a value from.
        default (K): The fallback value to return when result is Fail.

    Raises:
        TypeError: If `result` is not an Ok/Fail instance.

    Returns:
        T | None | K:
            - Ok.value if the result is Ok
            - default if the result is Fail
    """
    if not isinstance(result, ResultClass):
        raise TypeError(f"Expected Result (Ok/Fail), got {repr(result)}")
    if not is_fail(result):
        return result.value
    return default


def unwrap_or[T, E](result: T, default: E) -> T | E:
    """
    Extract and return the raw value from a Result, or return a default value.

    Note:
        Despite the type hint, this function safely handles non-Result inputs:
        if the input is not an Ok/Fail instance, the default is returned.

    Args:
        result (ResultInstance[T]): The Result (Ok/Fail) to unwrap.
        default (E): The fallback value to return if result is not a Result.

    Returns:
        T | E:
            - result.value if result is an Ok/Fail instance
            - default otherwise
    """
    if isinstance(result, ResultClass):
        return result.value
    return default


def as_result[S, T: Exception](
    *exceptions: type[T],
) -> Callable[[Callable[..., S]], Callable[..., Either[S, T]]]:
    """
    Decorator to convert exceptions into Fail results.

    This decorator wraps a function and converts any specified exceptions it raises
    into Fail results. If the function executes successfully, its return value is
    wrapped in an Ok result.

    Type Parameters:
        ExcT: The exception type(s) to catch. Must be a subclass of Exception.
        S: The return type of the decorated function.

    Args:
        *exceptions: One or more exception types to catch and convert to Fail.
                    All must be subclasses of Exception.

    Returns:
        A decorator that transforms a function with return type S to return Either[S, ExcT].

    Example:
        >>> @as_result(ValueError, TypeError)
        ... def parse_int(s: str) -> int:
        ...     return int(s)
        ...
        >>> result = parse_int("123")  # Ok[int]
        >>> error = parse_int("abc")   # Fail[ValueError]
    """
    if not exceptions or not all(
        isclass(exception) and issubclass(exception, Exception)
        for exception in exceptions
    ):
        raise ValueError("At least one exception type must be provided to as_result.")

    def decorator(func: Callable[..., S]) -> Callable[..., Either[S, T]]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Either[S, T]:
            try:
                return result_ok(func(*args, **kwargs))
            except exceptions as exception:
                return result_fail(exception)  # type: ignore

        return wrapper

    return decorator


as_result_all = partial(as_result, Exception)
