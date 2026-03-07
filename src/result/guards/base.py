from typing import TypeGuard, TypeIs
from result.types.base import Either, Result as ResultType, Ok, Fail
from result.base import Result as ResultInstance


def is_result[T](result: T) -> TypeGuard[ResultType[T]]:
    """
    Type guard to check if a value is a Result instance (Ok or Fail).

    Args:
        result (T): The object to check.

    Returns:
        TypeGuard[ResultInstance[T]]: True if `result` is an instance of Ok or Fail,
        otherwise False.
    """
    return isinstance(result, ResultInstance)


def is_ok[S, F](result: Either[S, F]) -> TypeIs[Ok[S]]:
    """
    Type guard to check if a Result is an Ok.

    This function can be used to narrow the type of a Result to Ok.

    Args:
        result (Either[S, F]): The Result object to check.

    Returns:
        TypeIs[Ok[S]]: True if `result` is an Ok result, otherwise False.
    """
    return result.isOk()


def is_fail[S, F](result: Either[S, F]) -> TypeIs[Fail[F]]:
    """
    Type guard to check if a Result is a Fail.

    This function can be used to narrow the type of a Result to Fail.

    Args:
        result (Either[S, F]): The Result object to check.

    Returns:
        TypeIs[Fail[F]]: True if `result` is a Fail result, otherwise False.
    """
    return result.isFail()