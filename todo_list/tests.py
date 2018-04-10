# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from todo_list.views import ParentTaskViewSet, ChildTaskViewSet
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory, APITestCase
from rest_framework import status
from datetime import datetime, timedelta

# Create your tests here.

class TodoListViewSetTestCase(APITestCase):

    def test_create_list(self):
        """
        Unit test to ensure we can create a list record.
        :return: None
        """
        '''Arrange'''
        url = '/v1/lists/'
        data = {
            "list_name": "A List",
            "list_description": "Things I need to do"
        }

        '''Act'''
        response = self.client.post(url, data, format='json')
        id = response.data['id']
        get_url = url + str(id) + '/'
        get_response = self.client.get(get_url)

        '''Assert'''
        # POST was successful
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # GET successfully retrieved created resource
        self.assertEqual(get_response.status_code, 200)


    def test_get_list_root(self):
        """
        Unit test to check GET requests to the lists endpoint
        :return: None
        """
        '''Arrange'''
        url = '/v1/lists/'
        '''Act'''
        response = self.client.get(url)
        '''Assert'''
        self.assertEqual(response.status_code, 200)


class ParentTaskViewSetTestCase(APITestCase):

    def test_create_task(self):
        """
        Unit test to ensure we can create and delete a task record
        :return: None
        """
        '''Arrange'''
        # Create a list
        list_url = '/v1/lists/'

        list_data = {
            "list_name": "Yet Another List",
            "list_description": "Still more things I need to do"
        }

        list_response = self.client.post(list_url, list_data, format='json')
        list_id = list_response.data['id']

        # Create a task
        url = '/v1/tasks/'
        data = {
            "todo_list_id": list_id,
            "task_name": "Do a little dance",
            "task_description": "Make a little love, get down tonight.",
            "task_due_date": "2018-04-20T12:00:00"
        }

        '''Act'''
        post_response = self.client.post(url, data, format='json')
        task_id = post_response.data['id']
        get_url = url + str(task_id) + '/'
        get_response = self.client.get(get_url)

        # Delete the task
        delete_response = self.client.delete(path=get_url)

        '''Assert'''
        # POST successful
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        # GET successful
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        # DELETE successful
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)

    def test_complete_task(self):
        """
        Unit test the complete_task endpoint and method.
        :return: None
        """
        '''Arrange'''
        # Create a list
        list_url = '/v1/lists/'

        list_data = {
            "list_name": "Yet Another List",
            "list_description": "Still more things I need to do"
        }

        list_response = self.client.post(list_url, list_data, format='json')
        list_id = list_response.data['id']

        # Create a task
        url = '/v1/tasks/'
        data = {
            "todo_list_id": list_id,
            "task_name": "Do a little dance",
            "task_description": "Make a little love, get down tonight.",
            "task_due_date": "2018-04-20T12:00:00"
        }

        post_response = self.client.post(url, data, format='json')
        task_id = post_response.data['id']

        # Create a child task
        child_data = {
            "parent_task_id": task_id,
            "child_task_name": "square dance",
            "child_task_description": "swing yer partner round and round",
            "child_task_due_date": "2018-03-29T12:00:00"
        }
        child_url = '/v1/child_tasks/'
        child_response = self.client.post(child_url, child_data, format='json')

        '''Act'''
        # Close the task
        close_url = '/v1/tasks/complete_task/'
        close_postdata = {"task_id": task_id}
        close_response = self.client.post(close_url, close_postdata, format='json')

        # Query the parent record for its completion date
        parent_task_id = post_response.data['id']
        parent_get_url = url + str(parent_task_id) + '/'
        parent_get_response = self.client.get(parent_get_url)
        parent_completion_str = parent_get_response.data['task_completed_date']
        parent_completion_str = parent_completion_str[:19]
        parent_completion_date = datetime.strptime(parent_completion_str[:-1], '%Y-%m-%dT%H:%M:%S')


        # Query the child record for its completion date
        child_task_id = child_response.data['id']
        child_get_url = '/v1/child_tasks/' + str(child_task_id) + '/'
        child_get_response = self.client.get(child_get_url)
        child_completion_str = child_get_response.data['child_task_completed_date']
        child_completion_str = child_completion_str[:19]
        child_completion_date = datetime.strptime(child_completion_str[:-1], '%Y-%m-%dT%H:%M:%S')

        '''Assert'''
        # Query to close task endpoint came back A-OK
        self.assertEqual(close_response.status_code, status.HTTP_200_OK)
        # parent completion date returned a pareseable datetime
        self.assertIsInstance(parent_completion_date, datetime)
        # child completion date returned a parseable datetime
        self.assertIsInstance(child_completion_date, datetime)

    def test_create_recurring_task(self):
        """
        Unit test the 'create recurring task' list route & Python method
        :return: None
        """
        '''Arrange'''
        # Create a list
        list_url = '/v1/lists/'

        list_data = {
            "list_name": "Yet Another List",
            "list_description": "Still more things I need to do"
        }

        list_response = self.client.post(list_url, list_data, format='json')
        list_id = list_response.data['id']

        '''Act'''
        # attempt to create a recurring task
        recurrence_url = '/v1/tasks/create_recurring_task/'
        recurrence_data = {
            "todo_list_id": list_id,
            "task_name": "recurring task",
            "task_description": "do stuff repeatedly",
            "recurrence_start_date": "2018-04-12T12:00:00",
            "recurrence_end_date": "2018-04-14T15:00:00",
            "recurrence_frequency": "daily"
        }
        recurrence_response = self.client.post(recurrence_url, recurrence_data, format='json', host='127.0.0.1')

        '''Assert'''
        # Endpoint responded as expected
        self.assertEqual(recurrence_response.status_code, status.HTTP_201_CREATED)
        # 3 new records were created
        self.assertEqual(len(recurrence_response.data), 3)
        # Each date due date advances by one day
        due_date = recurrence_response.data[0]['task_due_date']
        time_delta = timedelta(days=1)
        for task in recurrence_response.data:
            self.assertEqual(task['task_due_date'], due_date)
            due_date += time_delta

            # While we're at it, test each URL
            get_url = task['url']
            get_response = self.client.get(get_url)
            self.assertEqual(get_response.status_code, status.HTTP_200_OK)

    def test_view_list(self):
        """
        Unit test the List method.
        :return: None
        """

        '''Arrange'''
        # Instantiate a ParentTaskViewSet object
        parent_task_vs = ParentTaskViewSet()

        # instantiate a dummy Request object

        '''Act'''
        request_factory = APIRequestFactory()
        request = request_factory.get(path='/v1/tasks/')
        response = parent_task_vs.list(request)

        '''Assert'''
        # test method returns a Response object
        self.assertIsInstance(response, Response)


