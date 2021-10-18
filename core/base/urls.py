from django.urls import path
from . import views

from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('registrar', views.RegistrarViewSet)
router.register('especialidades', views.EspecialidadeViewSet)
router.register('medicos', views.MedicoViewSet)
router.register('agendas', views.AgendaViewSet)
router.register('consultas', views.ConsultaViewSet)

urlpatterns = [
    path('login/', obtain_auth_token, name='login'),
]
urlpatterns += router.urls
