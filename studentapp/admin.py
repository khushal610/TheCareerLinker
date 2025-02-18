from django.contrib import admin
from studentapp import models

# Register your models here.
admin.site.register(models.User)
admin.site.register(models.Quiz_attempt)
