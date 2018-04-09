"""
todo_list.serializers.py
Initial commit: Paul Anderson, 3/25/2018

Implementation of Django REST Framework's "serializers" API
See framework documentation: http://www.django-rest-framework.org/api-guide/serializers/
Performs JSON serialization and deserialization to interface the API views with the underlying data model.

"""
from todo_list.models import ToDoList, ParentTask, ChildTask
from django.contrib.auth.models import User, Group
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'url', 'username', 'email', 'groups')


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')


class ChildTaskSerializer(serializers.ModelSerializer):
    """
    Extends the DRF ModelSerializer class to provide a custom serializer for "todo" tasks that are children of a
    parent task
    """

    class Meta:
        model = ChildTask
        fields = ('url',
                  'id',
                  'parent_task_id',
                  'child_task_name',
                  'child_task_description',
                  'child_task_due_date',
                  'child_task_completed_date',
                  )

class ChildTaskCompletionSerializer(serializers.Serializer):
    """
    A special Serializer subclass for updating completion of child tasks.
    """
    child_task_id = serializers.IntegerField()


class ParentTaskCompletionSerializer(serializers.Serializer):
    """
    A special Serializer subclass for updating task completion.
    """
    task_id = serializers.IntegerField()


class ParentTaskSerializer(serializers.ModelSerializer):

    # DRF provides for nested serializers
    child_tasks = ChildTaskSerializer(many=True, read_only=True)

    class Meta:
        model = ParentTask
        fields = ('url',
                  'id',
                  'todo_list_id',
                  'task_name',
                  'task_description',
                  'task_due_date',
                  'task_completed_date',
                  'child_tasks'
                  )


class TodoListSerializer(serializers.ModelSerializer):
    """
    Extends the DRF ModelSerializer class representing a to-do list.
    """
    tasks = ParentTaskSerializer(many=True, read_only=True)

    class Meta:
        model = ToDoList
        fields = ('url',
                  'id',
                  'list_name',
                  'list_description',
                  'tasks'
                  )
