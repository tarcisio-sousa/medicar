from django.urls import path
from . import views

from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.urlpatterns import format_suffix_patterns


urlpatterns = [
    path('login/', obtain_auth_token, name='login'),
    path('registrar/', views.RegistrarList.as_view()),
    path('especialidades/', views.EspecialidadeList.as_view()),
    path('medicos/', views.MedicoList.as_view()),
    path('agendas/', views.AgendaList.as_view()),
    path('consultas/', views.ConsultaList.as_view()),
    path('consultas/<int:pk>', views.ConsultaDetail.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
