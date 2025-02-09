from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from devapp import models as devModels
from devapp import forms
from studentapp.models import User
from TheCareerLinker import views as TCL_views

# Create your views here.
def index(request):
    totalStudents = User.objects.filter(role="Student").count()
    totalDevelopers = User.objects.filter(role="Developer").count()
    totalQuiz = devModels.QuizCategory.objects.count()
    context = {
        'totalStudents':totalStudents,
        'totalDevelopers':totalDevelopers,
        'totalQuiz':totalQuiz,
    }
    return render(request,'adminapp/index.html',context=context)

def signout(request):
    logout(request)
    return redirect(TCL_views.main_login)

def formview(request):
    return render(request,'adminapp/form.html')

def studentTable(request):
    students = User.objects.filter(role="Student",is_superuser=False)
    context = {'students':students}
    return render(request,'adminapp/student-table.html',context=context)

def deleteUser(request,id):
    data = User.objects.get(id=id)
    data.delete()
    return redirect(studentTable)

def chartview(request):
    return render(request,'adminapp/chart.html')

def widget(request):
    return render(request,'adminapp/widget.html')

def assessment(request):
    return render(request,'adminapp/assessment.html')

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
                User.objects.create_user(
                    username=username,
                    password=password,
                    role=User.ADMIN,
                    is_superuser=True,
                    is_staff=True,
                )
                return render(request,"adminapp/admin-add-form.html",{'new_add_msg':"New Admin Created"})
        else:
            return render(request,"adminapp/admin-add-form.html",{'error':"Password Doesn't Match"})
    return render(request,"adminapp/admin-add-form.html")


def dev_list_table(request):
    dev_details = User.objects.filter(role="Developer")
    context = {'dev_details':dev_details}
    return render(request,"adminapp/dev-table.html",context=context)


def authorize_dev(request,id):
    data = User.objects.get(id=id)
    if request.method == "POST":
        data.is_verified = True
        data.save()
        return redirect(dev_list_table)
    return render(request,"adminapp/dev-table.html")

def unauthorize_dev(request,id):
    data = User.objects.get(id=id)
    if request.method == "POST":
        data.is_verified = False
        data.save()
        return redirect(dev_list_table)
    return render(request,"adminapp/dev-table.html")

def deleteDev(request,id):
    data = User.objects.get(id=id)
    data.delete()
    return redirect(dev_list_table)

def quiz_category_list_table(request):
    quiz_data = devModels.QuizCategory.objects.all()
    context = {'quiz_data':quiz_data}
    return render(request,"adminapp/quiz-category-list-table.html",context=context)