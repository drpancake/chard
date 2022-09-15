import json

from .types import AsyncFunction
from .exceptions import SerializationException


class TaskWrapper:
    fn: AsyncFunction
    task_name: str

    def __init__(self, fn: AsyncFunction, *, task_name: str):
        self.fn = fn
        self.task_name = task_name

    def send(self, *args, **kwargs) -> None:
        from chard.models import Task

        try:
            data = json.dumps(dict(args=args, kwargs=kwargs))
        except (TypeError, OverflowError):
            raise SerializationException(self.task_name)

        Task.objects.create(
            name=self.task_name,
            task_data=data,
        )

    def __call__(self, *args, **kwargs):
        return self.fn(*args, **kwargs)


def is_task(obj):
    return isinstance(obj, TaskWrapper)


def task(fn=None):
    def decorator(fn: AsyncFunction) -> TaskWrapper:
        task_name = f"{fn.__module__}.{fn.__name__}"
        return TaskWrapper(fn, task_name=task_name)

    if fn is None:
        return decorator
    return decorator(fn)
