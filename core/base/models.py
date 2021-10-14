import datetime

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Q
from rest_framework.authtoken.models import Token


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
        return f'{self.dia.strftime("%d/%m/%Y")} {self.medico}'

    def get_horarios_disponiveis(self):
        horarios = (
            AgendaHorario.objects
            .filter(agenda=self.id)
            .filter(
                Q(agenda__dia__gte=datetime.date.today()) | 
                Q(agenda__dia=datetime.date.today(), horario__gte=datetime.datetime.now().time())
            )
            .exclude(horario__in=Consulta.objects.filter(agenda=self.id).values_list('horario'))
            .values_list('horario', flat=True))
        horarios = [horario.strftime("%H:%M") for horario in horarios]
        return horarios

    def valid_data(self):
        return self.dia < datetime.date.today()

    def clean(self):
        if self.valid_data():
            raise ValidationError(_('Dia %(data)s não está disponível'), params={'data': self.dia},)


class AgendaHorario(models.Model):
    agenda = models.ForeignKey('Agenda', related_name='horarios', on_delete=models.CASCADE, blank=False, null=False)
    horario = models.TimeField(_('Horário'), blank=False, null=False)

    def __str__(self):
        return f'{self.horario.strftime("%H:%M")}'

    def get_data_hora(self):
        return datetime.datetime.combine(self.agenda.dia, self.horario)


class Consulta(models.Model):
    agenda = models.ForeignKey('Agenda', related_name='consultas', on_delete=models.CASCADE, blank=False, null=False)
    horario = models.TimeField(_('Horário'), blank=False, null=False)
    data_agendamento = models.DateTimeField(_('Data agendamento'), auto_now=True, blank=False, null=False)
    cliente = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=False, null=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['agenda_id', 'horario'], name='agenda_horario_unique')
        ]

    def __str__(self):
        return f'{self.agenda} - {self.horario.strftime("%H:%M")}'

    def get_data_hora(self):
        return datetime.datetime.combine(self.agenda.dia, self.horario)

    def valid_data_hora(self):
        return datetime.datetime.now() < self.get_data_hora()

    def valid_horario_in_agenda(self):
        return AgendaHorario.objects.filter(agenda=self.agenda, horario=self.horario).values_list('horario')

    def clean(self):
        if not self.valid_horario_in_agenda():
            raise ValidationError(_('Horário não está disponível'))
        elif not self.valid_data_hora():
            raise ValidationError(_('Não é possível realizar consulta para data e hora retroativa'))


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
