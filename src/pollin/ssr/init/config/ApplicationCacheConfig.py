from dataclasses import dataclass
from pathlib import Path

@dataclass
class ApplicationCacheConfig:
    """Configuration for local data caching"""
    cache_dir: Path
    enabled: bool = True

    @property
    def objects_cache_file(self) -> Path:
        return self.cache_dir / "objects_cache.json"

    @property
    def project_cache_file(self) -> Path:
        return self.cache_dir / "project_cache.json"

    @property
    def cache_metadata_file(self) -> Path:
        return self.cache_dir / "cache_metadata.json"