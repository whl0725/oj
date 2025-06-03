from rest_framework import serializers
from .models import Competition,Submit
from user.serializers import UserNameSerializer




class CompetitionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Competition
        fields = ['id','title','rule_type','start_time','end_time','create_time','created_by']




class DescriptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Competition
        fields = ['id','title','rule_type','start_time','end_time','create_time','created_by','description','ContestType']

class SubmitSerializer(serializers.ModelSerializer):

    user = UserNameSerializer(read_only=True, many=False)
    class Meta:
        # 指定模型为Submit
        model = Submit
        # 指定字段为id、user、language、submit_time、result
        fields = ['id','user','language','submit_time','status','problem']