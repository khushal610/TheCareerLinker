from django.shortcuts import render,HttpResponse,redirect
from studentapp import forms
from studentapp import models
from django.contrib.auth import authenticate,login,logout

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
    return render(request,'studentapp/trainers.html')

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


def signout(request):
    # logout(request)
    request.session.flush()
    return redirect(loginview)