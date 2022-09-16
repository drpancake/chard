API
===

Task decorator
--------------

.. autofunction:: chard.task

----

Apply it to any async function inside a Django apps's ``tasks.py`` file like
this:

.. code-block:: python

    import chard
    import asyncio

    @chard.task
    async def my_task(i):
         print(i)
         await asyncio.sleep(1)

The resulting task object can be used to queue a new task for the worker
like this:

.. code-block:: python

   my_task.send(123)

You can also call it synchronously:

.. code-block:: python

   await my_task(123)

Queueing a task returns a UUID that can be used to retrieve the corresponding
``Task`` model instance:

.. code-block:: python

   from chard.models import Task

   task_id = my_task.send(123)
   task = Task.objects.get(id=task_id)
   task.status # => 'pending'

Task model
----------

.. autoclass:: chard.models.Task
   :members:
   :exclude-members: DoesNotExist, MultipleObjectsReturned

----

How to count the number of pending tasks:

.. code-block:: python

   from chard.models import Task

   Task.objects.filter(status=Task.Status.PENDING).count() # => 5

Fetch a specific task:

.. code-block:: python

   from chard.models import Task

   Task.objects.get(id="76bae380-d8b3-424e-8ce9-d70196e0fa7d")