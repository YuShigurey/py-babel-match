# py-babel-match

Using built-in `ast` module to transform your match-case stmts into plain if-else stmts that can run on 3.9 or lower python version. ~~"Use next generation Python, today."~~

This lib is only available on python3.10+, because parsing match stmt requires python3.10+. Outputed code's minimal version is unknown, but aiming versions are python3.8 or higher (versions with dataclass).

## Example

### Input Code:

~~~python

def test_pattern_matching():
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
            case Err():
                pass

~~~

### Output Code:

~~~python

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
~~~

## TODO

### Config

Current `pyproject.toml` finder is rudimentary.

### Unsupported Use Cases

There are still a lot of unsupported use cases for now.

