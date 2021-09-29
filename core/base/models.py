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


'''
class ClinicaEspecialidade(models.Model):
    clinica = models.ForeignKey('Clinica', on_delete=models.CASCADE, blank=False, null=False)
    especialidade = models.ForeignKey('Especialidade', on_delete=models.CASCADE, blank=False, null=False)
'''


class Medico(models.Model):
    nome = models.CharField(max_length=250, blank=False, null=False)
    crm = models.CharField(_('CRM'), max_length=50, blank=False, null=False)
    email = models.CharField(max_length=250, blank=True, null=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        verbose_name = 'Médico'
        verbose_name_plural = 'Médicos'

    def __str__(self):
        return f'CRM {self.crm} - {self.nome}'


class MedicoEspecialidade(models.Model):
    medico = models.ForeignKey('Medico', on_delete=models.CASCADE, blank=False, null=False)
    especialidade = models.ForeignKey('Especialidade', on_delete=models.CASCADE, blank=False, null=False)


class Agenda(models.Model):
    medico = models.ForeignKey('Medico', on_delete=models.CASCADE, blank=False, null=False)
    data_alocacao = models.DateField('Dia', blank=False, null=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['medico', 'data_alocacao'], name='medico_horario_unique')
        ]

    def __str__(self):
        return f'{self.data_alocacao} {self.medico}'

    def clean(self):
        if self.data_alocacao < datetime.date.today():
            raise ValidationError(_('Dia %(data)s não está disponível'), params={'data': self.data_alocacao},)


class AgendaHorario(models.Model):
    pass
    # agenda = models.ForeignKey('Agenda', on_delete=models.CASCADE, blank=False, null=False)
    # horario = models.TimeField(_('Horário'), blank=False, null=False, unique=True)

    # def __str__(self):
    #     return f'{self.horario}'


class Consulta(models.Model):
    pass


class Cliente(models.Model):
    pass
