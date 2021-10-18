import datetime
from django_filters.rest_framework import DjangoFilterBackend
from .models import Especialidade, Medico, Agenda, Consulta
from .filters import MedicoFilter, AgendaFilter
from .serializers import EspecialidadeSerializer, MedicoSerializer
from .serializers import AgendaSerializer, ConsultaSerializer
from .serializers import RegistroSerializer
from rest_framework import status, viewsets
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.models import User


class RegistrarViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = RegistroSerializer


class EspecialidadeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Especialidade.objects.all()
    serializer_class = EspecialidadeSerializer
    filter_backends = [SearchFilter]
    search_fields = ['nome']


class MedicoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Medico.objects.all()
    serializer_class = MedicoSerializer
    filter_class = MedicoFilter
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ['nome']


class AgendaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Agenda.objects.all()
    serializer_class = AgendaSerializer
    filterset_class = AgendaFilter

    def get_queryset(self):
        queryset = self.queryset
        queryset = queryset.filter(dia__gte=datetime.date.today()).order_by('dia')
        agendas_id = [agenda.id for agenda in queryset if any(agenda.get_horarios())]
        queryset = queryset.filter(id__in=agendas_id).order_by('dia')
        return queryset


class ConsultaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Consulta.objects.all()
    serializer_class = ConsultaSerializer
    lookup_field = 'pk'

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.filter(
            agenda__dia__gte=datetime.date.today(),
            horario__gte=datetime.datetime.now().time())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        request.data.update({'cliente': request.user.id})
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def retrieve(self, request, *args, **kwargs):
        consulta = self.get_object()
        if consulta.valid_data_hora():
            serializer = self.get_serializer(consulta)
            return Response(serializer.data)
        else:
            return Response('Consulta não encontrada', status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        consulta = self.get_object()
        if consulta.cliente == self.request.user and consulta.valid_data_hora():
            self.perform_destroy(consulta)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response('Não foi possível remover a consulta', status=status.HTTP_400_BAD_REQUEST)
