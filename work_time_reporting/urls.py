from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("add_work_time/", views.add_work_time, name="add_work_time"),
    path("generate_summary/", views.generate_summary, name="generate_summary"),
]