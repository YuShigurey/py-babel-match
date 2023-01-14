import argparse as ap
import pathlib
from py_babel_match.config.config import Config
from py_babel_match.config.finder import get_config
from py_babel_match.core.match.transform import Transformer

def run():
    parser = ap.ArgumentParser(
        prog="py-babel-match",
        add_help=True,
    )
    parser.add_argument("-f", "--file", default=None, help="config file")
    args = parser.parse_args()
    
    cwd = pathlib.Path(".").absolute()
    cfg_path = get_config(cwd=cwd, explicit_config_path=args.file)
    config = Config.from_file(config_file_path=cfg_path)
    main(config=config)
    

def main(config: Config):
    for file in config.list_files():
        file_path = pathlib.Path(file)
        new_file_content = Transformer(file).transform()
        
        if file_path.name.endswith(".py310.py"):
            new_name = file_path.name.removesuffix(".py310.py") + ".py"
        else:
            new_name = file_path.name.removesuffix(".py") + "_compiled" + file_path.suffix
        
        with open(
            file_path.parent / new_name,
            mode="w",
        ) as new_file:
            new_file.write(new_file_content)
