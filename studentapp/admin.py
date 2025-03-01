from django.contrib import admin
from studentapp import models

# Register your models here.
admin.site.register(models.User)
admin.site.register(models.Bookmarked_session)


class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'quiz_category', 'score', 'date_time')  
    readonly_fields = ('date_time',)
admin.site.register(models.Quiz_attempt, QuizAttemptAdmin)

class AttemptedSessionAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'student_name', 'date_time', 'is_attempted')  
    readonly_fields = ('date_time',)
admin.site.register(models.Attempted_session, AttemptedSessionAdmin)

# @admin.register(models.Quiz_attempt)
# class Quiz_attempt(admin.ModelAdmin):
#     list_display = ['student_id','quiz_category','score','date_time']
    # model = models.Quiz_attempt