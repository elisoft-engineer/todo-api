from django.shortcuts import get_object_or_404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.permissions import IsOwner
from tasks.models import TaskStatus, Task
from tasks.serializers import TaskCreateSerializer, TaskSerializer, TaskUpdateSerializer


class TaskList(APIView):
    """
    Endpoint to handle both fetching all tasks and creating a new task.
    """

    allowed_methods = ['GET', 'POST']
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TaskCreateSerializer
        return TaskSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="status",
                type=OpenApiTypes.STR,
                required=True,
                description="Filter tasks by their status"
            ),
        ]
    )
    def get(self, request):
        """
        Handle GET request to fetch tasks.
        """
        status_str = request.query_params.get('status', None)
        if not status_str in [s.value for s in TaskStatus]:
            return Response({"detail": "Invalid task status was parsed"}, status=status.HTTP_400_BAD_REQUEST)
        task_status = TaskStatus(value=status_str)
        tasks = request.user.tasks.all().filter(status=task_status)
        serializer = self.get_serializer_class()(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Handle POST request to create a new project.
        """
        serializer = self.get_serializer_class()(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskDetail(APIView):
    """
    Retrieve, update, or delete a task instance.
    """

    allowed_methods = ['GET', 'PUT', 'PATCH', 'DELETE']
    permission_classes = [IsAuthenticated, IsOwner]

    def get_serializer_class(self):
        if self.request.method == 'PUT':
            return TaskUpdateSerializer
        elif self.request.method == 'GET':
            return TaskSerializer
        return None

    def get_object(self, pk):
        obj = get_object_or_404(Task, pk=pk)
        self.check_object_permissions(self.request, obj)
        return obj

    def get(self, request, pk):
        """
        Retrieve task details.
        """
        task = self.get_object(pk)
        serializer = self.get_serializer_class()(task)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        """
        Update a task.
        """
        task = self.get_object(pk)
        serializer = self.get_serializer_class()(task, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="to-onhold",
                type=OpenApiTypes.BOOL,
                required=False,
                description="Whether to push task to `on hold`"
            )
        ]
    )
    def patch(self, request, pk):
        task = self.get_object(pk)
        on_hold = request.query_params.get("to-onhold", None)
        if on_hold and str(on_hold).lower() in ['true', '1', 'yes']:
            if task.status in [TaskStatus.DONE, TaskStatus.ON_HOLD]:
                return Response({"detail": f"Task is already {task.status.value}"})
            else:
                task.status = TaskStatus.ON_HOLD
                task.save()
                return Response({"detail": "Task has been put on-hold"})
        if task.status == TaskStatus.TODO:
            task.status = TaskStatus.DOING
        elif task.status == TaskStatus.DOING:
            task.status = TaskStatus.DONE
        else:
            return Response(
                {
                    "detail": f"Task is {'already ' if task.status == TaskStatus.DONE else ''}{task.status.value}"
                },
                status=status.HTTP_200_OK
            )
        task.save()
        return Response({"detail": f"Task has been moved to `{task.status.value}`"}, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        """
        Delete a task.
        """
        task = self.get_object(pk)
        task.delete()
        return Response({"detail": "Task deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
