from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^dashboard$', views.dashboard),
    url(r'^new_goal$', views.new_goal),
    url(r'^goal$', views.goal),
]
