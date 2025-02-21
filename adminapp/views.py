from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from devapp import models as devModels
from devapp import forms
from studentapp.models import User,Quiz_attempt
from TheCareerLinker import views as TCL_views
from devapp import views as dev_views
from django.core.paginator import Paginator

# Create your views here.
def index(request):
    totalStudents = User.objects.filter(role="Student").count()
    totalDevelopers = User.objects.filter(role="Developer").count()
    totalQuiz = devModels.QuizCategory.objects.all().count()
    totalQuizAttempts = Quiz_attempt.objects.all().count()
    context = {
        'totalStudents':totalStudents,
        'totalDevelopers':totalDevelopers,
        'totalQuiz':totalQuiz,
        'totalQuizAttempts':totalQuizAttempts
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

def delete_quiz_category(request,id):
    data = devModels.QuizCategory.objects.get(id=id)
    if request.user.role == "Admin":
        data.delete()
        return redirect(quiz_category_list_table)
    elif request.user.role == "Developer":
        data.delete()
        return redirect(dev_views.table)


# def quiz_attempt_table(request):
#     data = Quiz_attempt.objects.all()
#     findTotalQuestions = devModels.QuizQuestions.objects.filter(quiz_category_id=data.quiz_category).count()
#     print("--------------------------->",findTotalQuestions)
#     context = {
#         'data':data
#     }
#     return render(request,"adminapp/quiz-attempts-table.html",context=context)

def quiz_attempt_table(request):
    data = Quiz_attempt.objects.all()
    total_questions_per_category = {}
    for attempt in data:
        quiz_category_id = attempt.quiz_category.id
        total_questions = devModels.QuizQuestions.objects.filter(quiz_category_id=quiz_category_id).count()
        total_questions_per_category[quiz_category_id] = total_questions
    print("--------------------------->", total_questions_per_category)
    paginator = Paginator(data, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        # 'data': data,
        'data': page_obj,
        'total_questions_per_category': total_questions_per_category 
    }
    return render(request, "adminapp/quiz-attempts-table.html", context=context)


def delete_quiz_attempt(request,id):
    quiz_attempt_data = Quiz_attempt.objects.get(id=id)
    quiz_attempt_data.delete()
    return redirect(quiz_attempt_table)