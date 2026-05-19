from django.urls import path
from .views import FavoriteListCreateView, FavoriteDestroyView

urlpatterns = [
    path('favorites/', FavoriteListCreateView.as_view(), name='favorite-list'),
    path('favorites/<int:pk>/', FavoriteDestroyView.as_view(), name='favorite-destroy'),
]