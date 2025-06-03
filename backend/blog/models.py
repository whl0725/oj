from django.db import models
from django_ckeditor_5.fields import CKEditor5Field
from user.models import User

class Blog(models.Model):
    title = models.CharField(max_length=200)
    content = CKEditor5Field('Content', config_name='extends')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField(default=True)
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    
    class Meta:
        db_table = "blog"
        ordering = ['-created_at']
        
    def __str__(self):
        return self.title

class Comment(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = CKEditor5Field('Comment', config_name='default')
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    
    class Meta:
        db_table = "comment"
        ordering = ['created_at']
        
    def __str__(self):
        return f'Comment by {self.author.username} on {self.blog.title}'
    