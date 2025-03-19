from django.db import models
from django.conf import settings
from studentapp.models import Student_Course_Query


class QuizCategory(models.Model): # id
    quiz_category_name = models.CharField(max_length=100,null=True,blank=True)
    quiz_level = models.CharField(max_length=15,null=True,blank=True)
    is_approved = models.BooleanField(default=False)
    is_course_quiz = models.BooleanField(default=False)
    dev_id = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)

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

class Online_Certification_Course(models.Model):
    course_name = models.CharField(max_length=255,null=True,blank=True)
    course_thumbnail_image = models.FileField(upload_to='course_thumbnail_images/',null=True,blank=True)
    course_summary = models.TextField(null=True,blank=True)
    course_duration = models.CharField(max_length=255,null=True,blank=True)
    course_type = models.CharField(max_length=255,null=True,blank=True)
    course_charges = models.CharField(max_length=255,null=True,blank=True)
    is_launched = models.BooleanField(default=False)
    dev_id = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)

class Module_list(models.Model):
    module_name = models.CharField(max_length=255,null=True,blank=True)
    course_id = models.ForeignKey(Online_Certification_Course,on_delete=models.CASCADE)
    dev_id = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)

class Module_Stage(models.Model):
    stage_name = models.CharField(max_length=255,null=True,blank=True)
    module_id = models.ForeignKey(Module_list,on_delete=models.CASCADE)
    dev_id = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)


class Course_Module_Content(models.Model): #id
    documentation_name = models.CharField(max_length=255,null=True,blank=True)
    course_documentation = models.TextField(null=True,blank=True)
    course_images = models.FileField(upload_to='course_images/',null=True,blank=True)
    course_pdf = models.FileField(upload_to='course_pdf/',null=True,blank=True)
    course_video = models.FileField(upload_to='course_video/',null=True,blank=True)
    course_quiz = models.ForeignKey(QuizCategory,on_delete=models.CASCADE,null=True,blank=True)
    stage_id = models.ForeignKey(Module_Stage,on_delete=models.CASCADE)
    dev_id = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)

class Certificate_Details(models.Model):
    company_logo = models.FileField(upload_to="company_logo/")
    dev_signature = models.FileField(upload_to="dev_signature/")
    dev_id = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,null=True,blank=True)

class Issued_Certificate(models.Model):
    student_id = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,null=True,blank=True)
    course_id = models.ForeignKey(Online_Certification_Course,on_delete=models.CASCADE,null=True,blank=True)
    certificate_details = models.ForeignKey(Certificate_Details,on_delete=models.CASCADE,null=True,blank=True)
    digital_signature = models.CharField(max_length=255,null=True,blank=True)


class Response_Student_Query(models.Model):
    query_id = models.ForeignKey(Student_Course_Query,on_delete=models.CASCADE,null=True,blank=True)
    dev_id = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,null=True,blank=True)
    response_content = models.TextField(null=True,blank=True)