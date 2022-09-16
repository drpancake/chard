Quickstart
==========

First add ``chard`` anywhere in your ``INSTALLED_APPS`` setting and then run
the migrations::

  python manage.py migrate

Create a file called ``tasks.py`` inside one of your Django apps and define
a task:

..  code-block:: python

  import chard
  import httpx
  from asgiref.sync import sync_to_async

  from .models import MyModel

  @chard.task
  async def my_task(country_code):
      url = f"https://somewhere.com/some-api.json?country_code={country_code}"
      async with httpx.AsyncClient() as client:
          resp = await client.get(url)
          obj = resp.json()
      for item in obj["items"]:
          await sync_to_async(MyModel.objects.create)(
            country_code=country_code,
            item=item
          )

To fire a task for the worker:

..  code-block:: python

  # Note that all arguments must be JSON serializable.
  my_task.send("gb")

Run the worker process and it will watch for new pending tasks::

  python manage.py chardworker

Example project
---------------

To see a full example of Chard in action:

🔗 `Check the example Django project <https://github.com/drpancake/chard-django-example>`_