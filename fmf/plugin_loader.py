from functools import lru_cache
import inspect
from fmf.constants import PLUGIN_ENV, SUFFIX
from fmf.utils import log
import importlib
import os


class Plugin:
    """
    Main abstact class for FMF plugins
    """
    # you have to define extension list as class attribute e.g. [".py"]
    extensions = list()
    file_patters = list()

    def get_data(self, filename):
        """
        return python dictionary representation of metadata inside file (FMF structure)
        """
        raise NotImplementedError("Define own impementation")

    def put_data(
            self, filename, hierarchy, data, append_dict, modified_dict,
            deleted_items):
        """
        Write data in dictionary representation back to file
        """
        raise NotImplementedError("Define own impementation")


@lru_cache(maxsize=1)
def enabled_plugins():
    plugins = os.getenv(PLUGIN_ENV).split(",") if os.getenv(PLUGIN_ENV) else []
    plugin_list = list()
    for item in plugins:
        loader = importlib.machinery.SourceFileLoader(
            os.path.basename(item), item)
        module = importlib.util.module_from_spec(
            importlib.util.spec_from_loader(loader.name, loader)
        )
        loader.exec_module(module)
        for name, plugin in inspect.getmembers(module):
            if inspect.isclass(plugin) and plugin != Plugin and issubclass(
                    plugin, Plugin):
                plugin_list.append(plugin)
                log.info("Loaded plugin {}".format(plugin))
    return plugin_list


def get_suffixes():
    output = [SUFFIX]
    for item in enabled_plugins():
        output += item.extensions
    return output


def get_plugin_for_file(filename):
    extension = "." + filename.rsplit(".", 1)[1]
    for item in enabled_plugins():
        if extension in item.extensions:
            log.debug("File {} parsed by by plugin {}".format(filename, item))
            return item
