from rest_framework import serializers

from work_diary.models import ScreenShot, WorkDiary


class ScreenShotsSerializer(serializers.Serializer):
    image = serializers.ImageField()
    description = serializers.CharField()
    create_date = serializers.DateTimeField()
    
    def create(self, validated_data):
        return ScreenShot.objects.create(**validated_data)
