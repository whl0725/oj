from django.contrib import admin
from .models import Problem,ProblemTag,ProblemTest

admin.site.register(Problem)
admin.site.register(ProblemTag)
admin.site.register(ProblemTest)