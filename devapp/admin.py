from django.contrib import admin
from devapp import models

# Register your models here.
admin.site.register(models.QuizCategory)
admin.site.register(models.QuizQuestions)
admin.site.register(models.QuizOptions)
admin.site.register(models.Online_sessions)