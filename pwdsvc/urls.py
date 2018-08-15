"""This module rovides url routing rules;
   to determine what function in view.py gets
   called based on the url values.
"""
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^users$', views.users, name='users'),
    url(r'^users/(\d+)$', views.users_by_uid, name='users_by_uid'),
    url(r'^users/(\d+)/groups$', views.users_uid_groups, name='users_uid_groups'),
    url(r'^users/query$', views.users_query, name='users_query'),
    url(r'^groups$', views.groups, name='groups'),
    url(r'^groups/(\d+)', views.groups_by_gid, name='groups_by_gid'),
    url(r'^groups/query$', views.groups_query, name='groups_query'),
]
