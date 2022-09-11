import json
import asyncio
import traceback
from asgiref.sync import sync_to_async

from django.db import close_old_connections
from django.core.management.base import BaseCommand
from django.conf import settings

from chard.discover import discover_task_functions
from chard.models import Task
from chard.exceptions import UnknownTaskException


async def run_task(fn, task_data):
    obj = json.loads(task_data)
    args = obj["args"]
    kwargs = obj["kwargs"]
    await fn(*args, **kwargs)


async def update_status(task_model, status):
    task_model.status = status
    await sync_to_async(task_model.save)(
        update_fields=["status", "updated_at"]
    )


async def loop():
    max_concurrent_tasks = getattr(settings, "CHARD_MAX_CONCURRENT_TASKS", 10)
    task_fns = discover_task_functions()
    task_models = {}
    tasks = []
    i = 0
    print(f"chard: starting with {max_concurrent_tasks} concurrent tasks")

    while True:
        # Create and run new tasks if we have capacity.
        capacity = max_concurrent_tasks - len(tasks)
        if capacity > 0:
            qs = (
                Task.objects.select_for_update(skip_locked=True)
                .filter(status=Task.STATUS_PENDING)
                .order_by("created_at")[:capacity]
            )
            async for task_model in qs:
                task_id = str(task_model.id)
                task_models[task_id] = task_model
                fn = task_fns.get(task_model.name)
                if not fn:
                    raise UnknownTaskException(task_model.name)
                await update_status(task_model, Task.STATUS_RUNNING)

                task = asyncio.create_task(run_task(fn, task_model.task_data))
                task.set_name(task_id)
                tasks.append(task)
        # Handle completed and failed tasks.
        for task in tasks:
            if task.done():
                task_id = task.get_name()
                task_model = task_models.pop(task_id)
                tasks.remove(task)
                try:
                    task.result()
                    await update_status(task_model, Task.STATUS_DONE)
                except Exception as e:
                    print(
                        f"[{task_id}] [{task_model.name}] Raised an "
                        f"exception: {e}"
                    )
                    traceback.print_exc()
                    await update_status(task_model, Task.STATUS_FAILED)
        # We need to periodically cleanup old DB connections.
        if i % 100 == 0:
            await sync_to_async(close_old_connections)()
            i = 0
        # Yield back to the event loop so that tasks can execute.
        await asyncio.sleep(0.1)
        i += 1


class Command(BaseCommand):
    help = "Runs the Chard worker."

    def handle(self, *args, **kwargs):
        asyncio.run(loop())
