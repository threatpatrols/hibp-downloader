from dataclasses import asdict, dataclass, field
from datetime import datetime
from email.utils import parsedate_to_datetime
from enum import Enum
from typing import Union

from .hash_type import HashType


class PrefixMetadataDataSource(str, Enum):
    unknown_source_status = "unknown_source_status"
    local_source_ttl_cache = "local_source_ttl_cache"
    local_source_etag_match = "local_source_etag_match"
    remote_source_remote_cache = "remote_source_remote_cache"
    remote_source_origin_source = "remote_source_origin_source"


@dataclass()
class PrefixMetadata:
    prefix: str
    start_timestamp: Union[datetime, None] = field(default=None)
    hash_type: Union[HashType, None] = field(default=None)
    etag: Union[str, None] = field(default=None)
    bytes: Union[int, None] = field(default=0)
    server_timestamp: Union[str, datetime, None] = field(default=None)
    last_modified: Union[str, datetime, None] = field(default=None)
    content_encoding: Union[str, None] = field(default=None)
    content_checksum: Union[str, None] = field(default=None)
    data_source: Union[PrefixMetadataDataSource, None] = field(default=None)

    def __post_init__(self):
        if isinstance(self.server_timestamp, str):
            if ", " in self.server_timestamp:
                self.server_timestamp = parsedate_to_datetime(self.server_timestamp)
            else:
                self.server_timestamp = datetime.fromisoformat(self.server_timestamp)

        if isinstance(self.last_modified, str):
            if "," in self.last_modified:
                self.last_modified = parsedate_to_datetime(self.last_modified)
            else:
                self.last_modified = datetime.fromisoformat(self.last_modified)

    def as_dict(self):
        return {k: v for k, v in asdict(self).items() if v is not None}
