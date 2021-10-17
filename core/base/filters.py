from django_filters import FilterSet, DateFilter, ModelMultipleChoiceFilter
from .models import Especialidade, Medico, Agenda


class MedicoFilter(FilterSet):
    especialidade = ModelMultipleChoiceFilter(
        field_name='especialidade',
        to_field_name='id',
        queryset=Especialidade.objects.all(),
    )

    class Meta:
        model = Medico
        fields = ['especialidade']


class AgendaFilter(FilterSet):
    data_inicio = DateFilter(field_name="dia", lookup_expr='gte')
    data_final = DateFilter(field_name="dia", lookup_expr='lte')
    medico = ModelMultipleChoiceFilter(
        field_name='medico',
        to_field_name='id',
        queryset=Medico.objects.all(),
    )
    especialidade = ModelMultipleChoiceFilter(
        field_name='medico__especialidade',
        to_field_name='id',
        queryset=Especialidade.objects.all(),
    )

    class Meta:
        model = Agenda
        fields = ['medico', 'especialidade', 'data_inicio', 'data_final']
