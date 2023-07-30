from dataclasses import dataclass, field


@dataclass(kw_only=True)
class AppContext:
    debug: bool = field(default=False)
    command: str | None = field(default=None)
    data_path: str | None = field(default=None)
    metadata_path: str | None = field(default=None)
    profiler: bool = False
    add_completion: bool = False
    no_args_is_help: bool = True
