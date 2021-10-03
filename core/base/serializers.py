import datetime
from rest_framework import serializers
from .models import Especialidade, Medico, Agenda, AgendaHorario, Consulta


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
        horarios = AgendaHorario.objects.filter(agenda=agenda.id)
        horarios = horarios.filter(agenda__dia__gte=datetime.date.today(), horario__gte=datetime.datetime.now().time())
        horarios = horarios.exclude(horario__in=Consulta.objects.filter(agenda=agenda.id).values_list('horario'))
        horarios = horarios.values_list('horario', flat=True)
        h = []
        for horario in horarios:
            h.append(horario.strftime("%H:%M"))
        ret['horarios'] = h
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
