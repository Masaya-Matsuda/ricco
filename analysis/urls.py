from analysis import views
from django.urls import path
from django.conf.urls import url, include

app_name = "analysis"

urlpatterns = [
    path("", views.analysis, name="analysis"),
]

