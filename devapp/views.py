from django.shortcuts import render,HttpResponse,redirect
from devapp import models,forms

# Create your views here.
def index(request):
    # return HttpResponse("Dev App Index Page")
    return render(request,'devapp/index.html')

def dev_widget(request):
    return render(request,'devapp/widget.html')

def dev_forms(request):
    return render(request,'devapp/form.html')

def assessment(request):
    return render(request,'devapp/assessment.html')


def dev_signIn(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            findUser = models.DevList.objects.get(email=email)  
            if findUser.is_verified == False:
                print("--------------------------------------->", findUser.is_verified)
                return render(request, "devapp/signin.html", {'auth_error': "Wait until you are authorized"})   
            if findUser.password != password:
                return render(request, "devapp/signin.html", {'auth_error': "Invalid password"})    
            return redirect(index)
        except:
            return render(request, "devapp/signin.html", {'auth_error': "User does not exist"})
    return render(request, "devapp/signin.html")



# ----------------------signup developer
def dev_signUp(request):
    if request.method == "POST":
        username = request.POST.get('username')
        company_name = request.POST.get('company_name')
        email = request.POST.get('email')
        contact = request.POST.get('contact')
        password = request.POST.get('password')
        try:
            ExistedUser = models.DevList.objects.get(username=username)
            return render(request,"devapp/signup.html",{'exist_dev_alert':"Username already exist"})
        except:
            devSignForm = forms.DevListForm(request.POST)
            if devSignForm.is_valid():
                dev_obj = devSignForm.save(commit=False)
                dev_obj.is_verified = False
                dev_obj.save()
                return redirect(dev_signIn)
            else:
                print(devSignForm.errors)
                return render(request,"devapp/signup.html",{'dev_signup_error':"Enter all valid data"})
    return render(request,"devapp/signup.html")