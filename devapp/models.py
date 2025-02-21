from django.db import models
from django.conf import settings
# from studentapp.models import User


class QuizCategory(models.Model): # id
    quiz_category_name = models.CharField(max_length=100,null=True,blank=True)
    quiz_level = models.CharField(max_length=15,null=True,blank=True)
    is_approved = models.BooleanField(default=False)
    dev_id = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    # dev_id = models.ForeignKey(User,on_delete=models.CASCADE)

class QuizQuestions(models.Model):
    quiz_question = models.CharField(max_length=255,null=True,blank=True)
    quiz_question_summary = models.TextField(null=True,blank=True)
    is_option_added = models.BooleanField(default=False)
    quiz_category_id = models.ForeignKey(QuizCategory,on_delete=models.CASCADE)

class QuizOptions(models.Model):
    option_1 = models.CharField(max_length=255,null=True,blank=True)
    option_2 = models.CharField(max_length=255,null=True,blank=True)
    option_3 = models.CharField(max_length=255,null=True,blank=True)
    option_4 = models.CharField(max_length=255,null=True,blank=True)
    question_id = models.ForeignKey(QuizQuestions,on_delete=models.CASCADE)

class Online_sessions(models.Model): #id
    dev_name = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    topic_name = models.CharField(max_length=255,null=True,blank=True)
    meeting_link = models.URLField(null=True,blank=True)
    start_time = models.TimeField(null=True,blank=True)
    end_time = models.TimeField(null=True,blank=True)
    is_live = models.BooleanField(default=False)
    week_days = models.JSONField(default=list)
    date_time = models.DateTimeField(auto_now_add=True,null=True,blank=True)
# class week_days(models.Model):
