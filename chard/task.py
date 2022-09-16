import json

from .types import AsyncFunction
from .exceptions import SerializationException


class TaskWrapper:
    fn: AsyncFunction

    def __init__(self, fn: AsyncFunction):
        self.fn = fn

    @property
    def task_name(self) -> str:
        return f"{self.fn.__module__}.{self.fn.__name__}"

    def send(self, *args, **kwargs) -> str:
        from chard.models import Task

        try:
            data = json.dumps(dict(args=args, kwargs=kwargs))
        except (TypeError, OverflowError):
            raise SerializationException(self.task_name)

        task = Task.objects.create(
            name=self.task_name,
            task_data=data,
        )
        return str(task.id)

    def __call__(self, *args, **kwargs):
        return self.fn(*args, **kwargs)

    def __str__(self):
        return f"TaskWrapper: {self.task_name}"


def is_task(obj):
    return isinstance(obj, TaskWrapper)


def task(fn: AsyncFunction) -> TaskWrapper:
    """
    Applying this decorator to an async function will turn it into a task
    object that will be discoverable by the Chard worker.
    """

    def decorator() -> TaskWrapper:
        return TaskWrapper(fn)

    return decorator()
