from rest_framework import serializers
from .models import ProblemTag, Problem

class ProblemTagSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProblemTag
        fields = [
            'name',
        ]
        read_only_fields = ['name', ]


class ProblemListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Problem
        fields = [
            '_id',
            'title',
            'accepted_number',
            'submission_number',
            'difficulty'
        ]
        read_only_fields = ['_id', 'title', 'difficulty']


class ProblemNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problem
        fields = [
            'title',
        ]


