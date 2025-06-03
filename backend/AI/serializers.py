from rest_framework import serializers
from .models import AIChatSession


class AIChatSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIChatSession
        fields = ['content']
