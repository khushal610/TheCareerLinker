from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class User(AbstractUser):
    ADMIN = 'Admin'
    DEVELOPER = 'Developer'
    STUDENT = 'Student'

    role = models.CharField(max_length=20,null=True,blank=True,default=STUDENT)

    # student registration fields
    contact = models.BigIntegerField(null=True,blank=True)
    address = models.CharField(max_length=255,null=True,blank=True)
    institute_name = models.CharField(max_length=70,null=True,blank=True)
    last_sem_marksheet = models.FileField(upload_to='student_marksheet/',null=True,blank=True)
    student_resume = models.FileField(upload_to='student_resume/',null=True,blank=True)
    course = models.CharField(max_length=20,null=True,blank=True)

    # developer registration fields
    company_name = models.CharField(max_length=70,null=True,blank=True)
    bio_title = models.CharField(max_length=70,null=True,blank=True)
    bio_detail = models.TextField(null=True,blank=True)
    experties = models.CharField(max_length=70,null=True,blank=True)
    experience = models.CharField(max_length=20,null=True,blank=True)
    dev_img = models.FileField(upload_to='developer_images/',null=True,blank=True)
    is_verified = models.BooleanField(default=False)