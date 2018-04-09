"""
todo_api.urls.py
Implementation commit: Paul Anderson, 3/25/2018

Set up Django routers to define API endpoint URIs

todo_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from rest_framework import routers
from todo_list import views

router = routers.DefaultRouter()
router.register(r'v1/lists', views.TodoListTaskViewSet)
router.register(r'v1/tasks', views.ParentTaskViewSet)
router.register(r'v1/child_tasks', views.ChildTaskViewSet)
router.register(r'v1/users', views.UserViewSet)
router.register(r'v1/groups', views.GroupViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]