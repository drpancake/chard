class NotAsyncException(Exception):
    def __init__(self, task_name):
        super().__init__(f"{task_name} is not an async function")


class UnknownTaskException(Exception):
    def __init__(self, task_name):
        super().__init__(f"Unknown task: {task_name}")


class SerializationException(Exception):
    def __init__(self, task_name):
        super().__init__(
            f"Task arguments must be JSON-serializable: {task_name}"
        )
