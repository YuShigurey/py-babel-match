# py-babel-match

Using built-in `ast` module to transform your match-case stmts into plain if-else stmts that can run on 3.9 or lower python version. ~~"Use next generation Python, today."~~

This lib is only available on python3.10+, because parsing match stmt requires python3.10+. Outputed code's minimal version is unknown, but aiming versions are python3.8 or higher (versions with dataclass).

## How To Use

Add "tool.py-babel-match" field to pyproject.toml.

~~~toml
[tool.py-babel-match]
glob = ["*.py310.py"]
~~~

Run command `py-babel-match` in console. Generated file will be shown besides the origin file.

You can also embed transform process into a python file.

~~~python
from pathlib import Path
from py_babel_match.config.config import Config
from py_babel_match.console import main
main(
    Config(
        files=[
            "test_pattern_matching.py310.py"
        ],
    )
)
~~~

## Example


### Prelude

~~~python
import sys
if sys.version_info.minor >=10:
    from dataclasses import dataclass as dc
else:
    from dataclasses import dataclass
    def dc(cls):
        ret = dataclass(cls)
        ret.__match_args__ = tuple(cls.__dataclass_fields__)
        return ret
    
from typing import Generic, TypeVar

_T = TypeVar("_T")
_E = TypeVar("_E")

@dc
class Ok(Generic[_T]):
    t: _T

@dc
class Err(Generic[_E]):
    e: _E
~~~

### Input Code:

~~~python

def test_pattern_matching():
    ignore_err = True
    
    def pass_fail():
        for score in range(0, 11):
            if score > 6:
                yield Ok(score)
            else:
                yield Err(ValueError("fail to pass"))
    
    for res in pass_fail():
        match res:
            case Ok(t=score):
                print(f"Passed! score is {score}")
            case Err() if ignore_err:
                pass
            case Err(e):
                raise e

~~~

### Output Code:

~~~python

def test_pattern_matching():
    ignore_err = True

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
        elif isinstance(res, Err) and ignore_err:
            pass
        elif isinstance(res, Err):
            (e,) = (res.__getattribute__(Err.__match_args__[0]),)
            raise e
~~~

## TODO

### Config

Current `pyproject.toml` finder is rudimentary.

### Unsupported Use Cases

There are still a lot of unsupported use cases for now. Detailed list is scheduled after test extablished.

