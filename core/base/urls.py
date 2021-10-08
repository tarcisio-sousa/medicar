from django.urls import path
from . import views

from rest_framework.authtoken.views import obtain_auth_token


urlpatterns = [
    path('', views.home, name='home'),

    path('login/', obtain_auth_token, name='login'),
    path('registrar/', views.registrar, name='registrar'),
    path('especialidades/', views.especialidades, name='especialidades'),
    path('medicos/', views.medicos, name='medicos'),
    path('agendas/', views.agendas, name='agendas'),
    path('consultas/', views.consultas, name='consultas'),
    path('consultas/<int:consulta_id>', views.consultas, name='consultas'),
]
