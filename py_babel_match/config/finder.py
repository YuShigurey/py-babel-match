from pathlib import Path


def get_config(cwd: str | Path, explicit_config_path: str | Path | None) -> Path:
    match cwd, explicit_config_path:
        case cwd, None: ret = get_config_path(cwd=cwd)
        case _, explicit_config_path: ret = explicit_config_path
        
    if ret is None:
        raise ValueError(f"{cwd, explicit_config_path = }")
    
    return Path(ret)

def get_config_path(cwd: str | Path) -> Path | None:
    cwd = Path(cwd)
    if (ret:=(Path(cwd)/"pyproject.toml")).exists():
        return ret
    else:
        return None
    