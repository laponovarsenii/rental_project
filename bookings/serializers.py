from rest_framework import serializers
from listings.models import Listing
from .models import Booking
from listings.serializers import ListingSerializer
from users.serializers import UserSerializer
import datetime


class BookingSerializer(serializers.ModelSerializer):
    listing = ListingSerializer(read_only=True)
    tenant = UserSerializer(read_only=True)

    listing_id = serializers.PrimaryKeyRelatedField(
        source='listing',
        queryset=Listing.objects.all(),
        write_only=True
    )


    cancel_deadline = serializers.DateField(required=False, allow_null=True)

    class Meta:
        model = Booking
        fields = (
            'id',
            'listing',
            'listing_id',
            'tenant',
            'start_date',
            'end_date',
            'cancel_deadline',
            'status',
            'created_at',
        )
        read_only_fields = ('id', 'tenant', 'status', 'created_at')

    def validate(self, data):
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        listing = data.get('listing')

        if start_date is None or end_date is None:
            raise serializers.ValidationError("start_date и end_date обязательны.")

        if start_date >= end_date:
            raise serializers.ValidationError("The start date must be before the end date.")

        qs = Booking.objects.filter(
            listing=listing,
            start_date__lt=end_date,
            end_date__gt=start_date,
            status__in=['pending', 'confirmed']
        )
        instance = getattr(self, 'instance', None)
        if instance is not None:
            qs = qs.exclude(pk=instance.pk)

        if qs.exists():
            raise serializers.ValidationError("This listing is already booked for these dates.")

        return data

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['tenant'] = request.user

        # Если cancel_deadline не передали, ставим дефолт — за 1 день до start_date
        if validated_data.get('cancel_deadline') is None and validated_data.get('start_date') is not None:
            validated_data['cancel_deadline'] = validated_data['start_date'] - datetime.timedelta(days=1)

        return super().create(validated_data)