import django_filters
from dbcontroller.models import Company


class CompanyFilter(django_filters.FilterSet):
    # groupper = django_filters.filterset.ChoiceFilter(choices=[
    #     (0, 'All'),
    #     (1, 'Count'),
    #     (2, 'Maximum'),
    #     (3, 'Avarage'),
    # ], label='Group method', method=)
    location_filter = django_filters.MultipleChoiceFilter(
        choices=[(i, i) for i in range(100)],
        label='Регион',
        conjoined=False,
        field_name='location_code',
    )

    class Meta:
        model = Company
        fields = ['is_ip']
