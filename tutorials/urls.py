from django.urls import path, re_path

from . import views

urlpatterns = [
    path('', views.signup, name='signup'),
    re_path(r'^apply/(?P<tutorial_id>\d+)/', views.apply, name="apply"),
    re_path(r'^approve/(?P<tutorial_id>\d+)/(?P<student_id>\d+)/', views.approve, name="approve"),
    re_path(r'^reject/(?P<tutorial_id>\d+)/(?P<student_id>\d+)/', views.reject, name="reject"),
]