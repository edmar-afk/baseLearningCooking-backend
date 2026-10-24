from django.contrib import admin
from .models import UserExtraInfo, Quizzes, Lessons

admin.site.register(UserExtraInfo)
admin.site.register(Quizzes)
admin.site.register(Lessons)