from django.db import models
from django_ckeditor_5.fields import CKEditor5Field
from django.db.models import JSONField
from user.models import User
import json
from django.core.serializers.json import DjangoJSONEncoder

# 自定义JSON编码器，支持富文本内容
class RichTextJSONEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'as_rich_text'):
            return obj.as_rich_text()
        return super().default(obj)


# 自定义JSON字段，支持富文本
class RichTextJSONField(JSONField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('encoder', RichTextJSONEncoder)
        super().__init__(*args, **kwargs)


class ProblemTag(models.Model):
    # 定义一个名为 ProblemTag 的模型类，继承自 Django 的 models.Model
    name = models.TextField()
    # 定义一个名为 name 的字段，类型为 TextField，用于存储问题标签的名称
    class Meta:
        # 定义模型的元数据
        db_table = "problem_tag"


class ProblemTest(models.Model):
    problem = models.CharField(max_length=255, null=True, blank=True, default='default_problem')  # 允许为空并设置默认值
    test = JSONField()  # 测试用例，存储为JSON格式
    class Meta:
        db_table = "problem_test"



class Problem(models.Model):
    # display ID
    _id = models.CharField(db_index=True,max_length=255)  # 问题显示的ID，设置为数据库索引以加快查询速度

    # for contest problem

    is_public = models.BooleanField(default=True)  # 是否为公开问题，默认为True

    title = models.TextField()  # 问题的标题

    description = CKEditor5Field(config_name='extends',null=True,blank=True)  # 问题的详细描述，支持富文本
    # samples 字段修改为支持富文本的JSON格式
    # 示例格式: [{"input": "<p>输入示例</p>", "output": "<p>输出示例</p>"}, ...]
    samples = RichTextJSONField(
        help_text="示例输入输出，支持富文本格式。格式为: [{'input': '<p>输入内容</p>', 'output': '<p>输出内容</p>'}, ...]"
    )  # 示例输入输出，存储为JSON格式，内部支持富文本内容

    run_test =RichTextJSONField(null=True,blank=True, help_text = "和samples一样")  # 默认运行数据

    hint = CKEditor5Field(null=True,config_name='extends')  # 提示信息，支持富文本，可以为空

    languages = JSONField()  # 支持的编程语言，存储为JSON格式

    create_time = models.DateTimeField(auto_now_add=True)  # 创建时间，自动设置为当前时间

    last_update_time = models.DateTimeField(null=True,blank=True)  # 最后更新时间，可以为空

    created_by = models.ForeignKey(User, on_delete=models.CASCADE)  # 创建者的外键，级联删除
    # ms
    time_limit = JSONField()  # 时间限制，单位为毫秒
    # MB
    memory_limit = JSONField()   # 内存限制，单位为MB

    Stack_memory_limit = models.IntegerField(null=True,blank=True)  # 栈内存限制，单位为MB

    test = models.ForeignKey(
        ProblemTest, 
        null=False, 
        on_delete=models.CASCADE,
        related_name='related_problems'  # 添加 related_name 解决命名冲突
    )  # 关联到ProblemTest模型的外键

    template = RichTextJSONField(null=True,blank=True)  # 模板，支持富文本

    mode = models.TextField(default="OI")  # 模式，默认为"OI"

    visible = models.BooleanField(default=True)  # 是否可见，默认为True

    difficulty = models.CharField(max_length=20,default="1",choices=[('1','Low'),('2','Mid'),('3','High')])  # 难度等级

    tags = models.ManyToManyField(ProblemTag)  # 多对多关联到ProblemTag模

    source = models.TextField(null=True,blank=True)  # 问题的来源，可以为空

    submission_number = models.BigIntegerField(default=0)  # 提交次数，默认为0

    accepted_number = models.BigIntegerField(default=0)  # 通过次数，默认为0



    class Meta:
        db_table = "problem"  # 数据库表名为"problem"
        unique_together = (("_id"),)  # 联合唯一约束，_id和contest的组合必须唯一
        ordering = ("create_time",)  # 默认排序字段为创建时间

    def accept(self):
        self.accepted_number += 1
        self.save()
        return self.accepted_number
    def summit(self):
        self.submission_number += 1
        self.save()
        return self.submission_number


    




class Run(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 运行者的外键，级联删除
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)  # 关联到Problem模型的外键，级联删除
    code = models.TextField()  # 提交的代码
    language = models.CharField(max_length=50)  # 提交使用的编程语言
    submit_time = models.DateTimeField(auto_now_add=True)  # 提交时间，自动设置为当前时间
    status = models.CharField(max_length=50,blank=True)  # 提交状态
    result = models.JSONField(null=True, blank=True)  # 提交结果


    class Meta:
        db_table = "Run"  # 数据库表名为"submission"
        ordering = ("submit_time",)  # 默认排序字段为创建时间