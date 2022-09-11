import time
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
    max_tasks = getattr(settings, "CHARD_MAX_CONCURRENT_TASKS", 10)
    timeout = getattr(settings, "CHARD_TIMEOUT", 60)
    task_fns = discover_task_functions()
    task_models = {}
    tasks = []
    i = 0
    print(f"chard: {max_tasks} concurrent tasks, {timeout}s timeout")

    while True:
        # Create and run new tasks if we have capacity.
        capacity = max_tasks - len(tasks)
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
                tasks.append((task, time.time()))
        # Handle completed and failed tasks.
        for tup in tasks:
            task, started = tup
            if task.done():
                task_id = task.get_name()
                task_model = task_models.pop(task_id)
                tasks.remove(tup)
                try:
                    task.result()
                    await update_status(task_model, Task.STATUS_DONE)
                except BaseException as e:
                    if not isinstance(e, asyncio.CancelledError):
                        print(
                            f"[{task_model.name}] [{task_id}] Raised an "
                            f"exception: {e}"
                        )
                        traceback.print_exc()
                    await update_status(task_model, Task.STATUS_FAILED)
            elif timeout != 0 and (time.time() - started) >= timeout:
                # This schedules cancellation of the task on the next loop
                # and the `task.done()` check above will clean it up.
                task.cancel()
                print(
                    f"[{task_model.name}] [{task_id}] Timed out after"
                    f" {timeout} seconds"
                )
        # We need to periodically cleanup old DB connections.
        if i % 100 == 0:
            await sync_to_async(close_old_connections)()
            i = 0
        # Yield back to the event loop so that tasks can execute.
        await asyncio.sleep(0.5)
        i += 1


class Command(BaseCommand):
    help = "Runs the Chard worker."

    def handle(self, *args, **kwargs):
        asyncio.run(loop())
