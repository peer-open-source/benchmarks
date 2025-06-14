import django_filters
from .models import Bundle

# class BundleFilter(django_filters.FilterSet):
#     key = django_filters.CharFilter(lookup_expr='icontains')
#     benchmarks__references__title = django_filters.CharFilter(label="Reference title contains", lookup_expr='icontains')

#     class Meta:
#         model = Bundle
#         fields = ['key', 'benchmarks__references__title']


import django_filters
from app.models import Bundle, GroupedTag
import django_filters
from app.models import Bundle, GroupedTag

class BundleFilter(django_filters.FilterSet):
    type = django_filters.ModelMultipleChoiceFilter(
        field_name="tags__name",
        queryset=GroupedTag.objects.filter(category=GroupedTag.TagCategory.TYPE).order_by("name"),
        to_field_name="name",
        label="Type",
        conjoined=False,
    )
    material = django_filters.ModelMultipleChoiceFilter(
        field_name="tags__name",
        queryset=GroupedTag.objects.filter(category=GroupedTag.TagCategory.MATERIAL).order_by("name"),
        to_field_name="name",
        label="Material",
        conjoined=False,
    )
    # feature = django_filters.ModelMultipleChoiceFilter(
    #     field_name="tags__name",
    #     queryset=GroupedTag.objects.filter(category=GroupedTag.TagCategory.FEATURE).order_by("name"),
    #     to_field_name="name",
    #     label="Feature",
    #     conjoined=False,
    # )

    class Meta:
        model = Bundle
        fields = []
