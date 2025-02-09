from django.db import models
from studentapp.models import User


class QuizCategory(models.Model): # id
    quiz_category_name = models.CharField(max_length=100,null=True,blank=True)
    quiz_level = models.CharField(max_length=15,null=True,blank=True)
    is_approved = models.BooleanField(default=False)
    dev_id = models.ForeignKey(User,on_delete=models.CASCADE)