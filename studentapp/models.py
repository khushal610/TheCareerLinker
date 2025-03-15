from django.contrib.auth.models import AbstractUser
from django.db import models
# from devapp.models import QuizCategory

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
    is_selected = models.BooleanField(default=False)

    # developer registration fields
    company_name = models.CharField(max_length=70,null=True,blank=True)
    bio_title = models.CharField(max_length=70,null=True,blank=True)
    bio_detail = models.TextField(null=True,blank=True)
    experties = models.CharField(max_length=70,null=True,blank=True)
    experience = models.CharField(max_length=20,null=True,blank=True)
    dev_img = models.FileField(upload_to='developer_images/',null=True,blank=True)
    is_verified = models.BooleanField(default=False)

class Quiz_attempt(models.Model): # id
    student_id = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    quiz_category = models.ForeignKey("devapp.QuizCategory",on_delete=models.CASCADE,null=True,blank=True)
    score = models.IntegerField(null=True,blank=True,default=0)
    date_time = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    # quiz_category = models.ForeignKey(QuizCategory,on_delete=models.CASCADE)

class Attempted_session(models.Model):
    session_id = models.ForeignKey("devapp.Online_sessions",on_delete=models.CASCADE,null=True,blank=True)
    student_name = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    date_time = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    is_attempted = models.BooleanField(default=False)

class Bookmarked_session(models.Model):
    session_id = models.ForeignKey("devapp.Online_sessions",on_delete=models.CASCADE,null=True,blank=True)
    student_id = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    is_bookmarked = models.BooleanField(default=False)

class Course_Enrollment(models.Model):
    student_id = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    course_id = models.ForeignKey("devapp.Online_Certification_Course",on_delete=models.CASCADE,null=True,blank=True)
    is_payment_received = models.BooleanField(default=False)
    is_course_completed = models.BooleanField(default=False)
    date_time = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    razorpay_payment_id = models.CharField(max_length=255, null=True, blank=True)
    razorpay_order_id = models.CharField(max_length=255, null=True, blank=True)
    razorpay_signature = models.CharField(max_length=255, null=True, blank=True)

class Course_Progress_Tracker(models.Model):
    student_id = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    course_id = models.ForeignKey("devapp.Online_Certification_Course",on_delete=models.CASCADE,null=True,blank=True)
    document_id = models.ForeignKey("devapp.Course_Module_Content",on_delete=models.CASCADE,null=True,blank=True)
    quiz_id = models.ForeignKey("devapp.QuizCategory",on_delete=models.CASCADE,null=True,blank=True)
    is_completed = models.BooleanField(default=False)
    date_time = models.DateTimeField(auto_now_add=True,null=True,blank=True)

class Contact_us(models.Model):
    user_id = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    subject = models.CharField(max_length=255,null=True,blank=True)
    message = models.TextField(null=True,blank=True)