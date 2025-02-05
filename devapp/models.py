from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
# class User(AbstractUser):
    # ADMIN = 'Admin'
    # DEVELOPER = 'Developer'
    # STUDENT = 'Student'

#     company_name = models.CharField(max_length=50)
#     bio_title = models.CharField(max_length=70)
#     bio_detail = models.TextField(max_length=255)
#     experties = models.CharField(max_length=50)
#     experience = models.CharField(max_length=20)
#     dev_img = models.FileField(upload_to='developer_images/')
#     is_verified = models.BooleanField(default=False)
#     role = models.CharField(default=DEVELOPER)


# class DevBio(models.Model):
#     dev_id = models.ForeignKey(DevList,on_delete=models.CASCADE)


# class QuizCategory(models.Model):
#     quiz_category_name = models.CharField(max_length=100)
#     quiz_level = models.CharField(max_length=15)
#     dev_id = models.ForeignKey(DevList,on_delete=models.CASCADE)