import json
import asyncio
from asgiref.sync import sync_to_async

from django.core.management.base import BaseCommand

from chard.discover import discover_task_functions
from chard.models import Task
from chard.exceptions import UnknownTaskException

TASKS_PER_LOOP = 10


async def run_task(task_id, fn, task_data):
    obj = json.loads(task_data)
    args = obj["args"]
    kwargs = obj["kwargs"]
    try:
        await fn(*args, **kwargs)
        return task_id, None
    except Exception as e:
        return task_id, e


async def loop():
    task_fns = discover_task_functions()
    print(f"loaded {len(task_fns)} task functions")

    while True:
        awaitables = []
        tasks = {}
        qs = Task.objects.filter(status=Task.STATUS_PENDING).order_by(
            "created_at"
        )
        async for task in qs[:TASKS_PER_LOOP]:
            print(f"[{task.name}] [{task.id}] queueing")
            tasks[task.id] = task
            fn = task_fns.get(task.name)
            if not fn:
                raise UnknownTaskException(task.name)
            awaitables.append(run_task(task.id, fn, task.task_data))

        if awaitables:
            print(f"running {len(awaitables)} tasks")
            for awaitable in asyncio.as_completed(awaitables):
                task_id, exc = await awaitable
                task = tasks[task_id]
                if exc:
                    task.status = Task.STATUS_FAILED
                else:
                    task.status = Task.STATUS_DONE
                await sync_to_async(task.save)(
                    update_fields=["status", "updated_at"]
                )
                print(f"[{task.name}] [{task.id}] {task.status=} | {exc=}")


class Command(BaseCommand):
    help = "Runs the Chard worker."

    def handle(self, *args, **kwargs):
        asyncio.run(loop())
