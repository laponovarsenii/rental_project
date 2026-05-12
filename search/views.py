from rest_framework import generics, permissions
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
        )


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

class PopularSearchView(APIView):
    def get(self, request):
        top_keywords = (
            SearchHistory.objects.values('keyword')
            .annotate(count=Count('id'))
            .order_by('-count')[:10]
        )

        return Response(top_keywords)