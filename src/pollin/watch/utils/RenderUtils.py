import os.path

class RenderUtils:
    """
    Utility class for rendering
    """

    @staticmethod
    def calc_relative_path(start_dir, target_dir):
        """
        Calculates the relative path between two directories
        :param start_dir root directory
        :param target_dir target directory (from which the relative path is being calculated)
        :return: relative path
        """
        rel_path = os.path.relpath(start_dir, start=target_dir)
        root_path = rel_path.replace(os.sep, '/')

        return root_path.replace(os.sep, '/')