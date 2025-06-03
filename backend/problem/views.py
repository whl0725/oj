from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Problem,ProblemTag
# from .serializers import ProblemDetailSerializer
import requests
import json
import logging
from .serializers import ProblemTagSerializer,ProblemListSerializer
from rest_framework.permissions import IsAuthenticated
from django.core.paginator import Paginator

class ProblemSubminAPI(APIView):
    JUDGE_SERVER_URL = 'http://116.205.124.191:5000/'
    JUDGE_TOKEN = '123456'

    def get_test_cases(self):
        return [

        ]

    def post(self, request):
        try:
            # 获取提交的代码
            code = request.data.get("code")
            if not code:
                return Response({
                    "code": 400,
                    "msg": "代码不能为空",
                    "data": None
                }, status=400)

            # 准备判题数据
            judge_data = {
                "src": code,
                "language": "cpp",
                "max_cpu_time": 1000,  # 1秒
                "max_memory": 128 * 1024 * 1024,  # 128MB
                "test": self.get_test_cases(),
                "test_display": 1
            }

            # 发送到判题服务器
            headers = {
                'judgertoken': self.JUDGE_TOKEN,
                'Content-Type': 'application/json'
            }

            response = requests.post(
                self.JUDGE_SERVER_URL,
                json=judge_data,
                headers=headers,
                timeout=50000  # 30秒超时
            )
            # 检查响应状态
            if response.status_code == 200:
                judge_result = response.json()
                if judge_result['accepted_count'] == judge_result["total_count"]:
                    return Response({
                        "code": 200,
                        "msg": "答案正确",
                    })
                else:
                    return Response({
                        "code":200,
                        "msg" :"答案不对",
                    })
            else:
                # 尝试解析错误信息
                try:
                    error_data = response.json()
                except json.JSONDecodeError:
                    error_data = {"message": response.text}

                return Response({
                    "code": response.status_code,
                    "msg": "判题失败",
                    "error": error_data.get("message", "未知错误"),
                    "data": error_data
                }, status=400)

        except requests.Timeout:
            return Response({
                "code": 408,
                "msg": "判题服务器响应超时",
                "data": None
            }, status=408)

        except requests.RequestException as e:
            return Response({
                "code": 500,
                "msg": "网络请求错误",
                "error": str(e),
                "data": None
            }, status=500)

        except Exception as e:
            return Response({
                "code": 500,
                "msg": "服务器内部错误",
                "error": str(e),
                "data": None
            }, status=500)



class ProblemDetails(APIView):
    def get(self, request):
        problem_id = request.query_params.get('problem_id')
        #print(f"获取的题目ID: {problem_id}, 类型: {type(problem_id)}")

        if not problem_id:
            return Response({
                "code": 400,
                "msg": "缺少题目ID参数",
                "data": None
            }, status=400)

        try:
            # 尝试转换ID格式（如果需要的话）
            # 如果 _id 字段是整数类型但从URL获取的是字符串
            try:
                # 根据您的模型字段类型调整转换方式
                problem_id_converted = int(problem_id)
            except (ValueError, TypeError):
                problem_id_converted = problem_id

            #print(f"查询参数: _id={problem_id_converted}, 类型: {type(problem_id_converted)}")

            # 尝试获取题目
            problem = Problem.objects.get(_id=problem_id_converted)
            #print(f"找到题目: {problem.title}")

            # 返回题目详情
            data = {
                "code": 200,
                "msg": "success",
                "data": {
                    "title": problem.title,
                    "description": problem.description,
                    "hint":problem.hint,
                    "samples": problem.samples,
                    "source":problem.source,
                    "languages": problem.languages,
                    # 其他字段...
                }
            }
            #print(f"返回数据: {data}")
            return Response(data)

        except Problem.DoesNotExist:
            print(f"题目不存在: _id={problem_id}")
            return Response({
                "code": 404,
                "msg": "题目不存在",
                "data": None
            }, status=200)
        except Exception as e:
            import traceback
            traceback_str = traceback.format_exc()
            print(f"获取题目详情失败: {str(e)}\n{traceback_str}")
            return Response({
                "code": 500,
                "msg": "获取题目详情失败",
                "error": str(e),
                "data": None
            }, status=500)



class Problem_Tag(APIView):
    """
    获取所有题目标签API
    """
    def get(self, request):
        tags = ProblemTag.objects.all()
        tag_data = ProblemTagSerializer(tags, many=True)
        return Response(tag_data.data)


class ProblemList(APIView):
    """
    获取所有题目列表API，支持分页、难度筛选和搜索
    """
    permission_classes = [IsAuthenticated]
    def get(self, request):
        # 获取分页参数
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))
        difficulty = request.query_params.get('difficulty', '')
        keyword = request.query_params.get('keyword', '').strip()
        
        # 获取所有公开题目
        query = Problem.objects.filter(is_public=True)
        
        # 按难度筛选
        if difficulty:
            difficulty_map = {
                'easy': '1',
                'medium': '2',
                'hard': '3'
            }
            if difficulty.lower() in difficulty_map:
                query = query.filter(difficulty=difficulty_map[difficulty.lower()])
        
        # 按关键词搜索标题
        if keyword:
            query = query.filter(title__icontains=keyword)
        
        # 创建分页器
        paginator = Paginator(query, page_size)
        total = paginator.count
        
        try:
            # 获取当前页的数据
            current_page = paginator.page(page)
        except:
            return Response({
                "code": 400,
                "msg": "页码参数错误",
                "data": None
            })
            
        # 序列化数据
        problem_data = ProblemListSerializer(current_page.object_list, many=True)
        
        # 处理数据
        problems_list = problem_data.data
        for problem in problems_list:
            problem['AC Rate'] = round(problem['accepted_number'] / problem['submission_number'] * 100, 2) if problem['submission_number'] != 0 else 0
            del problem['accepted_number']
        
        # 返回带分页信息的响应
        return Response({
            "code": 200,
            "msg": "success",
            "data": {
                "total": total,
                "problems": problems_list,
                "current_page": page,
                "page_size": page_size
            }
        })