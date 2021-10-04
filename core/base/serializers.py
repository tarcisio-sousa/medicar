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

    def to_representation(self, agenda):
        ret = super().to_representation(agenda)
        ret['horarios'] = agenda.get_horarios_disponiveis()
        return ret


class ConsultaSerializer(serializers.ModelSerializer):
    agenda = AgendaSerializer()

    class Meta:
        model = Consulta
        fields = ['id', 'agenda', 'horario', 'data_agendamento', ]
        depth = 2

    def to_representation(self, consulta):
        ret = super().to_representation(consulta)
        agenda = ret.pop('agenda')
        ret['horario'] = consulta.horario.strftime("%H:%M")
        ret['dia'] = agenda['dia']
        ret['medico'] = agenda['medico']
        return ret


class CriarConsultaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consulta
        fields = ['agenda', 'horario', ]
