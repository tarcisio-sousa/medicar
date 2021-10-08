from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Especialidade, Medico, Agenda, Consulta


class RegistroSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'confirm_password']
        extra_kwargs = {
                'password': {'write_only': True},
        }

    def save(self):

        user = User(
                    username=self.validated_data['username']
                )
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


class RegistrarConsultaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consulta
        fields = ['agenda', 'horario', 'cliente']
