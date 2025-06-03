from django.db import models
from django_ckeditor_5.fields import CKEditor5Field
from user.models import User
from django.db.models import JSONField
from problem.models import Problem
from home.models import Announcement

class CompetitionProblem(models.Model):
    competition = models.ForeignKey('Competition', on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    alias = models.CharField(max_length=255,blank=True,null=True)  # 比赛中的题目别名
    score = models.IntegerField(default=0)  # 题目在比赛中的分数
    submission_number = models.BigIntegerField(default=0)  # 比赛内提交数
    accepted_number = models.BigIntegerField(default=0)  # 比赛内通过数

    class Meta:
        db_table = "competition_problem"
        unique_together = ('competition', 'problem')  # 确保题目在比赛中唯一


class Competition(models.Model):
    # 比赛标题
    title = models.TextField()
    # 比赛描述，使用富文本字段
    description = CKEditor5Field(config_name='extends')

    # show real time rank or cached rank
    real_time_rank = models.BooleanField()
    ContestType = models.CharField(max_length=100, choices=[('0', 'Public'), ('1', 'Password Protected')],blank=True)
    password = models.TextField(null=True)
    # enum of ContestRuleType
    rule_type = models.CharField(max_length=100, choices=[('0', 'ACM'), ('1', 'OI')])

    start_time = models.DateTimeField()

    end_time = models.DateTimeField()

    create_time = models.DateTimeField(auto_now_add=True)

    last_update_time = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    # 是否可见 false的话相当于删除
    visible = models.BooleanField(default=True)

    problems = models.ManyToManyField(Problem, through=CompetitionProblem)
    announcements = models.ManyToManyField(Announcement)
    class Meta:
        db_table = "competition"
        ordering = ("-start_time",)


class Submit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)  # 提交者的外键，级联删除
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)  # 关联到Problem模型的外键，级联删除
    code = models.TextField()  # 提交的代码
    language = models.CharField(max_length=50)  # 提交使用的编程语言
    submit_time = models.DateTimeField(auto_now_add=True)  # 提交时间，自动设置为当前时间
    status = models.CharField(max_length=50)  # 提交状态

    result = models.JSONField(null=True, blank=True)  # 提交结果

    competition = models.ForeignKey(Competition, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        db_table = "submission"  # 数据库表名为"submission"
        ordering = ("submit_time",)  # 默认排序字段为创建时间

