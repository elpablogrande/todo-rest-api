# -*- coding: utf-8 -*-
"""
todo_list.models.py
Initial Commit: Paul Anderson, 3/25/2018

This module implements Django's Models abstraction; it creates the data model underlying the application.
Upon execution of Django app migration, it creates the tables in the database (in this case, the default SQLite3
database). In our app, it also provides an interface to the database for Django REST Framework's "serializers"
implementation.

Think of each class as a table in a SQL database, and each of the variables declared as the table's columns.
"""

from __future__ import unicode_literals
from django.db import models

# Create your models here.


class ToDoList(models.Model):
    """
    Each record represents a list of things to do.
    """

    list_name = models.CharField(max_length=50)
    list_description = models.CharField(max_length=1000)


class ParentTask(models.Model):
    """
    Each record represents a task nested within a todo list.
    Note that the "list" field is a foreign key to ToDoList.
    """

    todo_list_id = models.ForeignKey(ToDoList, related_name='tasks', on_delete=models.CASCADE)
    task_name = models.CharField(max_length=50)
    task_description = models.CharField(max_length=1000)
    task_due_date = models.DateTimeField(null=False)
    task_completed_date = models.DateTimeField(null=True)


class ChildTask(models.Model):
    """
    Each record represents a task that is a sub-task of a ParentTask record.
    Note that parent_task is a foreign key to ParentTask.
    """

    parent_task_id = models.ForeignKey(ParentTask, related_name='child_tasks', on_delete=models.CASCADE)
    child_task_name = models.CharField(max_length=50)
    child_task_description = models.CharField(max_length=1000)
    child_task_due_date = models.DateTimeField(null=False)
    child_task_completed_date = models.DateTimeField(null=True)
