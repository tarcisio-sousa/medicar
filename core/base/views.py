# from django.shortcuts import render
import datetime
from django.http import HttpResponse
from .models import Especialidade, Medico, Agenda, AgendaHorario, Consulta
from .serializers import EspecialidadeSerializer, MedicoSerializer
from .serializers import AgendaSerializer, ConsultaSerializer, CriarConsultaSerializer
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response


def home(request):
    return HttpResponse('Medicar')


@api_view(['GET', 'POST'])
def especialidades(request):
    if request.method == 'GET':
        if request.GET and request.GET['search']:
            search = request.GET['search']
            especialidades = Especialidade.objects.filter(nome__contains=search)
        else:
            especialidades = Especialidade.objects.all()
        serializer = EspecialidadeSerializer(especialidades, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = EspecialidadeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
def medicos(request):
    if request.method == 'GET':
        if request.GET:
            medicos = Medico.objects.all()
            if request.GET['search']:
                search = request.GET['search']
                medicos = medicos.filter(nome__contains=search)
            if request.GET['especialidade']:
                especialidades = request.GET['especialidade']
                medicos = medicos.filter(especialidade__in=especialidades)
        else:
            medicos = Medico.objects.all()
        serializer = MedicoSerializer(medicos, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = MedicoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def _verificaAgendasDisponiveis(agendas):
    agendasID = agendas.values_list('id')
    consultas = Consulta.objects.filter(agenda__in=agendasID).values_list('horario')
    horarios = AgendaHorario.objects.filter(agenda__in=agendasID).exclude(horario__in=consultas)
    print(consultas)
    print(horarios)
    # agendas = AgendaHorario.objects.filter(dia__gte=datetime.date.today()).order_by('dia')
    # print(agendas)
    # for agenda in agendas:
    #     print(agenda.horario)
    # agendas


# '''
# As agendas devem vir ordenadas por ordem crescente de data
# Agendas para datas passadas ou que todos os seus horários já foram preenchidos devem ser excluídas da listagem
# Horários dentro de uma agenda que já passaram ou que foram preenchidos devem ser excluídos da listagem
@api_view(['GET', 'POST'])
def agendas(request):
    if request.method == 'GET':
        agendas = Agenda.objects.filter(dia__gte=datetime.date.today()).order_by('dia')
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

    elif request.method == 'POST':
        serializer = AgendaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# '''
# A listagem não deve exibir consultas para dia e horário passados - ok
# Os itens da listagem devem vir ordenados por ordem crescente do dia e horário da consulta - ok
@api_view(['GET', 'POST', 'PUT', 'DELETE'])
def consultas(request, consulta_id=False):
    data_hoje = datetime.date.today()
    hora_agora = datetime.datetime.now().time()
    data_hora_hoje = datetime.datetime.now()
    if not consulta_id:
        if request.method == 'GET':
            consultas = Consulta.objects.filter(agenda__dia__gte=data_hoje, horario__gte=hora_agora)
            consultas = consultas.order_by('-agenda__dia', 'horario')
            serializer = ConsultaSerializer(consultas, many=True)
            return Response(serializer.data)

        elif request.method == 'POST':
            serializer = CriarConsultaSerializer(data=request.data)
            if serializer.is_valid():
                consulta = serializer.save()
                consulta = Consulta.objects.get(id=consulta.id)
                serializer = ConsultaSerializer(consulta)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        try:
            consulta = Consulta.objects.get(pk=consulta_id)
        except Consulta.DoesNotExist:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)

        if request.method == 'GET':
            serializer = ConsultaSerializer(consulta)
            return Response(serializer.data)

        elif request.method == 'PUT':
            serializer = ConsultaSerializer(consulta, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'DELETE':
            # não deve ser possível desmarcar uma consulta que não foi marcada pelo usuário logado
            # não deve ser possível desmarcar uma consulta que nunca foi marcada (identificador inexistente) - ok
            # não deve ser possível desmarcar uma consulta que já aconteceu - ok
            data_consulta = datetime.datetime.combine(consulta.agenda.dia, consulta.horario)

            if data_hora_hoje < data_consulta:
                consulta.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            serializer = ConsultaSerializer(consulta)
            return Response(serializer.data)
# '''
