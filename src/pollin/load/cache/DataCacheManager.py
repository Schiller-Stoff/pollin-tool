import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
import hashlib
from email.utils import formatdate, parsedate_to_datetime
from pollin.init.ApplicationContext import ApplicationContext
from pollin.init.config.ApplicationExternalConfig import ApplicationExternalConfig


class DataCacheManager:
    """Manages local caching of GAMS API data"""

    def __init__(self, app_context: ApplicationContext):
        self.app_context = app_context
        self.cache_config = app_context.get_config().cache
        self._ensure_cache_dir()

    def _ensure_cache_dir(self):
        """Ensure cache directory exists"""
        self.cache_config.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_key(self, project: str, host: str) -> str:
        """Generate cache key based on project and host"""
        key_string = f"{project}:{host}"
        return hashlib.md5(key_string.encode()).hexdigest()

    def _get_cache_metadata(self) -> Dict[str, Any]:
        """Get cache metadata (timestamps, keys, etc.)"""
        if not self.cache_config.cache_metadata_file.exists():
            return {}

        try:
            with open(self.cache_config.cache_metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.warning(f"Failed to read cache metadata: {e}")
            return {}

    def _save_cache_metadata(self, metadata: Dict[str, Any]):
        """Save cache metadata"""
        try:
            with open(self.cache_config.cache_metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Failed to save cache metadata: {e}")

    def _format_timestamp(self, dt: datetime) -> str:
        """Format datetime to HTTP date format (RFC 2822)"""
        # formatdate expects timestamp in seconds, usegmt=True for GMT
        return formatdate(dt.timestamp(), usegmt=True)

    def _parse_timestamp(self, timestamp_str: str) -> datetime:
        """Parse HTTP date format back to datetime"""
        logging.error(f"Parsing timestamp: {timestamp_str}")
        return parsedate_to_datetime(timestamp_str)

    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cache is still valid"""

        if not self.cache_config.enabled:
            return False

        metadata = self._get_cache_metadata()
        cache_info = metadata.get(cache_key)

        if not cache_info:
            logging.debug(f"Cache invalid: No cache metadata found for key {cache_key}. Cache invalid.")
            return False

        # cache must invalidate if host has changed
        if cache_info.get('host') != self.app_context.get_config().gams_host:
            logging.debug(f"Cache invalid: host has changed from {cache_info.get('host')} to {self.app_context.get_config().gams_host}")
            return False

        # cache must invalidate if object count has changed
        if cache_info.get(ApplicationExternalConfig.MODE_LOAD_OBJECT_COUNT_RESTRICTION) != self.app_context.get_config().project_external_config.get_obj_count_restriction():
            logging.debug(f"Cache invalid: object count restriction has changed from {cache_info.get(ApplicationExternalConfig.MODE_LOAD_OBJECT_COUNT_RESTRICTION)} to {self.app_context.get_config().project_external_config.get_obj_count_restriction()}")
            return False

        # required object arrays must contain same strings
        for obj_id in self.app_context.get_config().project_external_config.get_obj_required():
            if obj_id not in cache_info.get(ApplicationExternalConfig.MODE_LOAD_OBJECTS_REQUIRED, []):
                logging.debug(f"Cache invalid: required object '{obj_id}' is not in cached required objects {cache_info.get(ApplicationExternalConfig.MODE_LOAD_OBJECTS_REQUIRED, [])}")
                return False
        # also compare lengths to catch removed required objects
        if len(self.app_context.get_config().project_external_config.get_obj_required() or []) != len(cache_info.get(ApplicationExternalConfig.MODE_LOAD_OBJECTS_REQUIRED, [])):
            logging.debug(f"Cache invalid: number of required objects has changed from {cache_info.get(ApplicationExternalConfig.MODE_LOAD_OBJECTS_REQUIRED, [])} to {self.app_context.get_config().project_external_config.get_obj_required()}")
            return False

        try:
            cached_time = cache_info.get('timestamp')
            # cached_time = "Thu, 01 Jan 1970 00:00:02 GMT"
            project_abbr = self.app_context.get_config().project
            modified_since = self.app_context.get_pyrilo().project_modified_since(
                project_abbr=project_abbr,
                last_modified=str(cached_time)
            )

            # if the data has not changed since cached_time, the cache is valid
            cache_is_valid = not modified_since

            if not cache_is_valid:
                logging.debug(f"***Cache invalid: Encountered modified data for project {project_abbr} since {cached_time}. Cache invalid. ***")

            return cache_is_valid

        except (ValueError, KeyError) as e:
            logging.warning(f"Cache invalid: Invalid timestamp in cache metadata: {e}")
            return False


    def get_cached_objects(self, project: str) -> Optional[List[dict[str,str]]]:
        """Retrieve cached digital objects if valid"""
        if not self.cache_config.enabled:
            return None

        host = self.app_context.get_config().gams_host
        cache_key = self._get_cache_key(project, host)

        if not self._is_cache_valid(cache_key):
            logging.info(f"Cache invalid or expired for project {project}")
            return None

        cache_file = self.cache_config.cache_dir / f"objects_{cache_key}.json"

        if not cache_file.exists():
            return None

        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)

            # Convert back to DigitalObjectViewModel instances
            objects = []
            for obj_data in cached_data:
                digital_object = obj_data
                objects.append(digital_object)

            logging.info(f"Loaded {len(objects)} objects from cache for project {project}")
            return objects

        except Exception as e:
            logging.error(f"Failed to load cached objects: {e}")
            return None

    def cache_objects(self, project: str, objects: List[dict[str,str]]):
        """Cache digital objects"""
        if not self.cache_config.enabled:
            return

        host = self.app_context.get_config().gams_host
        cache_key = self._get_cache_key(project, host)
        cache_file = self.cache_config.cache_dir / f"objects_{cache_key}.json"

        try:
            # Convert objects to serializable format
            serializable_objects = [obj for obj in objects]

            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(serializable_objects, f, indent=2, ensure_ascii=False)

            # Update metadata
            metadata = self._get_cache_metadata()
            metadata[cache_key] = {
                'project': project,
                'host': host,
                'timestamp': self._format_timestamp(datetime.now()),
                ApplicationExternalConfig.MODE_LOAD_OBJECT_COUNT_RESTRICTION: self.app_context.get_config().project_external_config.get_obj_count_restriction(),
                ApplicationExternalConfig.MODE_LOAD_OBJECTS_REQUIRED: self.app_context.get_config().project_external_config.get_obj_required()
            }
            self._save_cache_metadata(metadata)

            logging.info(f"Cached {len(objects)} objects for project {project}")

        except Exception as e:
            logging.error(f"Failed to cache objects: {e}")

    def get_cached_project_data(self, project: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached project metadata"""
        if not self.cache_config.enabled:
            return None

        host = self.app_context.get_config().gams_host
        cache_key = self._get_cache_key(project, host)

        if not self._is_cache_valid(cache_key):
            return None

        cache_file = self.cache_config.cache_dir / f"project_{cache_key}.json"

        if not cache_file.exists():
            return None

        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Failed to load cached project data: {e}")
            return None

    def cache_project_data(self, project: str, project_data: Dict[str, Any]):
        """Cache project metadata"""
        if not self.cache_config.enabled:
            return

        host = self.app_context.get_config().gams_host
        cache_key = self._get_cache_key(project, host)
        cache_file = self.cache_config.cache_dir / f"project_{cache_key}.json"

        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, indent=2, ensure_ascii=False)

            logging.info(f"Cached project data for {project}")

        except Exception as e:
            logging.error(f"Failed to cache project data: {e}")

    def invalidate_cache(self, project: str):
        """Invalidate cache for a specific project"""
        host = self.app_context.get_config().gams_host
        cache_key = self._get_cache_key(project, host)

        # Remove cache files
        for cache_file in [
            self.cache_config.cache_dir / f"objects_{cache_key}.json",
            self.cache_config.cache_dir / f"project_{cache_key}.json"
        ]:
            if cache_file.exists():
                cache_file.unlink()

        # Update metadata
        metadata = self._get_cache_metadata()
        if cache_key in metadata:
            del metadata[cache_key]
            self._save_cache_metadata(metadata)

        logging.info(f"Invalidated cache for project {project}")

    def clear_all_cache(self):
        """Clear all cached data"""
        if self.cache_config.cache_dir.exists():
            import shutil
            shutil.rmtree(self.cache_config.cache_dir)
            self._ensure_cache_dir()

        logging.info("Cleared all cache data")