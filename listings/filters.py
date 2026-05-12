import django_filters
from .models import Listing


class ListingFilter(django_filters.FilterSet):

    price_min = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    price_max = django_filters.NumberFilter(field_name='price', lookup_expr='lte')


    city = django_filters.CharFilter(field_name='city', lookup_expr='icontains')


    rooms = django_filters.NumberFilter(field_name='rooms')
    rooms_min = django_filters.NumberFilter(field_name='rooms', lookup_expr='gte')


    housing_type = django_filters.CharFilter(field_name='housing_type')

    class Meta:
        model = Listing
        fields = ('city', 'price_min', 'price_max', 'rooms', 'rooms_min', 'housing_type')