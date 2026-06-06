from dataclasses import dataclass, field


@dataclass()
class AppContext:
    debug: bool = field(default=False)
    command: str | None = field(default=None)
    data_path: str | None = field(default=None)
    metadata_path: str | None = field(default=None)
    add_completion: bool = False
    no_args_is_help: bool = True
