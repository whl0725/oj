from django.db import models

from user.models import User
from django_ckeditor_5.fields import CKEditor5Field


# class QAmodel(models.Model):
#     content = RichTextField(verbose_name='首页公告', config_name='default')
    # config_name指定ckeditor配置文件，不指定就使用default

# 定义公告模型，继承自Django的Model类
class Announcement(models.Model):
    # 定义公告标题字段，使用TextField类型，可以存储较长的文本
    title = models.TextField()
    # 定义公告内容字段，使用RichTextField类型，支持富文本编辑，可以存储HTML格式的文本
    content = CKEditor5Field('内容',config_name='extends')
    # 定义创建时间字段，使用DateTimeField类型，auto_now_add=True表示在创建对象时自动设置当前时间
    create_time = models.DateTimeField(auto_now_add=True)
    # 定义创建者字段，使用ForeignKey类型，关联到User模型，on_delete=models.CASCADE表示当关联的User对象被删除时，该公告也会被删除
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    # 定义最后更新时间字段，使用DateTimeField类型，auto_now=True表示在每次保存对象时自动设置当前时间
    last_update_time = models.DateTimeField(auto_now=True)
    # 定义可见性字段，使用BooleanField类型，默认值为True，表示公告是否可见
    visible = models.BooleanField(default=True)

    class Meta:
        # 定义模型的元数据
        db_table = "announcement"
        # 指定数据库表名为"announcement"
        ordering = ("-create_time",)
