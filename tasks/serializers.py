from rest_framework import serializers

from api.serializers import EnumField
from tasks.models import Task, TaskStatus


class TaskSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.email")
    status = EnumField(enum_class=TaskStatus)

    class Meta:
        model = Task
        fields = ["id", "detail", "priority", "status", "user", "created_at"]


class TaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["detail", "priority"]


class TaskUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["detail", "priority"]
