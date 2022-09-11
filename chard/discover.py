import asyncio
import importlib
from inspect import getmembers
import pkgutil

from django.apps import apps
from django.utils.module_loading import module_has_submodule

from .task import is_task
from .exceptions import NotAsyncException


def is_package(module):
    return hasattr(module, "__path__")


def get_submodules(package):
    submodules = []
    package_path = package.__path__
    prefix = package.__name__ + "."
    for _, module_name, _ in pkgutil.walk_packages(package_path, prefix):
        imported_submodule = importlib.import_module(module_name)
        submodules.append(imported_submodule)
    return submodules


def discover_task_functions():
    task_module = "tasks"
    app_configs = []
    for conf in apps.get_app_configs():
        if module_has_submodule(conf.module, task_module):
            app_configs.append((conf, task_module))
    modules = []
    for conf, task_module in app_configs:
        module = conf.name + "." + task_module
        imported_module = importlib.import_module(module)
        if not is_package(imported_module):
            modules.append(imported_module)
        else:
            submodules = get_submodules(imported_module)
            for submodule in submodules:
                modules.append(submodule)
    fns = {}
    for module in modules:
        for name, task_wrapper in getmembers(module, is_task):
            task_name = task_wrapper.task_name
            fn = task_wrapper.fn
            if not asyncio.iscoroutinefunction(fn):
                raise NotAsyncException(task_name)
            fns[task_name] = fn
    print(f"chard: loaded {len(fns)} task functions")
    for task_name in fns.keys():
        print(f"--> {task_name}")
    return fns
