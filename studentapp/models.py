from django.db import models

# Create your models here.
# -------------------- Registration model 
# full_name = models.CharField(max_length=40,default=first_name+last_name)
# username = models.CharField(max_length=50)
class Registration(models.Model):
    first_name = models.CharField(max_length=20,default="")  
    last_name = models.CharField(max_length=20,default="")
    email = models.EmailField()                   
    contact = models.IntegerField()
    password = models.CharField(max_length=10)      
    address = models.CharField(max_length=255)
    institute_name = models.CharField(max_length=70)
    last_sem_marksheet = models.FileField(upload_to='student_marksheet/')
    student_resume = models.FileField(upload_to='student_resume/')
    course = models.CharField(max_length=20,default="B.C.A")

