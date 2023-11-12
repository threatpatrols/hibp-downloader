from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional

from .hash_type import HashType


@dataclass()
class WorkerArgs:
    hash_type: HashType
    data_path: Path
    metadata_path: Path
    encoding_type: str
    ignore_etag: bool = field(default=False)
    local_cache_ttl: int = field(default=(12 * 3600))
    worker_index: Optional[int] = None

    def as_dict(self):
        return {k: v for k, v in asdict(self).items()}
