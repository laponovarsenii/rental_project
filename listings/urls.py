from django.urls import path
from .views import ListingListCreateView, ListingDetailView, ViewHistoryListView, PopularListView

urlpatterns = [
    path('popular/', PopularListView.as_view()),
    path('', ListingListCreateView.as_view()),
    path('<int:pk>/', ListingDetailView.as_view()),
    path('history/', ViewHistoryListView.as_view(), name='view-history'),
]