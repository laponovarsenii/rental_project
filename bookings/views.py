from django.db import transaction
from django.utils import timezone
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
        return (Booking.objects.filter(tenant=user) | Booking.objects.filter(listing__owner=user)).select_related(
            'listing', 'tenant').order_by('-created_at')

    def get_serializer_context(self):
        return {'request': self.request}

    def destroy(self, request, *args, **kwargs):
        with transaction.atomic():
            try:
                booking = Booking.objects.get(pk=kwargs['pk'])
            except Booking.DoesNotExist:
                return Response({'detail': 'Бронирование не найдено'}, status=404)

            if request.user != booking.tenant:
                return Response({'detail': 'Вы не можете отменить это бронирование (не ваш заказ)'}, status=403)

            # используем cancel_deadline (если он задан) и timezone-aware дату
            today = timezone.now().date()
            if booking.cancel_deadline and today > booking.cancel_deadline:
                return Response({'detail': 'Срок отмены истёк, отмена невозможна.'}, status=400)
            # при отсутствии cancel_deadline можно также запретить отмену в день заезда:
            if not booking.cancel_deadline and today >= booking.start_date:
                return Response({'detail': 'Бронирование нельзя отменить в день въезда или позже.'}, status=400)

            # атомарное обновление с проверкой версии (оптимистичная блокировка)
            old_version = booking.version
            rows = Booking.objects.filter(pk=booking.pk, version=old_version).update(
                status='cancelled',
                version=old_version + 1
            )
            if rows != 1:
                return Response({'detail': 'Бронирование было изменено'}, status=409)

        return Response({'detail': 'Бронирование отменено.'}, status=200)


class BookingStatusUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        with transaction.atomic():
            try:
                booking = Booking.objects.select_related('listing').get(pk=pk)
            except Booking.DoesNotExist:
                return Response({'detail': 'Booking not found'}, status=404)

            if request.user != booking.listing.owner:
                return Response({'detail': 'Недостаточно прав'}, status=403)

            status_new = request.data.get('status')

            mapping = {
                'approved': 'confirmed',
                'declined': 'rejected',
                'confirmed': 'confirmed',
                'rejected': 'rejected'
            }
            mapped = mapping.get(status_new)
            if mapped is None:
                return Response({'detail': 'Некорректный статус'}, status=400)

            # можно также проверять текущую версию при необходимости;
            booking.status = mapped
            booking.save()

            return Response(BookingSerializer(booking).data)