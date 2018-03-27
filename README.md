# todo-rest-api

**By Paul Anderson**

Demonstration of implementing Django REST framework to create a simple server-side "to do list" app.

**Domain:** To-do list

**Interface:** Web API

**Language:** Python 3

**Libraries Implemented:** Django, Django REST Framework

## Installation
To install on Ubuntu:

* Make sure your server/firewall is listening on port 8000
* Update system and install dependencies:

```
# update system
sudo apt-get update

# install Python 3
sudo apt-get install python3

# install pip3
sudo apt-get install python3-pip

# install Django
sudo pip3 install django

# install Django REST framework
sudo pip3 install django-rest-framework
```

* Navigate to the directory where you want to install the app, clone the repo and start the Django app.

```
# Migrate the data models
sudo python3 manage.py makemigrations
sudo python3 manage.py migrate

# Run unit tests
python3 manage.py test

# Start the server
sudo python3 manage.py runserver 0.0.0.0:8000
```

# API Documentation

## Common functionality
### URIs
**Important note:** All URIs must be accessed using a trailing slash! 
Good:`http://example.com/v1/lists/`

Bad:`http://example.com/v1/lists`

### Versioning
Versioning of the API is handled with the URI. I.e., all endpoints for the current version, v1, are accessed under the URI `/v1/`. 

### HTTP headers
Requests to the API should implement the following headers:

```
accept: application/json
content-type: application/json
```

### Authentication
For demonstration purposes and ease of accessibility, this app does not implement client authentication. However, Django REST Framework supports both Basic Auth and Oauth.

## Endpoints

The API has 3 endpoints: Lists, Tasks and Child Tasks.

### Lists endpoint
URI: `/v1/lists/`

Endpoint for creating, updating and deleting to-do lists

**Creating lists:**

To create a list, perorm a POST request with a JSON body, formatted like the example below:

```
{
	"list_name": "My List",
	"list_description": "Some things I need to do"
}
```
Response:

```
{
	"url": "http://example.com:8000/v1/lists/1/",
	"id": 1,
	"list_name": "My List",
	"list_description": "Some things I need to do",
	"tasks": [],
}
```
Please note that in keeping with the HATEOAS principle, the response provides the URL of the newly created resource. The resource's unique identifier is appended to the URI. You may access the resource in detail with a GET request to the URL in the response's "url" field. Per requirement, this will also display any tasks that have been created in the list.

**Updating Lists**

To update an existing list, submit a PUT request to its resource URI (i.e., `http://example.com:8000/v1/lists/1/`). Format the request body with the same fields as a POST request (above).

**Deleting Lists**

To delete a list (and all the tasks and sub-tasks), submit a request using the DELETE method to its individual resource URI.

**Viewing all lists and their tasks**

You may access the entire data model with a GET request to `/v1/lists/`. 

### Tasks endpoint

URI: `/v1/tasks/`

Endpoint for creating, updating and deleting tasks within a list.

**Creating Tasks**

Submit a POST request to the tasks endpoint, with the body JSON formatted like the example below:

```
{
  "todo_list_id": 1,
  "task_name": "Do a little dance",
  "task_description": "Make a little love, get down tonight.",
  "task_due_date": "2018-04-20T12:00:00"
}
```
**todo\_list\_id**: Unique identifier of the task's parent task list (see above).

**Other fields:** Should be pretty self-explanatory.

Response:

```
{
	"url": "http:example:8000/v1/tasks/1/",
	"id": 1,
	"todo_list_id": 1,
	"task_name": "Do a little dance",
	"task_description": "Make a little love, get down tonight.",
	"task_due_date": "2018-04-20T12:00:00Z",
	"task_completed_date": null,
	"child_tasks": [],
}
```

**Accessing, updating and deleting Task records:**

Uses the same GET/PUT/DELETE mechanism as lists (above) on the resource URI, i.e., `http:example:8000/v1/tasks/1/`

**Marking a task as complete:**

To simplify this process, use the following special extension to the Tasks endpoint:
`/v1/tasks/complete_task/`

Submit a POST request with JSON as follows:

```
{
  "task_id": 1
}
```
Response:

```
{
	"completed_datetime": "2018-03-27T22:27:14.796359",
	"task_id": 1,
	"status": "Task completed"
}
```

Please note that if the Task has any Child Tasks, these will also be marked complete.

### Child Tasks endpoint
Endpoint for creating, updating and deleting sub-tasks or "children" of an existing task.

URI: `/v1/child_tasks/`

**Creating child tasks:**

Submit a POST request to the child tasks endpoint, formatted as follows:

```
{
	"parent_task_id": 1,
	"child_task_name": "square dance",
  	"child_task_description": "swing yer partner round and round",
	"child_task_due_date": "2018-03-29T12:00:00"  
}
```

With the field parent\_task\_id being the unique identifier of the child task's parent.

response:

```
{
	"url": "http://example.com:8000/v1/child_tasks/1/",
	"id": 1,
	"parent_task_id": 1,
	"child_task_name": "square dance",
	"child_task_description": "swing yer partner round and round",
	"child_task_due_date": "2018-03-29T12:00:00Z",
	"child_task_completed_date": null
}
```

**Accessing, updating and deleting child tasks:**

These tasks use the same pattern as Lists and parent Tasks by performing GET/PUT/DELETE requests to the individual child task resource URI, i.e., `http://example.com:8000/v1/child_tasks/1/`

**Marking child tasks complete:**

Like the parent Tasks endpoint, the child tasks endpoint has a simplified extension for marking child tasks complete. Per requirements, marking complete all child tasks for a given parent task will cause the parent task to automatically be marked complete.

URI: `/v1/child_tasks/complete_child_task/`

POST body example:

```
{
  "child_task_id": 1
}
```
Response:

```
{
	"completed_datetime": "2018-03-27T22:43:52.660417",
	"status": "Child task completed",
	"child_task_id": 1
}
```

## About the code
This implementation was accomplished entirely by overriding existing classes provided by the Django and Django REST Framework libraries. For ease of deployment, all the files required for Django implementation are included in this repository. Therefore, much of the code here is not my own, but the following files contain my implementation:

App Configuration:

[todo-rest-api/todo_api/settings.py](https://github.com/elpablogrande/todo-rest-api/blob/master/todo_api/settings.py)

[todo-rest-api/todo_api/urls.py](https://github.com/elpablogrande/todo-rest-api/blob/master/todo_api/urls.py)

Data Models:

[todo-rest-api/todo_list/models.py](https://github.com/elpablogrande/todo-rest-api/blob/master/todo_list/models.py)

JSON Serializers:

[todo-rest-api/todo_list/serializers.py](https://github.com/elpablogrande/todo-rest-api/blob/master/todo_list/serializers.py)

Django Views (Control structures):

[todo-rest-api/todo_list/views.py](https://github.com/elpablogrande/todo-rest-api/blob/master/todo_list/views.py)

Unit Tests:

[todo-rest-api/todo_list/tests.py](https://github.com/elpablogrande/todo-rest-api/blob/master/todo_list/tests.py)




