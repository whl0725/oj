from rest_framework import serializers
from .models import User, UserProfile
from competition.models import Submit
from problem.serializers import ProblemNameSerializer
class UserSerializer(serializers.ModelSerializer):
    #username = serializers.CharField(max_length=150)
    #email = serializers.EmailField()
    #create_time = serializers.DateTimeField()
    #admin_type = serializers.TextField()
    #problem_permission = serializers.TextField(default=ProblemPermission.NONE)
    #is_disabled = serializers.BooleanField(default=False)
    class Meta:
        model = User
        fields = '__all__'

#登录的序列化
class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

# 登出的序列化
class UserLogoutSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    #token = serializers.CharField()

#注册的序列化
class UserRegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=32)
    password = serializers.CharField(min_length=6)
    email = serializers.EmailField(max_length=64)
    captcha = serializers.CharField()

class UserUpdateSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    realName = serializers.CharField(max_length=32, allow_null=True, required=False)
    blog = serializers.URLField(max_length=256, allow_blank=True, required=False)
    mood = serializers.CharField(max_length=256, allow_blank=True, required=False)
    github = serializers.URLField(max_length=256, allow_blank=True, required=False)
    school = serializers.CharField(max_length=64, allow_blank=True, required=False)
    major = serializers.CharField(max_length=64, allow_blank=True, required=False)
    language = serializers.CharField(max_length=32, allow_blank=True, required=False)

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['real_name', 'school', 'major', 'language', 'mood', 'blog', 'github']
        extra_kwargs = {
            'real_name': {'required': False, 'allow_blank': True},
            'school': {'required': False, 'allow_blank': True},
            'major': {'required': False, 'allow_blank': True},
            'language': {'required': False, 'allow_blank': True},
            'mood': {'required': False, 'allow_blank': True},
            'blog': {'required': False, 'allow_blank': True},
            'github': {'required': False, 'allow_blank': True}
        }


class UserNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username']

class UserSubmissionsSerializer(serializers.ModelSerializer):
    user = UserNameSerializer(read_only=True, many=False)
    #problem = ProblemNameSerializer(read_only=True, many=False)
    #print(problem)
    #problem = problem.title
    class Meta:
        model = Submit
        fields = ['id','language','submit_time','status', 'user','problem']