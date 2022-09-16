Configuration
=============

You can optionally place these in your ``settings.py``:

..  code-block:: python

  # How many tasks can run concurrently (default: 10)
  CHARD_MAX_CONCURRENT_TASKS = 50

  # How long a task can run until it is forcibly canceled - setting this to
  # to 0 means no timeout (default: 60)
  CHARD_TIMEOUT = 30
