from typing import Dict


class ApplicationRenderContext:
    """
    Stores runtime variables for the rendering process
    """

    _static_file_hash_mapping: Dict[str,str]
    """
    Contains mapping between original filepaths (in src directory) and the hashed values e.g. manifest.json -> manifest.123456.json    
    """

    def __init__(self):
        self._static_file_hash_mapping = {}

    def set_static_file_hash_mapping(self, static_file_hash_mapping: Dict[str,str]):
        self._static_file_hash_mapping = static_file_hash_mapping

    def get_static_file_hash_mapping(self):
        return self._static_file_hash_mapping