class ChildTaskViewSetTestCase(APITestCase):
    """
    Unit tests for the ChildTaskViewSet class.
    """

    def test_create_child_task(self):
        """
        Unit test to check functionality to create, access and delete a child task record.
        :return:
        """

        '''Arrange'''
        # Create a list
        list_url = '/v1/lists/'

        list_data = {
            "list_name": "Yet Another List",
            "list_description": "Still more things I need to do"
        }

        list_response = self.client.post(list_url, list_data, format='json')
        list_id = list_response.data['id']

        # Create a task
        url = '/v1/tasks/'
        data = {
            "todo_list_id": list_id,
            "task_name": "Do a little dance",
            "task_description": "Make a little love, get down tonight.",
            "task_due_date": "2018-04-20T12:00:00"
        }

        post_response = self.client.post(url, data, format='json')
        task_id = post_response.data['id']

        '''Act'''
        # Create a child task
        child_data = {
            "parent_task_id": task_id,
            "child_task_name": "square dance",
            "child_task_description": "swing yer partner round and round",
            "child_task_due_date": "2018-03-29T12:00:00"
        }
        child_url = '/v1/child_tasks/'
        child_response = self.client.post(child_url, child_data, format='json')
        child_id = child_response.data['id']

        # test a GET request
        child_record_url = child_url + str(child_id) + '/'
        get_response = self.client.get(child_record_url)

        # test a DELETE request
        delete_response = self.client.delete(child_record_url)

        '''Assert'''
        # Record created successfully
        self.assertEqual(child_response.status_code, status.HTTP_201_CREATED)
        # GET executed successfully
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        # DELETE executed successfully
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)

    def test_complete_child_task(self):
        """
        Unit test to check functionality of the complete_child_task endpoint
        :return: None
        """

        '''Arrange'''
        # Create a list
        list_url = '/v1/lists/'

        list_data = {
            "list_name": "Yet Another List",
            "list_description": "Still more things I need to do"
        }

        list_response = self.client.post(list_url, list_data, format='json')
        list_id = list_response.data['id']

        # Create a task
        url = '/v1/tasks/'
        data = {
            "todo_list_id": list_id,
            "task_name": "Do a little dance",
            "task_description": "Make a little love, get down tonight.",
            "task_due_date": "2018-04-20T12:00:00"
        }

        post_response = self.client.post(url, data, format='json')
        task_id = post_response.data['id']

        '''Act'''
        # Create a child task
        child_data = {
            "parent_task_id": task_id,
            "child_task_name": "square dance",
            "child_task_description": "swing yer partner round and round",
            "child_task_due_date": "2018-03-29T12:00:00"
        }
        child_url = '/v1/child_tasks/'
        child_response = self.client.post(child_url, child_data, format='json')
        child_id = child_response.data['id']

        # mark the child task complete
        completion_url = '/v1/child_tasks/complete_child_task/'
        child_completion_body = {
            "child_task_id": child_id
        }

        completion_response = self.client.post(completion_url, child_completion_body, format='json')

        # Query the child task to ensure it's marked complete
        child_get_url = child_url + str(child_id) + '/'
        child_get_response = self.client.get(child_get_url)
        child_completion_date_str = child_get_response.data['child_task_completed_date']
        child_completion_date_str = child_completion_date_str[:19]
        child_completion_date = datetime.strptime(child_completion_date_str[:-1], '%Y-%m-%dT%H:%M:%S')

        # Marking the child task complete should cause the parent task to be automatically marked complete too.
        # Query it.
        parent_get_url = url + str(task_id) + '/'
        parent_get_response = self.client.get(parent_get_url)
        parent_completion_date_str = parent_get_response.data['task_completed_date']
        parent_completion_date_str = parent_completion_date_str[:19]
        parent_completion_date = datetime.strptime(parent_completion_date_str[:-1], '%Y-%m-%dT%H:%M:%S')

        '''Assert'''
        # Completion POST request was successful
        self.assertEqual(completion_response.status_code, status.HTTP_200_OK)
        # Child was marked complete, returning a parseable date when queried
        self.assertIsInstance(child_completion_date, datetime)
        # Parent automatically was marked complete, also giving us a parseable date
        self.assertIsInstance(parent_completion_date, datetime)

    def test_check_siblings_completed(self):
        """
        Unit test the check_siblings_completed method
        :return: None
        """

        '''Arrange'''
        # Create a list
        list_url = '/v1/lists/'

        list_data = {
            "list_name": "Yet Another List",
            "list_description": "Still more things I need to do"
        }

        list_response = self.client.post(list_url, list_data, format='json')
        list_id = list_response.data['id']

        # Create a task
        url = '/v1/tasks/'
        data = {
            "todo_list_id": list_id,
            "task_name": "Do a little dance",
            "task_description": "Make a little love, get down tonight.",
            "task_due_date": "2018-04-20T12:00:00"
        }

        post_response = self.client.post(url, data, format='json')
        task_id = post_response.data['id']

        '''Act'''
        # Create a child task
        child_data = {
            "parent_task_id": task_id,
            "child_task_name": "square dance",
            "child_task_description": "swing yer partner round and round",
            "child_task_due_date": "2018-03-29T12:00:00"
        }
        child_url = '/v1/child_tasks/'
        child_response = self.client.post(child_url, child_data, format='json')
        child_id = child_response.data['id']

        # mark the child task complete
        completion_url = '/v1/child_tasks/complete_child_task/'
        child_completion_body = {
            "child_task_id": child_id
        }

        # Instantiate a ChildTaskViewSet object
        child_vs = ChildTaskViewSet()

        # Call the check_siblings_completed method with the expectation that the task is incomplete
        incomplete_state = child_vs.check_siblings_completed(parent_task_id=task_id)

        # Call the completion URI
        self.client.post(completion_url, child_completion_body, format='json')

        # Call check_siblings_completed again
        complete_state = child_vs.check_siblings_completed(parent_task_id=task_id)

        '''Assert'''
        self.assertFalse(incomplete_state)
        self.assertTrue(complete_state)

    def test_list(self):
        """
        Unit test the List method.
        :return: None
        """

        '''Arrange'''
        # Instantiate a ChildTaskViewSet object
        child_task_vs = ChildTaskViewSet()

        # instantiate a dummy Request object

        '''Act'''
        request_factory = APIRequestFactory()
        request = request_factory.get(path='/v1/child_tasks/')
        response = child_task_vs.list(request)

        '''Assert'''
        # test method returns a Response object
        self.assertIsInstance(response, Response)
