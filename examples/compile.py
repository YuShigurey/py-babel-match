from pathlib import Path
from py_babel_match.config.config import Config
from py_babel_match.console import main

main(
    Config(
        files=[
            "test_pattern_matching.py310.py"
        ],
        config_file_path=Path(__file__).parent/"pyproject.toml"
    )
)