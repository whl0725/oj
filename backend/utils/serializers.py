from rest_framework import serializers
from competition.models import Submit


class SubmitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submit
        fields = '__all__'


class RunSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submit
        fields = ['status',"result"]