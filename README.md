# Chard

**Experimental!**

A simple async/await task queue for Django. One process, no threads, no
other dependencies.

It uses the Django ORM to keep track of tasks.

Parts of Chard were inspired by [dramatiq](https://github.com/Bogdanp/dramatiq)
and [django_dramatiq](https://github.com/Bogdanp/django_dramatiq).

## Installation

```sh
pip install django-chard
```

## Quickstart

First add `chard` anywhere in your `INSTALLED_APPS` setting and then run
the migrations:

```sh
python manage.py migrate
```

Create a file called `tasks.py` in one of your apps and define a task:

```python
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
```

To fire a task for the worker:

```python
my_task.send("gb")
```

Run the worker process and it will listen for new pending tasks:

```sh
python manage.py chardworker
```
