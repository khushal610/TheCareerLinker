from django.db import models

# Create your models here.
class DevList(models.Model):
    username = models.CharField(max_length=50)
    company_name = models.CharField(max_length=50)
    email = models.EmailField()
    contact = models.IntegerField()
    password = models.CharField(max_length=16)
    is_verified = models.BooleanField(default=False)