from django.contrib import admin
from devapp import models

# Register your models here.
admin.site.register(models.QuizCategory)
admin.site.register(models.QuizQuestions)
admin.site.register(models.QuizOptions)
admin.site.register(models.Online_sessions)
admin.site.register(models.Online_Certification_Course)
admin.site.register(models.Module_list)
admin.site.register(models.Module_Stage)
admin.site.register(models.Course_Module_Content)
admin.site.register(models.Certificate_Details)
admin.site.register(models.Issued_Certificate)