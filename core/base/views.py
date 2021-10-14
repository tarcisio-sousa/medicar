import datetime
from django.db.models import Q
from django.http import Http404
from django_filters import FilterSet, DateFilter, ModelMultipleChoiceFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import Especialidade, Medico, Agenda, Consulta, AgendaHorario
from .serializers import EspecialidadeSerializer, MedicoSerializer
from .serializers import AgendaSerializer, ConsultaSerializer, RegistrarConsultaSerializer
from .serializers import RegistroSerializer
from rest_framework import filters, generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


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

    def get_horarios_consulta_agendada(self, agenda_id):
        return Consulta.objects.filter(agenda=agenda_id).values_list('horario')

    def get_horarios_agenda(self, agenda_id):
        return (
            AgendaHorario.objects
            .filter(agenda=agenda_id)
            .filter(
                Q(agenda__dia__gte=datetime.date.today()) |
                Q(agenda__dia=datetime.date.today(), horario__gte=datetime.datetime.now().time())
            )
            .exclude(horario__in=self.get_horarios_consulta_agendada(agenda_id))
            .values_list('horario', flat=True))

    def get_queryset(self):
        queryset = self.queryset
        queryset = queryset.filter(dia__gte=datetime.date.today()).order_by('dia')
        agendas = queryset.values_list('id', flat=True)
        agendas_id = [agenda for agenda in agendas if self.get_horarios_agenda(agenda)]
        queryset = queryset.filter(id__in=agendas_id).order_by('dia')
        return queryset
# '''


# '''
# A data em que o agendamento foi feito deve ser salva ao se marcar uma consulta - ok
# Não deve ser possível marcar uma consulta para um dia e horário passados - ok
# Não deve ser possível marcar uma consulta se o usuário já possui uma consulta marcada no mesmo dia e horário
# Não deve ser possível marcar uma consulta se o dia e horário já foram preenchidos - ok

# A listagem não deve exibir consultas para dia e horário passados - ok
# Os itens da listagem devem vir ordenados por ordem crescente do dia e horário da consulta - ok
class ConsultaList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        data_hoje = datetime.date.today()
        hora_agora = datetime.datetime.now().time()
        consultas = Consulta.objects.filter(agenda__dia__gte=data_hoje, horario__gte=hora_agora)
        consultas = consultas.order_by('-agenda__dia', 'horario')
        serializer = ConsultaSerializer(consultas, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        request.data['cliente'] = request.user.id
        serializer = RegistrarConsultaSerializer(data=request.data)
        if serializer.is_valid():
            consulta = serializer.save()
            consulta = Consulta.objects.get(id=consulta.id)
            serializer = ConsultaSerializer(consulta)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# '''
# não deve ser possível desmarcar uma consulta que não foi marcada pelo usuário logado - ok
# não deve ser possível desmarcar uma consulta que nunca foi marcada (identificador inexistente) - ok
# não deve ser possível desmarcar uma consulta que já aconteceu - ok
class ConsultaDetail(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Consulta.objects.get(pk=pk)
        except Consulta.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        consulta = self.get_object(pk)
        serializer = ConsultaSerializer(consulta)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        consulta = self.get_object(pk)
        serializer = ConsultaSerializer(consulta, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        consulta = self.get_object(pk)
        if consulta.cliente == request.user and consulta.valid_data_hora():
            consulta.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = ConsultaSerializer(consulta)
        return Response(serializer.data)
# '''
