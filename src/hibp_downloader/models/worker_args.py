from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional

from .hash_type import HashType


@dataclass()
class WorkerArgs:
    hash_type: HashType
    data_path: Path
    metadata_path: Path
    encoding_type: str

    http_timeout: int
    http_max_retries: int
    http_proxy: str
    http_verify: str
    http_debug: bool

    ignore_etag: bool
    local_cache_ttl: int
    worker_index: Optional[int] = None

    def as_dict(self):
        return {k: v for k, v in asdict(self).items()}
