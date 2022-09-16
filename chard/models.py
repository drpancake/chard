import uuid

from django.db import models


class Task(models.Model):
    class Status(models.TextChoices):
        """All possible task status values."""

        PENDING = "pending"
        """ The task is queued. """

        RUNNING = "running"
        """ The task is running. """

        FAILED = "failed"
        """ The task failed with an exception or it timed out. """

        DONE = "done"
        """ The task completed successfully. """

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    """Automatically assigned UUID."""

    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING
    )
    """The status of the task."""

    created_at = models.DateTimeField(auto_now_add=True)
    """When the task was created."""

    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    """When the task was last updated."""

    name = models.CharField(max_length=255)
    """The name of the task function e.g. `myapp.tasks.my_task`."""

    task_data = models.TextField()
    """JSON-encoded arguments for the task."""

    def __str__(self):
        return str(self.id)
