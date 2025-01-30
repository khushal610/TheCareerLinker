from django.db import models

# Create your models here.
class DevList(models.Model):
    username = models.CharField(max_length=50)
    company_name = models.CharField(max_length=50)
    email = models.EmailField()
    contact = models.IntegerField()
    password = models.CharField(max_length=16)
    is_verified = models.BooleanField(default=False)


class DevBio(models.Model):
    dev_id = models.ForeignKey(DevList,on_delete=models.CASCADE)
    bio_summary = models.CharField(max_length=70)
    bio_detail = models.TextField(max_length=255)
    experties = models.CharField(max_length=50)
    experience = models.CharField(max_length=20)
    dev_img = models.FileField(upload_to='developer_images/')