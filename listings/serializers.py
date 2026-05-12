from rest_framework import serializers
from .models import Listing, ViewHistory
from users.serializers import UserSerializer



class ListingSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    owner_id = serializers.PrimaryKeyRelatedField(
        source='owner',
        read_only=True
    )
    class Meta:
        model = Listing
        fields = (
            'id',
            'owner',
            'owner_id',
            'title',
            'description',
            'city',
            'address',
            'price',
            'rooms',
            'housing_type',
            'is_active',
            'created_at'
        )
        read_only_fields = ('id', 'owner', 'created_at')

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['owner'] = request.user
        return super().create(validated_data)


class ViewHistorySerializer(serializers.ModelSerializer):
    listing = ListingSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = ViewHistory
        fields = ('id', 'listing', 'user', 'viewed_at')
        read_only_fields = ('id', 'user', 'viewed_at')