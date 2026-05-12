from rest_framework import generics, permissions
from rest_framework.pagination import PageNumberPagination

from .models import Review
from .serializers import ReviewSerializer


class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user

class ReviewPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class ReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    pagination_class = ReviewPagination

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        listing_id = self.request.query_params.get('listing_id')
        queryset = Review.objects.select_related('listing', 'author')
        if listing_id:
            return queryset.filter(listing_id=listing_id).order_by('-created_at')
        return queryset.order_by('-created_at')

    def get_serializer_context(self):
        return {'request': self.request}


class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ReviewSerializer
    permission_classes = (permissions.IsAuthenticated, IsAuthorOrReadOnly)

    def get_queryset(self):
        return Review.objects.select_related('listing', 'author')

    def get_serializer_context(self):
        return {'request': self.request}