import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .prefix_metadata import PrefixMetadata, PrefixMetadataDataSource


@dataclass()
class QueueItemStats:
    prefix_first: str
    prefix_last: str
    prefix_count: int

    request_count: int
    bytes_received: int
    bytes_processed: int

    local_source_ttl_cache_count: int
    local_source_etag_match_count: int
    remote_source_remote_cache_count: int
    remote_source_origin_source_count: int
    unknown_source_status_count: int

    start_time: float = field(default=time.time())
    __end_time: float | None = field(default=None)
    __request_rate: float = field(default=0)  # per-second
    __bytes_processed_rate: float = field(default=0)  # per-second

    @property
    def request_rate(self) -> float:
        return self.__request_rate

    @property
    def bytes_processed_rate(self) -> float:
        return self.__bytes_processed_rate

    @property
    def run_time(self) -> float:
        return self.end_time - self.start_time  # type: ignore[operator]

    @property
    def end_time(self) -> float | None:
        return self.__end_time

    @end_time.setter
    def end_time(self, value: float) -> None:
        self.__end_time = value
        if self.run_time > 0:
            self.__request_rate = self.request_count / self.run_time
            self.__bytes_processed_rate = self.bytes_processed / self.run_time

    def end_trigger(self) -> None:
        self.end_time = time.time()


@dataclass()
class QueueRunningStats:
    start_time: float = field(default_factory=time.time)
    queue_item_count: int = field(default=0)

    prefix_latest: str | None = field(default=None)
    prefix_count_sum: int = field(default=0)

    request_count_sum: int = field(default=0)
    bytes_received_sum: int = field(default=0)
    bytes_processed_sum: int = field(default=0)

    local_source_ttl_cache_count_sum: int = field(default=0)
    local_source_etag_match_count_sum: int = field(default=0)
    remote_source_remote_cache_count_sum: int = field(default=0)
    remote_source_origin_source_count_sum: int = field(default=0)
    unknown_source_status_count_sum: int = field(default=0)

    __end_time: float | None = field(default=None)
    __request_rate_total: float = field(default=0)  # per-second
    __bytes_processed_rate_total: float = field(default=0)  # per-second

    @property
    def request_rate_total(self) -> float:
        return self.__request_rate_total

    @property
    def bytes_processed_rate_total(self) -> float:
        return self.__bytes_processed_rate_total

    @property
    def run_time(self) -> float:
        return self.end_time - self.start_time  # type: ignore[operator]

    @property
    def end_time(self) -> float | None:
        return self.__end_time

    @end_time.setter
    def end_time(self, value: float) -> None:
        self.__end_time = value
        if self.run_time > 0:
            self.__request_rate_total = self.request_count_sum / self.run_time
            self.__bytes_processed_rate_total = self.bytes_processed_sum / self.run_time

    def end_trigger(self) -> None:
        self.end_time = time.time()

    def add_item_stats(self, item: QueueItemStats) -> None:
        self.queue_item_count += 1
        self.prefix_latest = item.prefix_last
        self.prefix_count_sum += item.request_count
        self.request_count_sum += item.request_count
        self.bytes_received_sum += item.bytes_received
        self.bytes_processed_sum += item.bytes_processed
        self.local_source_ttl_cache_count_sum += item.local_source_ttl_cache_count
        self.local_source_etag_match_count_sum += item.local_source_etag_match_count
        self.remote_source_remote_cache_count_sum += item.remote_source_remote_cache_count
        self.remote_source_origin_source_count_sum += item.remote_source_origin_source_count
        self.unknown_source_status_count_sum += item.unknown_source_status_count
        self.end_trigger()


class QueueItemStatsCompute:
    stats: QueueItemStats

    def __init__(self, results: list[PrefixMetadata]):
        data: dict[str, Any] = {
            "start_time": None,
            "prefix_first": results[0].prefix,
            "prefix_last": results[-1].prefix,
            "prefix_count": len(results),
            "request_count": 0,
            "bytes_received": 0,
            "bytes_processed": 0,
            "local_source_ttl_cache_count": 0,
            "local_source_etag_match_count": 0,
            "remote_source_remote_cache_count": 0,
            "remote_source_origin_source_count": 0,
            "unknown_source_status_count": 0,
        }

        oldest_timestamp = datetime.now().astimezone()

        for item in results:
            if item.start_timestamp and item.start_timestamp < oldest_timestamp:
                oldest_timestamp = item.start_timestamp

            item_bytes = 0
            if item.bytes and item.bytes > 0:
                item_bytes = item.bytes

            data["bytes_processed"] += item_bytes
            if item.data_source not in (
                PrefixMetadataDataSource.local_source_ttl_cache,
                PrefixMetadataDataSource.local_source_etag_match,
            ):
                data["bytes_received"] += item_bytes

            # Count every request that actually hit the API (including 304 etag matches)
            if item.data_source != PrefixMetadataDataSource.local_source_ttl_cache:
                data["request_count"] += 1

            if item.data_source == PrefixMetadataDataSource.local_source_ttl_cache:
                data["local_source_ttl_cache_count"] += 1
            elif item.data_source == PrefixMetadataDataSource.local_source_etag_match:
                data["local_source_etag_match_count"] += 1
            elif item.data_source == PrefixMetadataDataSource.remote_source_remote_cache:
                data["remote_source_remote_cache_count"] += 1
            elif item.data_source == PrefixMetadataDataSource.remote_source_origin_source:
                data["remote_source_origin_source_count"] += 1
            elif item.data_source == PrefixMetadataDataSource.unknown_source_status:
                data["unknown_source_status_count"] += 1

        data["start_time"] = oldest_timestamp.timestamp()
        self.stats = QueueItemStats(**data)
