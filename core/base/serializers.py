import datetime

from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from .models import Especialidade, Medico, Agenda, Consulta, AgendaHorario


class RegistroSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'confirm_password']
        extra_kwargs = {
                'password': {'write_only': True},
        }

    def save(self):
        user = User(username=self.validated_data['username'])
        password = self.validated_data['password']
        confirm_password = self.validated_data['confirm_password']
        if password != confirm_password:
            raise serializers.ValidationError({'password': 'Senhas não correspondem.'})
        user.set_password(password)
        user.save()
        return user


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['id'].read_only = True
        self.fields['data_agendamento'].read_only = True
        self.fields['agenda'].write_only = True
        self.fields['cliente'].write_only = True

    class Meta:
        model = Consulta
        fields = ['id', 'agenda', 'horario', 'data_agendamento', 'cliente']
        validators = [
            UniqueTogetherValidator(
                queryset=Consulta.objects.all(),
                fields=['agenda', 'horario'],
                message=_("Já existe uma consulta cadastrada para essa agenda e horário.")
            )
        ]

    def to_representation(self, consulta):
        ret = super().to_representation(consulta)
        agenda = AgendaSerializer().to_representation(consulta.agenda)

        ret['horario'] = consulta.horario.strftime("%H:%M")
        ret['dia'] = agenda['dia']
        ret['medico'] = agenda['medico']
        return ret

    def get_data_hora(self, consulta):
        return datetime.datetime.combine(consulta['agenda'].dia, consulta['horario'])

    def valid_data_hora(self, consulta):
        return datetime.datetime.now() < self.get_data_hora(consulta)

    def valid_horario_in_agenda(self, consulta):
        return (
            AgendaHorario.objects
            .filter(agenda=consulta['agenda'], horario=consulta['horario'])
            .values_list('horario'))

    def validate(self, consulta):
        if not self.valid_horario_in_agenda(consulta):
            raise serializers.ValidationError(_('Horário não está disponível'))
        elif not self.valid_data_hora(consulta):
            raise serializers.ValidationError(_('Não é possível realizar consulta para data e hora retroativa'))
        return consulta
