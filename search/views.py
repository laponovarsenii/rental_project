from rest_framework import generics, permissions
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from .models import SearchHistory
from .serializers import SearchHistorySerializer
from listings.models import Listing
from listings.serializers import ListingSerializer
from django.db.models import Count


class SearchView(APIView):
    def get(self, request):
        keyword = request.query_params.get('q', '')

        if not keyword:
            return Response({'error': 'Введите поисковый запрос'}, status=400)

        listings = Listing.objects.filter(is_active=True).filter(
            Q(title__icontains=keyword) |
            Q(city__icontains=keyword) |
            Q(description__icontains=keyword)
        ).select_related('owner')


        if request.user.is_authenticated:
            SearchHistory.objects.get_or_create(
                user=request.user,
                keyword=keyword
            )

        serializer = ListingSerializer(listings, many=True, context={'request': request})
        return Response(serializer.data)


class SearchHistoryListView(generics.ListAPIView):
    serializer_class = SearchHistorySerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return SearchHistory.objects.filter(
            user=self.request.user
        ).order_by('-searched_at')


class PopularSearchPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class PopularSearchView(generics.ListAPIView):
    serializer_class = SearchHistorySerializer
    pagination_class = PopularSearchPagination
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):

        return SearchHistory.objects.values('keyword').annotate(
            count=Count('id')
        ).order_by('-count')

    def list(self, request, *args, **kwargs):

        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(page)

        return Response(queryset)