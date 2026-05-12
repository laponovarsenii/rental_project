from datetime import date

from django.db import transaction
from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Booking
from .serializers import BookingSerializer


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.tenant == request.user or obj.listing.owner == request.user


class BookingListCreateView(generics.ListCreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        return (Booking.objects.filter(tenant=user) | Booking.objects.filter(listing__owner=user)).select_related(
            'listing', 'tenant').order_by('-created_at')

    def get_serializer_context(self):
        return {'request': self.request}


class BookingDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BookingSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrReadOnly)

    def get_queryset(self):
        user = self.request.user
        return Booking.objects.filter(
            tenant=user
        ) | Booking.objects.filter(
            listing__owner=user
        )

    def get_serializer_context(self):
        return {'request': self.request}

    def destroy(self, request, *args, **kwargs):
        with transaction.atomic():
            booking = Booking.objects.select_for_update().get(pk=kwargs['pk'])

            if request.user != booking.tenant:
                return Response({'detail': 'Вы не можете отменить это бронирование (не ваш заказ)'}, status=403)
            if date.today() >= booking.start_date:
                return Response({'detail': 'Бронирование нельзя отменить в день въезда или позже.'}, status=400)

            booking.status = 'cancelled'
            if Booking.objects.filter(pk=booking.pk, version=booking.version).exists():
                booking.version += 1
                booking.save()
            else:
                return Response({'detail': 'Бронирование было изменено'}, status=409)

        return Response({'detail': 'Бронирование отменено.'}, status=200)

class BookingStatusUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):

        with transaction.atomic():
            try:
                booking = Booking.objects.select_for_update().get(pk=pk)
            except Booking.DoesNotExist:
                return Response({'detail': 'Booking not found'}, status=404)

            if request.user != booking.listing.owner:
                return Response({'detail': 'Недостаточно прав'}, status=403)

            status_new = request.data.get('status')
            if status_new not in ['approved', 'declined']:
                return Response({'detail': 'Некорректный статус'}, status=400)

            booking.status = status_new
            booking.save()

            return Response(BookingSerializer(booking).data)
