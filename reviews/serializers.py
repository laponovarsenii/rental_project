from rest_framework import serializers

from listings.models import Listing
from .models import Review
from listings.serializers import ListingSerializer
from users.serializers import UserSerializer


class ReviewSerializer(serializers.ModelSerializer):

    listing = ListingSerializer(read_only=True)
    author = UserSerializer(read_only=True)

    listing_id = serializers.PrimaryKeyRelatedField(
        source='listing',
        queryset=Listing.objects.all(),
        write_only=True
    )

    class Meta:
        model = Review
        fields = (
            'id',
            'listing',
            'listing_id',
            'author',
            'rating',
            'text',
            'created_at'
        )

        read_only_fields = ('id', 'author', 'created_at')

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError(
                "The rating must be from 1 to 5"
            )
        return value

    def validate(self, data):
        request = self.context.get('request')
        listing = data.get('listing')
        if Review.objects.filter(author=request.user, listing=listing).exists():
            raise serializers.ValidationError(
                "You have already left a review for this ad."
            )
        return data

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['author'] = request.user
        return super().create(validated_data)