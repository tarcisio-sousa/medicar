from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path('especialidades/', views.especialidades, name='especialidades'),
    path('medicos/', views.medicos, name='medicos'),
    path('agendas/', views.agendas, name='agendas'),
    path('consultas/', views.consultas, name='consultas'),
    path('consultas/<int:consulta_id>', views.consultas, name='consultas'),
]
