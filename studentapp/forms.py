# from django import forms
# from studentapp import models
# from django.contrib.auth.forms import UserCreationForm

# class Student_Reg_Form(forms.ModelForm):
#     contact = forms.IntegerField(required=True)
#     address = forms.CharField(max_length=255,required=True)
#     institute_name = forms.CharField(max_length=70,required=True)
#     last_sem_marksheet = forms.FileField(required=True)
#     student_resume = forms.FileField(required=True)
#     course = forms.CharField(max_length=20,required=True)

#     class Meta:
#         model = models.User
#         fields = ['username','email','contact','password','address','institute_name','last_sem_marksheet','student_resume','course']


# class Developer_Reg_Form(forms.ModelForm):
#     contact = forms.IntegerField(required=True)
#     address = forms.CharField(max_length=255,required=True)
#     company_name = forms.CharField(max_length=70,required=True)
#     bio_title = forms.CharField(max_length=70,required=True)
#     bio_detail = forms.CharField(max_length=255,required=True)
#     experties = forms.CharField(max_length=70,required=True)
#     experience = forms.CharField(max_length=20,required=True)
#     dev_img = forms.FileField(required=True)

#     class Meta:
#         model = models.User
#         fields = ['username','email','contact','password','address','company_name','bio_title','bio_detail','experties','experience','dev_img']