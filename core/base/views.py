# from django.shortcuts import render
from django.http import HttpResponse
from .models import Especialidade, Medico
from .serializers import EspecialidadeSerializer, MedicoSerializer
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
