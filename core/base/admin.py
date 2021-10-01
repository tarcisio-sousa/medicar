from django.contrib import admin
from core.base.models import Especialidade, Medico, Agenda, AgendaHorario, Consulta


@admin.register(Especialidade)
class EspecialidadeAdmin(admin.ModelAdmin):
    list_display = ['nome', ]


@admin.register(Medico)
class MedicoAdmin(admin.ModelAdmin):
    list_display = ['crm', 'nome', ]


class AgendaHorarioInline(admin.TabularInline):
    model = AgendaHorario
    extra = 1


@admin.register(Agenda)
class AgendaAdmin(admin.ModelAdmin):
    list_display = ['medico', 'dia', ]
    inlines = (AgendaHorarioInline, )


@admin.register(Consulta)
class ConsultaAdmin(admin.ModelAdmin):
    list_display = ['agenda', 'data_agendamento', 'horario', ]
