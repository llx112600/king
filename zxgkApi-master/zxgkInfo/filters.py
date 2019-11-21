from django_filters import CharFilter
from .models import Person
from django_filters.rest_framework import FilterSet


class PersonFilter(FilterSet):
    pname = CharFilter(field_name='iname', lookup_expr='exact')
    cardnum = CharFilter(field_name='cardNum', lookup_expr='exact')

    class Meta:
        model = Person
        fields = ['pname', 'cardnum']
