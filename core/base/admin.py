from django.contrib import admin
from core.base.models import Especialidade, Medico, MedicoEspecialidade, Agenda


@admin.register(Especialidade)
class EspecialidadeAdmin(admin.ModelAdmin):
    list_display = ['nome', ]


class MedicoEspecialidadeInline(admin.TabularInline):
    model = MedicoEspecialidade
    extra = 1


@admin.register(Medico)
class MedicoAdmin(admin.ModelAdmin):
    list_display = ['crm', 'nome', ]
    inlines = (MedicoEspecialidadeInline, )


# class AgendaHorarioInline(admin.TabularInline):
#     model = AgendaHorario
#     extra = 1


@admin.register(Agenda)
class AgendaAdmin(admin.ModelAdmin):
    list_display = ['medico', 'data_alocacao', ]
    # inlines = (AgendaHorarioInline, )
