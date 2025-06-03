from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.db.models import JSONField
import json
# 用户的权限的定义
class AdminType(object):
    REGULAR_USER = "Regular User"
    ADMIN = "Admin"
    SUPER_ADMIN = "Super Admin"

# 用户对题目的权限
class ProblemPermission(object):
    NONE = "None"
    Part = "Part"
    ALL = "All"

#定义了一个管理模型
class UserManager(models.Manager):
    use_in_migrations = True

    def get_by_natural_key(self, username):
        return self.get(**{f"{self.model.USERNAME_FIELD}__iexact": username})

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('admin_type', AdminType.SUPER_ADMIN)
        extra_fields.setdefault('problem_permission', ProblemPermission.ALL)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('admin_type') != AdminType.SUPER_ADMIN:
            raise ValueError('Superuser must have admin_type=SUPER_ADMIN.')

        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

# 这里定义用户的数据，姓名，邮箱，创建时间，用户类型，题目权限，是否被禁用
class User(AbstractBaseUser):
    username = models.CharField(unique=True,max_length=150)
    email = models.TextField(null=True)
    create_time = models.DateTimeField(auto_now_add=True, null=True)
    admin_type = models.TextField(default=AdminType.REGULAR_USER)
    problem_permission = models.TextField(default=ProblemPermission.NONE)
    is_disabled = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def is_admin(self):
        return self.admin_type == AdminType.ADMIN

    def is_super_admin(self):
        return self.admin_type == AdminType.SUPER_ADMIN

    def is_admin_role(self):
        return self.admin_type in [AdminType.ADMIN, AdminType.SUPER_ADMIN]

    def can_mgmt_all_problem(self):
        return self.problem_permission == ProblemPermission.ALL

    def is_contest_admin(self, contest):
        return (self.is_authenticated
                and (contest.created_by == self or self.admin_type == AdminType.SUPER_ADMIN))

    class Meta:
        db_table = "user"
    
    is_staff = models.BooleanField(
        default=False,
        help_text='指定用户是否可以登录到管理站点。'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='指定该用户账号是否可用。'
    )

    def has_perm(self, perm, obj=None):
        "用户是否有特定权限"
        return self.is_admin_role()

    def has_module_perms(self, app_label):
        "用户是否有查看特定应用的权限"
        return self.is_admin_role()

    
    # def is_staff(self):
    #     "用户是否为工作人员"
    #     return self.is_admin_role()
# 用户数据表的附表
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # acm_problems_status = JSONField(default=dict, null=True)
    # oi_problems_status = JSONField(default=dict, null=True)
    accepted = JSONField(default=dict, null=True)
    real_name = models.TextField(null=True)
    avatar = models.TextField(default="/static/default.jpg")
    blog = models.URLField(null=True)
    mood = models.TextField(null=True)
    github = models.TextField(null=True)
    school = models.TextField(null=True)
    major = models.TextField(null=True)
    language = models.TextField(null=True)
    # for ACM
    accepted_number = models.IntegerField(default=0)
    # for OI

    submission_number = models.IntegerField(default=0)

    def add_accepted_problem_number(self):
        self.accepted_number = models.F("accepted_number") + 1
        self.save()

    def add_submission_number(self):
        self.submission_number = models.F("submission_number") + 1
        self.save()

    def add_accepted(self,problem_id):
        # if problem_id not in self.accepted:
        #     id=json.dumps({problem_id})

        pass
    

    class Meta:
        db_table = "user_profile"