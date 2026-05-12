from django.urls import path
from .views import ListingListCreateView, ListingDetailView, ViewHistoryListView, PopularListView

urlpatterns = [
    path('', ListingListCreateView.as_view()),
    path('<int:pk>/', ListingDetailView.as_view()),
    path('history/', ViewHistoryListView.as_view()),
    path('popular/', PopularListView.as_view()),
]