from dataclasses import dataclass as dc
from typing import Generic, TypeVar
_T = TypeVar('_T')
_E = TypeVar('_E')

@dc
class Ok(Generic[_T]):
    t: _T

@dc
class Err(Generic[_E]):
    e: _E

def test_pattern_matching():

    def pass_fail():
        for score in range(0, 11):
            if score > 6:
                yield Ok(score)
            else:
                yield Err(ValueError('fail to pass'))
    for res in pass_fail():
        if isinstance(res, Ok):
            (score,) = (res.t,)
            print(f'Passed! score is {score}')
        elif isinstance(res, Err):
            pass