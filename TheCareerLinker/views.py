from django.shortcuts import render,redirect
from studentapp import views as student_views
from devapp import views as dev_views
from adminapp import views as admin_views
from django.contrib.auth import login,logout,authenticate

def main_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request,username=username,password=password)
        if user is not None and user.role == "Student":
            login(request,user)
            return redirect(student_views.home)
        elif user is not None and user.role == "Developer":
            if user.is_verified == True:
                login(request,user)
                return redirect(dev_views.index)
            else:
                print("developer is not authorized")
                return render(request,'login.html',{'error':"Wait until you are authorize"})
        elif user is not None and user.role == "Admin":
            login(request,user)
            return redirect(admin_views.index)
        else:
            return render(request,'login.html',{'error':"User doesn't exist"})
    return render(request,"login.html")