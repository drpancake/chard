import json

from .exceptions import SerializationException


class TaskWrapper:
    def __init__(self, fn, *, task_name):
        self.fn = fn
        self.task_name = task_name

    @property
    def is_chard_task(self):
        return True

    def send(self, *args, **kwargs):
        from chard.models import Task

        try:
            data = json.dumps(dict(args=args, kwargs=kwargs))
        except (TypeError, OverflowError):
            raise SerializationException(self.task_name)

        Task.objects.create(
            name=self.task_name,
            task_data=data,
        )


def task(fn=None):
    def decorator(fn):
        task_name = f"{fn.__module__}.{fn.__name__}"
        return TaskWrapper(fn, task_name=task_name)

    if fn is None:
        return decorator
    return decorator(fn)
