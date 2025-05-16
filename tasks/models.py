import enum
import uuid

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from enumfields.drf import EnumField

User = get_user_model()

class TaskStatus(enum.Enum):
    """
    Datatype for the status of a task
    """
    TODO = "todo"
    DOING = "doing"
    DONE = "done"
    ON_HOLD = "on hold"


class Task(models.Model):
    id = models.UUIDField(primary_key=True, unique=False, editable=False, default=uuid.uuid4)
    detail = models.TextField()
    priority = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    status = EnumField(TaskStatus, default=TaskStatus.TODO)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tasks")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-priority", "created_at"]
