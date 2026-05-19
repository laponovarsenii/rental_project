from rest_framework import serializers
from .models import Favorite
from listings.models import Listing

class FavoriteSerializer(serializers.ModelSerializer):

    listing = serializers.PrimaryKeyRelatedField(queryset=Listing.objects.all())


    class Meta:
        model = Favorite
        fields = ['id', 'listing', 'created_at']
        read_only_fields = ['id', 'created_at']


    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)