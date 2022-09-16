# Chard

Chard is a simple async/await background task queue for Django. One process,
no threads, no other dependencies.

It uses Django's ORM to keep track of tasks. **This is a new project under active development**.
PRs are welcome!

📖 [**Documentation**](https://chard.readthedocs.io/en/latest/)

📨 [**Sign up to the newsletter to get news and updates**](https://mailchi.mp/3b66d5565783/chard-newsletter)

🔗 [Check the example Django project](https://github.com/drpancake/chard-django-example)

## Requirements

- Python 3.8+
- Django 4.1+

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
# Note that all arguments must be JSON serializable.
my_task.send("gb")
```

Run the worker process and it will watch for new pending tasks:

```sh
python manage.py chardworker
```

To see a full example of Chard in action:

🔗 [Check the example Django project](https://github.com/drpancake/chard-django-example)

## Roadmap

- Return `Task.id` when firing a task so that you can check its status
- Figure out how to continually check for new pending tasks without hammering the DB too much
- Error reporting interface to hook up e.g. Sentry
- Simple monitoring dashboard
- Task scheduling

## Contributing

Please see [CONTRIBUTING](CONTRIBUTING.md) the contributing guidelines.

## License

Please see [LICENSE](LICENSE) for licensing details.
