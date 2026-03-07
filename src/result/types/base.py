from typing import List
from result.base import _Ok, _Fail

type Either[S, F] = Ok[S] | Fail[F]
type Ok[S] = _Ok[S]
type Fail[F] = _Fail[F]
type Result[T] = Ok[T] | Fail[T]
type ResultCombine[S, F] = Either[List[S], F]
