from django.urls import path, re_path

from . import views

urlpatterns = [
    path('', views.signup, name='signup'),
    path('signup/', views.signup, name='signup'),
    re_path(r'activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/',
            views.activate, name='activate'),
]