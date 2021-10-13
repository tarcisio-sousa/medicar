import datetime
from django.http import Http404
from django_filters.rest_framework import DjangoFilterBackend
from .models import Especialidade, Medico, Agenda, Consulta
from .serializers import EspecialidadeSerializer, MedicoSerializer
from .serializers import AgendaSerializer, ConsultaSerializer, RegistrarConsultaSerializer
from .serializers import RegistroSerializer
from rest_framework import filters, generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class RegistrarList(APIView):
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        data = {}
        serializer = RegistroSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            data['response'] = 'Novo usuário registrado com sucesso.'
            data['username'] = user.username
        else:
            data = serializer.errors
        return Response(serializer.data)


class EspecialidadeList(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Especialidade.objects.all()
    serializer_class = EspecialidadeSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['nome']


class MedicoList(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Medico.objects.all()
    serializer_class = MedicoSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['nome']
    # Retornar lista de especialidades
    filter_fields = ['especialidade__nome']


# '''
# Não deve ser possível criar mais de uma agenda para um médico em um mesmo dia - ok
# Não deve ser possível criar uma agenda para um médico em um dia passado - ok

# As agendas devem vir ordenadas por ordem crescente de data - ok
# Agendas para datas passadas ou que todos os seus horários já foram preenchidos devem ser excluídas da listagem - ok
# Horários dentro de uma agenda que já passaram ou que foram preenchidos devem ser excluídos da listagem - ok
class AgendaList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        agendas = Agenda.objects.filter(dia__gte=datetime.date.today()).order_by('dia')
        agendas = [agenda for agenda in agendas if agenda.get_horarios_disponiveis()]
        if request.GET:
            if 'medico' in request.GET:
                medicos = request.GET.getlist('medico')
                agendas = agendas.filter(medico_id__in=medicos)
            if 'especialidade' in request.GET:
                especialidades = request.GET.getlist('especialidade')
                agendas = agendas.filter(medico__especialidade__in=especialidades)
            if 'data_inicio' in request.GET and 'data_final' in request.GET:
                data_inicio = request.GET.get('data_inicio')
                data_final = request.GET.get('data_final')
                agendas = agendas.filter(dia__gte=data_inicio, dia__lte=data_final)
        serializer = AgendaSerializer(agendas, many=True)
        return Response(serializer.data)
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
        # não deve ser possível desmarcar uma consulta que não foi marcada pelo usuário logado
        # não deve ser possível desmarcar uma consulta que nunca foi marcada (identificador inexistente) - ok
        # não deve ser possível desmarcar uma consulta que já aconteceu - ok
        if consulta.cliente == request.user and consulta.valid_data_hora():
            consulta.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = ConsultaSerializer(consulta)
        return Response(serializer.data)
# '''
