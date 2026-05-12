from rest_framework import serializers
from .models import SearchHistory


class SearchHistorySerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = SearchHistory
        fields = ('id', 'user', 'keyword', 'searched_at')
        read_only_fields = ('id', 'user', 'searched_at')

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['user'] = request.user
        return super().create(validated_data)




class KeywordCountSerializer(serializers.Serializer):
    keyword = serializers.CharField()
    count = serializers.IntegerField()