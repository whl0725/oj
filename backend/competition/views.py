from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Competition,Submit,CompetitionProblem
from .serializers import CompetitionSerializer,DescriptionSerializer,SubmitSerializer
from home.serializers import HomePageSerializer
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from user.models import User
class PasswordAPI(APIView):


    def post(self,request):
        password = request.data.get("password")
        
        return Response("ok")


class CompetitionAPI(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))
        
        # 获取所有可见的比赛
        competitions = Competition.objects.all().filter(visible=True)
        
        # 计算总数
        total = competitions.count()
        
        # 计算分页
        start = (page - 1) * page_size
        end = start + page_size
        competitions = competitions[start:end]
        
        serializer = CompetitionSerializer(competitions, many=True)
        return Response({
            'code': 0,
            'data': serializer.data,
            'total': total,
            'message': 'success'
        })


class DescriptionAPI(APIView):

    def get(self, request, id):
        Competitions = Competition.objects.filter(id=id)
        description = DescriptionSerializer(Competitions, many=True)
        #print(description.data)
        user_id = description.data[0]['created_by']
        user = User.objects.get(id=user_id)
        description.data[0]['created_by'] = user.username
        return Response(description.data)



class PasswordAPI(APIView):

    def post(self,request):
        data = request.data.get("password")
        id = request.data.get("id")
        password= Competition.objects.filter(id=id).get().password
        if(data == password):
            return Response("ok")
        else:
            return Response("no")



class AnnouncementAPI(APIView):

    def get(self,request,id):
        competition = Competition.objects.get(id=id)
        # 获取所有已关联的公告
        announcements = competition.announcements.all()
        serializer = HomePageSerializer(announcements, many=True)

        return Response({
            "code": 0,
            "data": {
                "announcements": serializer.data
            },
            "message": "success"
        })



class ProblemListAPI(APIView):

    def get(self, request, id):
        try:
            competition = Competition.objects.get(id=id)
            # 获取比赛的所有题目，通过 CompetitionProblem 关联表
            competition_problems = competition.competitionproblem_set.all()
            
            problems_data = []
            for cp in competition_problems:
                problem = cp.problem
                problems_data.append({
                    'id': problem.id,
                    'title': cp.alias,  # 使用比赛中设置的别名
                    'submission_number': cp.submission_number,
                    'accepted_number': cp.accepted_number,
                    'AC Rate': round(cp.accepted_number / cp.submission_number * 100, 2) if cp.submission_number > 0 else 0.00
                })

            return Response({
                'code': 0,
                'data': problems_data,
                'message': 'success'
            })
            
        except Competition.DoesNotExist:
            return Response({
                'code': 1,
                'message': '比赛不存在'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'code': 1,
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class ProblemDetails(APIView):

    def get(self, request, competition_id, problem_id):
        # 获取比赛信息和题目别名
        competition = Competition.objects.get(id=competition_id)
        competition_problem = competition.competitionproblem_set.get(problem_id=problem_id)

        # 获取原题目详情
        problem = competition_problem.problem

        # 返回题目详情，使用比赛中的别名
        data = {
            "code": 200,
            "msg": "success",
            "data": {
                "id": problem.id,
                "title": competition_problem.alias,  # 使用比赛中的别名
                "description": problem.description,
                "hint": problem.hint,
                "samples": problem.samples,
                "source": problem.source,
                "languages": problem.languages,
                "submission_number": competition_problem.submission_number,  # 使用比赛内的提交数
                "accepted_number": competition_problem.accepted_number,  # 使用比赛内的通过数
                "score": competition_problem.score  # 比赛中的题目分数
            }
        }
        return Response(data)


class SubmissionListAPI(APIView):

    def post(self,request):
        id = request.data.get("id")
        data = Submit.objects.filter(competition_id = id).order_by('-submit_time')
        serializer = SubmitSerializer(data, many=True)
        serializer_data = serializer.data

        # 先获取该比赛的所有题目信息
        competition_problems = CompetitionProblem.objects.filter(competition_id=id)
        # 创建一个字典用于快速查找，key是problem_id
        problem_map = {str(cp.problem.id): cp for cp in competition_problems}

        # 为每个提交记录添加题目别名
        for submission in serializer_data:
            problem_id = str(submission['problem'])
            if problem_id in problem_map:
                cp = problem_map[problem_id]
                # 使用比赛中的题目别名
                submission['problem'] = cp.alias
                # 计算通过率
                #submission['acRate'] = round(cp.accepted_number / cp.submission_number * 100, 2) if cp.submission_number > 0 else 0.00

        return Response(serializer_data)