from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.index, name='index'),
    path('generate_report/', views.generate_report, name='generate_report'),
    path('open_report/', views.open_report, name='open_report'),
]
