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
                
if __name__ == "__main__":
    test_pattern_matching()