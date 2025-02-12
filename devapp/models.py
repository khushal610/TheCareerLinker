from django.db import models
from studentapp.models import User


class QuizCategory(models.Model): # id
    quiz_category_name = models.CharField(max_length=100,null=True,blank=True)
    quiz_level = models.CharField(max_length=15,null=True,blank=True)
    is_approved = models.BooleanField(default=False)
    dev_id = models.ForeignKey(User,on_delete=models.CASCADE)

class QuizQuestions(models.Model):
    quiz_question = models.CharField(max_length=255,null=True,blank=True)
    is_option_added = models.BooleanField(default=False)
    quiz_category_id = models.ForeignKey(QuizCategory,on_delete=models.CASCADE)

class QuizOptions(models.Model):
    option_1 = models.CharField(max_length=255,null=True,blank=True)
    option_2 = models.CharField(max_length=255,null=True,blank=True)
    option_3 = models.CharField(max_length=255,null=True,blank=True)
    option_4 = models.CharField(max_length=255,null=True,blank=True)
    question_id = models.ForeignKey(QuizQuestions,on_delete=models.CASCADE)