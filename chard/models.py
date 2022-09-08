import uuid

from django.db import models


class Task(models.Model):
    STATUS_PENDING = "pending"
    STATUS_RUNNING = "running"
    STATUS_FAILED = "failed"
    STATUS_DONE = "done"
    STATUSES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_RUNNING, "Running"),
        (STATUS_FAILED, "Failed"),
        (STATUS_DONE, "Done"),
    ]

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    status = models.CharField(
        max_length=10, choices=STATUSES, default=STATUS_PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    name = models.CharField(max_length=255)
    task_data = models.TextField()

    def __str__(self):
        return str(self.id)
