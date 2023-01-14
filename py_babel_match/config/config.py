from dataclasses import dataclass, field
from functools import reduce
from itertools import chain
from operator import add
from pathlib import Path
from glob import glob
import tomli


@dataclass
class Config:
    files: list[str] = field(default_factory=list)
    glob: list[str] = field(default_factory=list)
    config_file_path: Path = field(default=".")
    
    @classmethod
    def from_file(cls, config_file_path: Path) -> "Config":
        with open(config_file_path, 'rb') as f:
            full_config_dict = tomli.load(f)
            
        config_dict: dict = full_config_dict.get("tool", {}).get("py-babel-match")
        if config_dict is None:
            raise ValueError("In pyproject.toml, domain tool.py-babel-match is not found")
        
        return Config(**config_dict, config_file_path=config_file_path)
    
    def list_files(self):
        config_dir = self.config_file_path.parent
        ret = [
            config_dir/_
            for _ in self.files
        ] + reduce(
            add, 
            [glob(pathname=_, root_dir=config_dir, recursive=True)
            for _ in self.glob]
            , []
        )
        
        print(ret)
        return ret

        
        
        
        
        
    