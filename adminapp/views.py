from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from devapp import models as devModels
from devapp import forms
from studentapp import models

# Create your views here.
def index(request):
    totalStudents = models.Registration.objects.all().count()
    totalDevelopers = devModels.DevList.objects.all().count()
    context = {
        'totalStudents':totalStudents,
        'totalDevelopers':totalDevelopers,
    }
    return render(request,'adminapp/index.html',context=context)

def signIn(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username,password=password)
        if user is not None:
            login(request,user)
            return redirect(index)
        else:
            return HttpResponse("Please Enter valid data")
    return render(request,'adminapp/signin.html')

def signout(request):
    logout(request)
    return redirect(signIn)

def formview(request):
    return render(request,'adminapp/form.html')

def studentTable(request):
    data = models.Registration.objects.all
    context = {'data':data}
    return render(request,'adminapp/student-table.html',context=context)

def deleteUser(request,id):
    data = models.Registration.objects.get(id=id)
    data.delete()
    return redirect(studentTable)

def chartview(request):
    return render(request,'adminapp/chart.html')

def widget(request):
    return render(request,'adminapp/widget.html')

def assessment(request):
    return render(request,'adminapp/assessment.html')

def dev_add_form(request):
    return render(request,'adminapp/dev-add-form.html')

def admin_add_form(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirmPassword = request.POST.get('confirmPassword')
        if password == confirmPassword:
            try:
                User.objects.get(username=username)
                return render(request,"adminapp/admin-add-form.html",{'alert':"Admin already exist"})
            except:
                User.objects.create_user(username=username,password=password)
                return render(request,"adminapp/admin-add-form.html",{'new_add_msg':"New Admin Created"})
        else:
            return render(request,"adminapp/admin-add-form.html",{'error':"Password Doesn't Match"})
    return render(request,"adminapp/admin-add-form.html")


def dev_list_table(request):
    devData = devModels.DevList.objects.all()
    context = {'devData':devData}
    return render(request,"adminapp/dev-table.html",context=context)


def authorize_dev(request,id):
    data = devModels.DevList.objects.get(id=id)
    if request.method == "POST":
        data.is_verified = True
        data.save()
        return redirect(dev_list_table)
    return render(request,"adminapp/dev-table.html")

def unauthorize_dev(request,id):
    data = devModels.DevList.objects.get(id=id)
    if request.method == "POST":
        data.is_verified = False
        data.save()
        return redirect(dev_list_table)
    return render(request,"adminapp/dev-table.html")

def deleteDev(request,id):
    data = devModels.DevList.objects.get(id=id)
    data.delete()
    return redirect(dev_list_table)