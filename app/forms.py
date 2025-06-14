import django_filters
from .models import Bundle

class BundleFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains', label='Title')
    description = django_filters.CharFilter(lookup_expr='icontains', label='Description')
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__name',
        to_field_name='name',
        queryset=Bundle.tags.model.objects.all(),
        conjoined=False,
        label='Tags',
    )

    class Meta:
        model = Bundle
        fields = ['title', 'description', 'tags']
