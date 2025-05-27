from datetime import timedelta
import enum
import uuid

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.timezone import now
from enumfields import EnumField

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

    def __str__(self):
        return self.detail
    
    @property
    def humanized_time(self) -> str:
        diff = now() - self.created_at
        if diff < timedelta(minutes=1):
            return "Just now"
        elif diff < timedelta(hours=1):
            minutes = int(diff.total_seconds() / 60)
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        elif diff < timedelta(days=1):
            hours = int(diff.total_seconds() / 3600)
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif diff < timedelta(days=2):
            return "Yesterday"
        elif diff < timedelta(weeks=1):
            days = diff.days
            return f"{days} day{'s' if days > 1 else ''} ago"
        elif diff < timedelta(weeks=4):
            weeks = diff.days // 7
            return f"{weeks} week{'s' if weeks > 1 else ''} ago"
        else:
            return self.created_at.strftime("%b %d, %Y")
