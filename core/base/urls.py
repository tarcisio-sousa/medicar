from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path('especialidades', views.especialidades, name='especialidades'),
    path('medicos', views.medicos, name='medicos'),
]
