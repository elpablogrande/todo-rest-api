# -*- coding: utf-8 -*-
"""
todo_list.views.py
Initial commit: Paul Anderson, 3/25/2018

Implements Django's "views" abstraction by subclassing Django REST Framework's "viewsets" classes.
Each subclass of ModelViewSet represents an endpoint in the API.

Counterintuitively, the Control layer of the MVC pattern is implemented here. It's really a control layer, not a view
layer.
"""

from __future__ import unicode_literals

# Create your views here.

from datetime import datetime
from todo_list.models import ToDoList, ParentTask, ChildTask
from rest_framework import viewsets, status
from rest_framework.decorators import list_route
from rest_framework.response import Response
from django.contrib.auth.models import User, Group
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BasicAuthentication

from todo_list.serializers import TodoListSerializer, ParentTaskSerializer, ChildTaskSerializer, \
    ChildTaskCompletionSerializer, ParentTaskCompletionSerializer, UserSerializer, GroupSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer

    #def list(self, request):
    #    """
    #    foo
    #    :param request:
    #    :return:
    #    """
    #    response = super(UserViewSet, self).list(self, request)
    def get_queryset(self):
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        user = self.request.user
        return User.objects.filter(username=user)


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class TodoListTaskViewSet(viewsets.ModelViewSet):
    """
    API endpoint providing access to todo lists.
    """
    queryset = ToDoList.objects.all()
    serializer_class = TodoListSerializer


class ParentTaskViewSet(viewsets.ModelViewSet):
    """
    API endpoint that hopefully works
    """
    queryset = ParentTask.objects.all()
    serializer_class = ParentTaskSerializer

    request = None
    format_kwarg = None

    def list(self, request):
        """
        Override ModelViewSet's "list" method to append the server's current datetime.
        This allows the front-end app to evaluate whether the task is past due at time of request
        based on the server's clock.
        :param request: Request data object
        :return: a Response object.
        """

        current_dtm = datetime.now()
        response = super(ParentTaskViewSet, self).list(request)
        for task in response.data:
            task['request_date'] = current_dtm

        return response

    @list_route(methods=['post'])
    def complete_task(self, request, pk=None):
        """
        A method for marking a child task complete.
        The @list_route decorator appends the method name to the URL and implements the code below.
        This allows the client to mark a task complete without requiring the other fields in a simplified PUT request.
        :param request:
        :param pk:
        :return:
        """
        serializer = ParentTaskCompletionSerializer(data=request.data)
        serializer_valid = serializer.is_valid()
        id_valid = False

        if serializer_valid:
            task_id = serializer.data['task_id']
            id_valid = ParentTask.objects.filter(id__exact=task_id).exists()

        if id_valid:
            # If valid, update the record in the database.
            completed_datetime = datetime.now()
            ParentTask.objects.filter(id__exact=task_id).update(task_completed_date=completed_datetime)

            # If the task has any "child" tasks, mark them all complete.
            incomplete_tasks = ChildTask.objects.filter(parent_task_id__exact=task_id,
                                                        child_task_completed_date__isnull=True)
            incomplete_tasks.update(child_task_completed_date=completed_datetime)

            # Return a response
            return Response({'status': 'Task completed',
                             'task_id': task_id,
                             'completed_datetime': completed_datetime})
        else:
            # The request did not pass validation; return a 400 header.
            if serializer.errors:
                error_response = serializer.errors
            else:
                error_response = {'status': 'Invalid Task ID'}
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)


class ChildTaskViewSet(viewsets.ModelViewSet):
    """
    API endpoint handling tasks that are children of a "parent" task, representing data in the ChildTask model.
    """
    queryset = ChildTask.objects.all()
    serializer_class = ChildTaskSerializer

    request = None
    format_kwarg = None

    def check_siblings_completed(self, parent_task_id):
        """
        Queries the database to find out whether the parent task's child tasks are all complete.
        :param parent_task_id: The ID of this child task's parent.
        :return: Boolean, True/False, all child tasks are marked complete.
        """
        siblings_completed = False

        incomplete_count = ChildTask.objects.filter(
            parent_task_id__exact=parent_task_id, child_task_completed_date__isnull=True
        ).count()

        if incomplete_count == 0:
            siblings_completed = True

        return siblings_completed

    def list(self, request):
        """
        Override ModelViewSet's "list" method to append the server's current datetime.
        This allows the front-end app to evaluate whether the task is past due at time of request
        based on the server's clock.
        :param request: Request data object
        :return: a Response object
        """
        current_dtm = datetime.now()
        response = super(ChildTaskViewSet, self).list(request)
        for child_task in response.data:
            child_task['request_date'] = current_dtm
        return response

    @list_route(methods=['post'])
    def complete_child_task(self, request, pk=None):
        """
        A method for marking a child task complete.
        The @list_route decorator appends the method name to the URL and implements the code below.
        This allows the client to mark a task complete without requiring the other fields in a simplified PUT request.
        :param request:
        :param pk:
        :return: a Response object
        """

        serializer = ChildTaskCompletionSerializer(data=request.data)

        # Validate the request.
        id_valid = False
        serializer_valid = serializer.is_valid()
        if serializer_valid:
            child_task_id = serializer.data['child_task_id']
            id_valid = ChildTask.objects.filter(id__exact=child_task_id).exists()

        if id_valid:
            # If valid, update the record in the database.

            completed_datetime = datetime.now()
            ChildTask.objects.filter(id__exact=child_task_id).update(child_task_completed_date=completed_datetime)
            parent_task_id = ChildTask.objects.values_list('parent_task_id', flat=True).get(pk=child_task_id)

            if self.check_siblings_completed(parent_task_id):
                # If no incomplete tasks remain, update the parent task as complete.
                completed_datetime = datetime.now()
                ParentTask.objects.filter(id__exact=parent_task_id).update(task_completed_date=completed_datetime)

            return Response({'status': 'Child task completed',
                             'child_task_id': child_task_id,
                             'completed_datetime': completed_datetime})
        else:
            # The request did not pass validation; return a 400 header.
            if serializer.errors:
                error_response = serializer.errors
            else:
                error_response = {'status': 'Invalid child task ID'}
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        """
        Override the ModelViewSet update method to add some controls.
        This method gets called when a PUT request to the API updates a child task.
        Because the request may signify the completion of a child task, we check to see if all the parent's child tasks
        are complete. If so, we mark the parent task as completed.
        :param request: The request body wrapped in a Model object
        :param pk: not implemented
        :return: a Response object
        """
        child_task = self.get_object()
        serializer = ChildTaskSerializer(data=request.data)
        parent_task_id = serializer.data['parent_task_id']
        if serializer.is_valid():
            # Request passed validation.
            response = super(ChildTaskViewSet, self).update(request, pk)

            # Because the child task may have been updated, we now check to see whether
            if self.check_siblings_completed(parent_task_id=child_task.parent_task_id):
                # If no incomplete tasks remain, update the parent task as complete.
                completed_datetime = datetime.now()
                ParentTask.objects.filter(id__exact=parent_task_id).update(task_completed_date=completed_datetime)

            return response
        else:
            # The request did not pass validation; return a 400 header.
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
