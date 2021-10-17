import datetime
from django_filters import FilterSet, DateFilter, ModelMultipleChoiceFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import Especialidade, Medico, Agenda, Consulta
from .serializers import EspecialidadeSerializer, MedicoSerializer
from .serializers import AgendaSerializer, ConsultaSerializer
from .serializers import RegistroSerializer
from rest_framework import filters, generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response


class RegistrarList(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegistroSerializer


class EspecialidadeList(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Especialidade.objects.all()
    serializer_class = EspecialidadeSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['nome']


class MedicoFilter(FilterSet):
    especialidade = ModelMultipleChoiceFilter(
        field_name='especialidade',
        to_field_name='id',
        queryset=Especialidade.objects.all(),
    )

    class Meta:
        model = Medico
        fields = ['especialidade']


class MedicoList(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Medico.objects.all()
    serializer_class = MedicoSerializer
    filter_class = MedicoFilter
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['nome']


# '''
# Não deve ser possível criar mais de uma agenda para um médico em um mesmo dia - ok
# Não deve ser possível criar uma agenda para um médico em um dia passado - ok

# As agendas devem vir ordenadas por ordem crescente de data - ok
# Agendas para datas passadas ou que todos os seus horários já foram preenchidos devem ser excluídas da listagem - ok
# Horários dentro de uma agenda que já passaram ou que foram preenchidos devem ser excluídos da listagem - ok
class AgendaFilter(FilterSet):
    data_inicio = DateFilter(field_name="dia", lookup_expr='gte')
    data_final = DateFilter(field_name="dia", lookup_expr='lte')
    medico = ModelMultipleChoiceFilter(
        field_name='medico',
        to_field_name='id',
        queryset=Medico.objects.all(),
    )
    especialidade = ModelMultipleChoiceFilter(
        field_name='medico__especialidade',
        to_field_name='id',
        queryset=Especialidade.objects.all(),
    )

    class Meta:
        model = Agenda
        fields = ['medico', 'especialidade', 'data_inicio', 'data_final']


class AgendaList(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Agenda.objects.all()
    serializer_class = AgendaSerializer
    filterset_class = AgendaFilter

    def get_queryset(self):
        queryset = self.queryset
        queryset = queryset.filter(dia__gte=datetime.date.today()).order_by('dia')
        agendas_id = [agenda.id for agenda in queryset if any(agenda.get_horarios_disponiveis())]
        queryset = queryset.filter(id__in=agendas_id).order_by('dia')
        return queryset
# '''


# '''
# A data em que o agendamento foi feito deve ser salva ao se marcar uma consulta - ok
# Não deve ser possível marcar uma consulta para um dia e horário passados - ok
# Não deve ser possível marcar uma consulta se o usuário já possui uma consulta marcada no mesmo dia e horário - ok
# Não deve ser possível marcar uma consulta se o dia e horário já foram preenchidos - ok

# A listagem não deve exibir consultas para dia e horário passados - ok
# Os itens da listagem devem vir ordenados por ordem crescente do dia e horário da consulta - ok
class ConsultaList(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Consulta.objects.all()
    serializer_class = ConsultaSerializer

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


# '''
# não deve ser possível desmarcar uma consulta que não foi marcada pelo usuário logado - ok
# não deve ser possível desmarcar uma consulta que nunca foi marcada (identificador inexistente) - ok
# não deve ser possível desmarcar uma consulta que já aconteceu - ok
class ConsultaDetail(generics.RetrieveDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Consulta.objects.all()
    serializer_class = ConsultaSerializer
    lookup_field = 'pk'

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
        else:
            return Response('Não foi possível remover a consulta', status=status.HTTP_400_BAD_REQUEST)
# '''
