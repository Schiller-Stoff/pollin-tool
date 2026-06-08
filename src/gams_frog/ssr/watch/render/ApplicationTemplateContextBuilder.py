from typing import Dict, Any


class ApplicationTemplateContextBuilder:
    """
    Responsible for building the context dictionary given as context to jinja2 templates.
    """

    def __init__(self, app_context):
        self.app_context = app_context

    def create(self, template_name: str, root_path: str, extra_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Builds the standard render context dictionary.
        :param template_name name of the jinja template
        :root_root_path relative path of the output file to the build root
        :param extra_context: Additional data specific to the current page (e.g., 'objects', 'object')
        """
        manifest = self.app_context.get_application_render_context().get_static_file_hash_mapping()
        project_data = self.app_context.get_app_data_store().get_project_data()

        def resolve_path(file_path: str | None = None) -> str:
            """
            Builds the relative path from the project's web root for given file_path.
            """
            base_path = root_path.rstrip('/')

            if file_path is None:
                return base_path + "/"

            if file_path.startswith("/"):
                return f"{base_path}{file_path}"

            return f"{base_path}/{file_path}"

        def asset_helper(asset_path: str) -> str:
            """
            Resolves the asset hash and automatically prepends the correct root and static path.
            Bypasses manipulation for absolute external URLs.
            """
            # 1. Escape hatch for external URLs (CDNs)
            if asset_path.startswith(('http://', 'https://', '//')):
                return asset_path
            # 2. Get the hashed filename (or fallback to original for vendor files/dev mode)
            resolved_filename = manifest.get(asset_path, asset_path)
            # 3. Cleanly concatenate the paths
            # .rstrip('/') ensures we don't accidentally create double slashes like //static/
            base_path = root_path.rstrip('/')
            # Strip leading slash from asset_path if the dev accidentally added one
            clean_filename = resolved_filename.lstrip('/')

            return f"{base_path}/static/{clean_filename}"

        # 1. Build the base framework data
        base_context = {
            'project': project_data,
            'env': self.app_context.get_config().ENV.to_dict(),
            '_template_name': template_name.replace(".j2", ""),
            '_template_file_name': template_name,
            '_root_path': root_path,
            'manifest': manifest
        }

        # 2. Inject page-specific data (like 'objects' or 'object')
        if extra_context:
            base_context.update(extra_context)

        # 3. Return the strict namespace structure
        return {
            "context": base_context,
            "fn": {
                'asset': asset_helper,
                'root': resolve_path
            }
        }

