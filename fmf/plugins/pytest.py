from fmf.plugin_loader import Plugin
from fmf.utils import log
from fmf_metadata.pytest_collector import collect
from fmf_metadata.constants import PYTEST_DEFAULT_CONF
from fmf_metadata.base import _Test, _TestCls, define_undefined
from fmf_metadata.base import FMF
import importlib
import inspect
import re
import os
from multiprocessing import Process, Queue

_ = FMF


class Pytest(Plugin):
    extensions = [".py"]
    file_patters=["test.*"]

    @staticmethod
    def update_data(store_dict, func, config):
        keys = []
        filename = os.path.basename(func.fspath)
        if func.cls:
            cls = _TestCls(func.cls, filename)
            keys.append(cls.name)
        else:
            cls = _TestCls(None, filename)
        test = _Test(func)
        # normalise test name to pytest identifier
        test.name = re.search(
            f".*({os.path.basename(func.function.__name__)}.*)", func.name
        ).group(1)
        # TODO: removed str_normalise(...) will see what happen
        keys.append(test.name)
        define_undefined(store_dict, keys, config, filename, cls, test)
        return store_dict

    def get_data(self, file_name):
        def call_collect(queue, file_name):
            """
            have to call in separate process, to avoid problems with pytest multiple collectitons
            when called twice on same data test list is empty because already imported
            """
            out = dict()

            for item in collect([file_name]):
                self.update_data(store_dict=out, func=item,
                                 config=PYTEST_DEFAULT_CONF)
                log.info("Processing Item: {}".format(item.function))
            queue.put(out)

        process_queue = Queue()
        process = Process(target=call_collect,
                          args=(process_queue, file_name,))
        process.start()
        out = process_queue.get()
        process.join()
        if out:
            return out
        return None

    @staticmethod
    def import_test_module(filename):
        loader = importlib.machinery.SourceFileLoader(
            os.path.basename(filename), filename)
        module = importlib.util.module_from_spec(
            importlib.util.spec_from_loader(loader.name, loader)
        )
        loader.exec_module(module)
        return module

    def put_data(
            self, filename, hierarchy, data, append_dict, modified_dict,
            deleted_items):
        module = self.import_test_module(filename)
        where = module
        for item in hierarchy:
            where = getattr(where, item.lstrip("/"))
        lines, start_line = inspect.getsourcelines(where)
        spaces = re.match(r"(^\s*)", lines[0]).groups()[0]
        # try to find if already defined
        with open(filename, "r") as f:
            contents = f.readlines()
        for k in deleted_items:
            for num, line in enumerate(lines):
                if re.match(r"{}.*@FMF\.{}".format(spaces, k), line):
                    contents.pop(start_line + num - 1)
        for k, v in modified_dict.items():
            for num, line in enumerate(lines):
                if re.match(r"{}.*@FMF\.{}".format(spaces, k), line):
                    contents.pop(start_line + num - 1)
            append_dict[k] = v
        for k, v in append_dict.items():
            contents.insert(start_line, """{}@FMF.{}({})\n""".format(spaces,
                                                                     k, repr(v)[1:-1] if isinstance(v, list) else repr(v)))
        with open(filename, "w") as f:
            f.writelines(contents)
