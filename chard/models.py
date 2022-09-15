import uuid

from django.db import models


class Task(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending"
        RUNNING = "running"
        FAILED = "failed"
        DONE = "done"

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    name = models.CharField(max_length=255)
    task_data = models.TextField()

    def __str__(self):
        return str(self.id)
