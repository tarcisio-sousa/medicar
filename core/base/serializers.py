from rest_framework import serializers
from .models import Especialidade, Medico, Agenda, Consulta


class EspecialidadeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Especialidade
        fields = ['id', 'nome', ]


class MedicoSerializer(serializers.ModelSerializer):
    especialidade = EspecialidadeSerializer()

    class Meta:
        model = Medico
        fields = ['id', 'crm', 'nome', 'especialidade', ]


class AgendaSerializer(serializers.ModelSerializer):
    medico = MedicoSerializer()
    horarios = serializers.StringRelatedField(many=True)

    class Meta:
        model = Agenda
        fields = ['id', 'medico', 'dia', 'horarios', ]


class ConsultaSerializer(serializers.ModelSerializer):
    agenda = AgendaSerializer()

    class Meta:
        model = Consulta
        fields = ['id', 'agenda', 'horario', 'data_agendamento', ]
        depth = 3


class CriarConsultaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consulta
        fields = ['agenda', 'horario', ]
