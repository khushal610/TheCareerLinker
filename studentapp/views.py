from django.shortcuts import render,HttpResponse,redirect
from studentapp import forms
from studentapp import models
from django.contrib.auth import authenticate,login,logout
from devapp import models as devModels
from django.core.mail import send_mail
from django.conf import settings
import math,random

# Create your views here.
# index page 
def home(request):
    username = request.session.get('username')
    return render(request,'studentapp/index.html',{'username':username})

# about page
def about(request):
    username = request.session.get('username')
    return render(request,'studentapp/about.html',{'username':username})

# contact page
def contact(request):
    return render(request,'studentapp/contact.html')

# courses page
def courses(request):
    return render(request,'studentapp/courses.html')

# course-details page
def courseDetails(request):
    return render(request,'studentapp/course-details.html')

# trainers page
def trainers(request):
    dev_data = devModels.DevList.objects.all()
    dev_bio_data = devModels.DevBio.objects.all()
    context = {
        'dev_data':dev_data,
        'dev_bio_data':dev_bio_data
    }
    return render(request,'studentapp/trainers.html',context=context)

# pricing page
def pricing(request):
    return render(request,'studentapp/pricing.html')

# profile page
def profile(request):
    username = request.session.get('username')
    uemail = request.session.get('uemail')
    userdata = models.Registration.objects.get(email=uemail)
    context = {'username': username,'uemail': uemail,'userdata': userdata}
    return render(request,'studentapp/profile.html',context=context)

# registration page
def registration(request):
    if request.method == "POST":
        password = request.POST.get('password')
        confirmPassword = request.POST.get('confirmPassword')
        if password == confirmPassword:
            register_form = forms.RegistrationForm(request.POST,request.FILES)
            email = request.POST.get("email")
            try:
                user = models.Registration.objects.get(email=email)
                return HttpResponse("email is already registered")
            except:
                if register_form.is_valid():
                    register_form.save()
                    return redirect(loginview)
                else:
                    print(register_form.errors)
                    return HttpResponse("errors")
                # form = forms.RegistrationForm(request.POST,request.FILES)
        else:
            return render(request,'studentapp/registration.html',{'error':"Password Does Not Match"})
    else:
        register_form = forms.RegistrationForm()
    return render(request,'studentapp/registration.html')

# login
def loginview(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = models.Registration.objects.get(email=email)

        if user.password == password:
            request.session['username'] = user.first_name + " " +user.last_name
            request.session['uemail'] = user.email
            return redirect(home)
        else:
            return render(request,'studentapp/login.html',{'error':"Invalid Password"})
    return render(request,'studentapp/login.html')

# logout
def signout(request):
    # logout(request)
    request.session.flush()
    return redirect(loginview)

# forgot password
def forgot_password(request):
    if request.method == "POST":
        user_email = request.POST.get('email')
        try:
            check_user_exist = models.Registration.objects.get(email=user_email)
            generated_otp = send_otp_email(user_email)
            request.session['OTP'] = generated_otp
            request.session['USER_EMAIL'] = user_email
            print("forgot password page -------------------->",generate_otp)
            return redirect(compare_otp)
        except:
            return render(request,"studentapp/forgot-password.html",{'error':"Please Register First"})
        
    return render(request,"studentapp/forgot-password.html")

# otp email sending method
def send_otp_email(user_email):
    OTP = generate_otp()
    subject = "Reset Password"
    message = f"To reset your password your OTP is : {OTP}"
    from_email = settings.EMAIL_HOST_USER
    to_email = user_email
    print("send_otp_email : method ---------------------->",OTP)
    send_mail(subject, message, from_email, [to_email])
    return OTP

# otp generating method
def generate_otp():
    numbers = "0123456789"
    OTP = ""
    for i in range(6):
        OTP += numbers[math.floor(random.random() * 10)]
    return OTP

# comparison of otp
def compare_otp(request):
    if request.method == "POST":
        user_otp = request.POST.get('user_otp')
        system_otp = request.session.get('OTP')
        if user_otp == system_otp:
            return redirect(reset_password)
        else:
            return render(request,"studentapp/compare-otp.html",{'otp_error':"OTP is not matched"})
        print("compare_otp page --------------------------->",system_otp)
    return render(request,"studentapp/compare-otp.html")

# changing the password
def reset_password(request):
    if request.method == "POST":
        new_pass = request.POST.get('new_pass')
        new_confirm_pass = request.POST.get('new_confirm_pass')
        if new_pass == new_confirm_pass:
            user_email = request.session.get('USER_EMAIL')
            check_user_exist = models.Registration.objects.get(email=user_email)
            try:
                check_user_exist.password = new_pass
                check_user_exist.save()
                request.session.flush()
                return redirect(loginview)
            except:
                return render(request,"studentapp/reset-password.html",{'error':"User Not Found"})
        else:
            return render(request,"studentapp/reset-password.html",{'error':"Password doesn't match"})
    return render(request,"studentapp/reset-password.html")