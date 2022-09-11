from django.contrib import admin

from .models import Task


class TaskAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "status", "created_at", "updated_at")
    search_fields = ("id", "name")
    ordering = ("-created_at",)


admin.site.register(Task, TaskAdmin)
