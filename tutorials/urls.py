from django.urls import path, re_path

from . import views

urlpatterns = [
    path('', views.signup, name='signup'),
    path('signup/', views.signup, name='signup'),
    re_path(r'activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/',
            views.activate, name='activate'),
    re_path(r'^apply/(?P<tutorial_id>\d+)/', views.apply, name="apply"),
    re_path(r'^withdraw/(?P<tutorial_id>\d+)/(?P<student_id>\d+)/', views.withdraw, name="withdraw"),
    re_path(r'^cancel/(?P<tutorial_id>\d+)/(?P<student_id>\d+)/', views.cancel, name="cancel"),
    re_path(r'^export/?$', views.export, name='export'),
]