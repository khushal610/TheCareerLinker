from django.contrib import admin
from studentapp import models

# Register your models here.
admin.site.register(models.User)
# admin.site.register(models.Quiz_attempt)


class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'quiz_category', 'score', 'date_time')  # Display in the list view
    readonly_fields = ('date_time',)  # Make it visible in the form but not editable

admin.site.register(models.Quiz_attempt, QuizAttemptAdmin)

# @admin.register(models.Quiz_attempt)
# class Quiz_attempt(admin.ModelAdmin):
#     list_display = ['student_id','quiz_category','score','date_time']
    # model = models.Quiz_attempt