from dataclasses import dataclass, field
from typing import Union


@dataclass()
class AppContext:
    debug: bool = field(default=False)
    command: Union[str, None] = field(default=None)
    data_path: Union[str, None] = field(default=None)
    metadata_path: Union[str, None] = field(default=None)
    profiler: bool = False
    add_completion: bool = False
    no_args_is_help: bool = True
