from rest_framework import serializers

from listings.models import Listing
from .models import Booking
from listings.serializers import ListingSerializer
from users.serializers import UserSerializer


class BookingSerializer(serializers.ModelSerializer):
    listing = ListingSerializer(read_only=True)
    tenant = UserSerializer(read_only=True)

    listing_id = serializers.PrimaryKeyRelatedField(
        source='listing',
        queryset=Listing.objects.all(),
        write_only=True
        )

    class Meta:
        model = Booking
        fields = (
            'id',
            'listing',
            'listing_id',
            'tenant',
            'start_date',
            'end_date',
            'status',
            'created_at'
        )
        read_only_fields = ('id', 'tenant', 'status', 'created_at')

    def validate(self, data):
        if data['start_date'] >= data['end_date']:
            raise serializers.ValidationError(
                "The start date must be before the end date."
            )

        listing = data.get('listing')
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        overlapping = Booking.objects.filter(
            listing=listing,
            start_date__lt=end_date,
            end_date__gt=start_date,
            status__in=['pending', 'confirmed']
        ).exists()

        if overlapping:
            raise serializers.ValidationError(
                "This listing is already booked for these dates."
            )

        return data

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['tenant'] = request.user
        return super().create(validated_data)