import datetime
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class Clinica(models.Model):
    nome = models.CharField(max_length=250, blank=False, null=False)


class Especialidade(models.Model):
    nome = models.CharField(max_length=250, blank=False, null=False)

    def __str__(self):
        return f'{self.nome}'


class Medico(models.Model):
    nome = models.CharField(max_length=250, blank=False, null=False)
    crm = models.CharField(_('CRM'), max_length=50, blank=False, null=False)
    email = models.EmailField(max_length=250, blank=True, null=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    especialidade = models.ForeignKey('Especialidade', on_delete=models.CASCADE, blank=False, null=False)

    class Meta:
        verbose_name = 'Médico'
        verbose_name_plural = 'Médicos'

    def __str__(self):
        return f'CRM {self.crm} - {self.nome}'


class Agenda(models.Model):
    medico = models.ForeignKey('Medico', on_delete=models.CASCADE, blank=False, null=False)
    dia = models.DateField('Dia', blank=False, null=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['medico', 'dia'], name='medico_horario_unique')
        ]

    def __str__(self):
        return f'{self.dia} {self.medico}'

    def clean(self):
        if self.dia < datetime.date.today():
            raise ValidationError(_('Dia %(data)s não está disponível'), params={'data': self.dia},)


class AgendaHorario(models.Model):
    agenda = models.ForeignKey('Agenda', related_name='horarios', on_delete=models.CASCADE, blank=False, null=False)
    horario = models.TimeField(_('Horário'), blank=False, null=False)

    def __str__(self):
        return f'{self.horario.strftime("%H:%M")}'


class Consulta(models.Model):
    agenda = models.ForeignKey('Agenda', related_name='consultas', on_delete=models.CASCADE, blank=False, null=False)
    horario = models.TimeField(_('Horário'), blank=False, null=False, unique=True)
    data_agendamento = models.DateTimeField(_('Data agendamento'), auto_now=True, blank=False, null=False)

    def __str__(self):
        return f'{self.agenda} - {self.horario.strftime("%H:%M")}'


class Cliente(models.Model):
    pass
