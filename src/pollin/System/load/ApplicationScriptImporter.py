import importlib
import secrets
import string
import sys
from os import PathLike


class ApplicationScriptImporter:
    """
    Class to import scripts from the project script directory
    Allows to load scripts dynamically
    """


    project_scripts_dir: PathLike
    """
    The directory where the project scripts are stored
    """

    imported_module: str | None
    """
    The module that has been imported
    """


    def __init__(self, project_scripts_dir: PathLike):
        self.project_scripts_dir = project_scripts_dir

        if self.project_scripts_dir.exists():
            # TODO add logging
            # TODO definition of extends.py should be in config class?
            demo_script = self.project_scripts_dir / "extends.py"
            if demo_script.exists():
                self.imported_module = ApplicationScriptImporter.load_module(demo_script)
        else:
            self.imported_module = None



    def get_function(self, script_name):
        """
        loads a script from the project script directory

        :param script_name: name of the script to load
        :return: loaded module OR None if the script could not be loaded
        """
        if self.imported_module is None:
            return None

        try:
            # dynamically access specific function
            return self.imported_module.__getattribute__(script_name)
        except AttributeError:
            return None





    @staticmethod
    def gensym(length=32, prefix="gensym_"):
        """
        generates a fairly unique symbol, used to make a module name,
        used as a helper function for load_module

        :return: generated symbol
        """
        alphabet = string.ascii_uppercase + string.ascii_lowercase + string.digits
        symbol = "".join([secrets.choice(alphabet) for i in range(length)])

        return prefix + symbol


    @staticmethod
    def load_module(source, module_name=None):
        """
        reads file source and loads it as a module

        :param source: file to load
        :param module_name: name of module to register in sys.modules
        :return: loaded module
        """

        if module_name is None:
            module_name = ApplicationScriptImporter.gensym()

        spec = importlib.util.spec_from_file_location(module_name, source)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        return module
