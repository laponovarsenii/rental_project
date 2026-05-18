from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Listing, ViewHistory
from .serializers import ListingSerializer, ViewHistorySerializer
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from listings.filters import ListingFilter
from django.db.models import Count


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user


class ListingListView(generics.ListAPIView):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer


class ListingListCreateView(generics.ListCreateAPIView):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    filterset_class = ListingFilter
    search_fields = ('title', 'city', 'description')
    ordering_fields = ('price', 'created_at', 'rooms')

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        return Listing.objects.filter(is_active=True)

    def get_serializer_context(self):
        return {'request': self.request}

class ListingDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ListingSerializer
    permission_classes = [IsOwnerOrReadOnly, IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Listing.objects.select_related('owner')

    def get_serializer_context(self):
        return {'request': self.request}

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        user = request.user if request.user.is_authenticated else None

        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key

        if user is not None:
            ViewHistory.objects.get_or_create(user=user, listing=instance)

        else:
            ViewHistory.objects.get_or_create(user=None, listing=instance, session_key=session_key)

        serializer = ListingSerializer(instance)
        return Response(serializer.data)


class ViewHistoryListView(generics.ListAPIView):
    serializer_class = ViewHistorySerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return ViewHistory.objects.filter(
            user=self.request.user
        ).order_by('-viewed_at')

class PopularListView(generics.ListAPIView):
    serializer_class = ListingSerializer

    def get_queryset(self):
        return Listing.objects.filter(
            is_active=True
        ).select_related('owner').annotate(
            views_count=Count('view_history')
        ).order_by('-views_count', 'created_at')[:10]