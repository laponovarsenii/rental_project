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
        if getattr(self, 'swagger_fake_view', False):
            return Booking.objects.none()
        user = getattr(self.request, 'user', None)
        if not user or getattr(user, 'is_anonymous', True):
            return Booking.objects.none()
        return (Booking.objects.filter(tenant=user) | Booking.objects.filter(listing__owner=user)).select_related(
            'listing', 'tenant').order_by('-created_at')

    def get_serializer_context(self):
        return {'request': self.request}


class BookingDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BookingSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrReadOnly)

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Booking.objects.none()
        user = getattr(self.request, 'user', None)
        if not user or getattr(user, 'is_anonymous', True):
            return Booking.objects.none()
        return (Booking.objects.filter(tenant=user) | Booking.objects.filter(listing__owner=user)).select_related(
            'listing', 'tenant').order_by('-created_at')

    def get_serializer_context(self):
        return {'request': self.request}

    def destroy(self, request, *args, **kwargs):
        with transaction.atomic():
            try:
                booking = Booking.objects.select_for_update().get(pk=kwargs['pk'])
            except Booking.DoesNotExist:
                return Response({'detail': 'Reservation not found'}, status=404)

            if request.user != booking.tenant:
                return Response({'detail': 'You cannot cancel this reservation (not your order)'}, status=403)

            today = timezone.now().date()
            if booking.cancel_deadline and today > booking.cancel_deadline:
                return Response({'detail': 'The cancellation period has expired, cancellation is not possible.'}, status=400)
            if not booking.cancel_deadline and today >= booking.start_date:
                return Response({'detail': 'Reservations cannot be cancelled on or after the day of arrival.'}, status=400)

            old_version = booking.version
            rows = Booking.objects.filter(pk=booking.pk, version=old_version).update(
                status='cancelled',
                version=old_version + 1
            )
            if rows != 1:
                return Response({'detail': 'The reservation has been changed'}, status=409)

        return Response({'detail': 'Reservation cancelled.'}, status=200)


class BookingStatusUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        with transaction.atomic():
            try:
                booking = Booking.objects.select_related('listing').select_for_update().get(pk=pk)
            except Booking.DoesNotExist:
                return Response({'detail': 'Booking not found'}, status=404)

            if request.user != booking.listing.owner:
                return Response({'detail': 'Insufficient rights'}, status=403)

            status_new = request.data.get('status')
            mapping = {
                'approved': 'confirmed',
                'declined': 'rejected',
                'confirmed': 'confirmed',
                'rejected': 'rejected'
            }

            mapped = mapping.get(status_new)
            if mapped is None:
                return Response({'detail': 'Incorrect status'}, status=400)

            booking.status = mapped
            booking.save()

            return Response(BookingSerializer(booking).data)