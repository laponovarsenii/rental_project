from django.urls import path
from .views import SearchView, SearchHistoryListView, PopularSearchView

urlpatterns = [
    path('', SearchView.as_view()),
    path('history/', SearchHistoryListView.as_view()),
    path('popular/', PopularSearchView.as_view()),
]