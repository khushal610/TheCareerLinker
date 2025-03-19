from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from devapp import models as devModels
from devapp import forms
from studentapp.models import User,Quiz_attempt,Attempted_session,Contact_us,Course_Enrollment,Feedback
from TheCareerLinker import views as TCL_views
from devapp import views as dev_views
from django.core.paginator import Paginator
from django.db.models import Q

# Create your views here.
def index(request):
    totalStudents = User.objects.filter(role="Student").count()
    totalDevelopers = User.objects.filter(role="Developer").count()
    totalQuiz = devModels.QuizCategory.objects.all().count()
    totalOnlineClasses = devModels.Online_sessions.objects.all().count()
    totalContactDetails = Contact_us.objects.all().count()
    totalShortlistedStudentData = User.objects.filter(role="Student").count()
    totalCourseEnrollmentData = Course_Enrollment.objects.all().count()
    totalFeedbacks = Feedback.objects.all().count()
    context = {
        'totalStudents':totalStudents,
        'totalDevelopers':totalDevelopers,
        'totalQuiz':totalQuiz,
        'totalOnlineClasses':totalOnlineClasses,
        'totalContactDetails':totalContactDetails,
        'totalShortlistedStudentData':totalShortlistedStudentData,
        'totalCourseEnrollmentData':totalCourseEnrollmentData,
        'totalFeedbacks':totalFeedbacks
    }
    return render(request,'adminapp/index.html',context=context)

def signout(request):
    logout(request)
    return redirect(TCL_views.main_login)

def formview(request):
    return render(request,'adminapp/form.html')

def studentTable(request):
    query = request.GET.get('search', '')
    students = User.objects.filter(role="Student", is_superuser=False)
    if query:
        students = students.filter(
            Q(username__icontains=query) | Q(course__icontains=query) | Q(institute_name__icontains=query)
        )
    paginator = Paginator(students, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'students': page_obj,
        'search_query': query
    }
    return render(request, 'adminapp/student-table.html', context)

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
    query = request.GET.get('search', '')
    dev_details = User.objects.filter(role="Developer")
    if query:
        dev_details = dev_details.filter(
            Q(username__icontains=query) | Q(company_name__icontains=query)
        )
    paginator = Paginator(dev_details, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'dev_details': page_obj,
        'search_query': query
    }
    return render(request, "adminapp/dev-table.html", context)


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

def quiz_attempt_table(request,id):
    data = Quiz_attempt.objects.filter(quiz_category=id)
    quiz_data = devModels.QuizCategory.objects.get(id=id)
    total_questions = devModels.QuizQuestions.objects.filter(quiz_category_id=id).count()
    paginator = Paginator(data, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'data': page_obj,
        'quiz_data':quiz_data,
        'total_questions':total_questions,
    }
    return render(request, "adminapp/quiz-attempts-table.html", context=context)


def delete_quiz_attempt(request,id):
    quiz_attempt_data = Quiz_attempt.objects.get(id=id)
    if request.user.role == "Admin":
        quiz_attempt_data.delete()
        return redirect(quiz_category_list_table)
    if request.user.role == "Developer":
        quiz_attempt_data.delete()
        return redirect(dev_views.quiz_category_table)


def manage_online_session_table(request):
    session_data = devModels.Online_sessions.objects.all()
    paginator = Paginator(session_data, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'session_data':page_obj
    }
    return render(request,"adminapp/manage-online-session-table.html",context=context)

def session_attempted_student(request,id):
    session_attempted_data = Attempted_session.objects.filter(session_id=id)
    session_data = devModels.Online_sessions.objects.get(id=id)
    session_name = session_data.topic_name
    context = {
        'session_data':session_attempted_data,
        'session_name':session_name
    }
    return render(request,"adminapp/session-attempted-student.html",context=context)


def shortlisted_student_detail(request):
    query = request.GET.get('search', '')
    shortlisted_student_data = User.objects.filter(role="Student")
    if query:
        shortlisted_student_data = shortlisted_student_data.filter(
            Q(username__icontains=query) | Q(company_name__icontains=query) | Q(institute_name__icontains=query) | Q(course__icontains=query)
        )
    paginator = Paginator(shortlisted_student_data, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'shortlisted_student_data': page_obj,
        'search_query': query
    }
    return render(request, "adminapp/shortlisted-student-detail.html", context)


def contact_details(request):
    contact_details_data = Contact_us.objects.all()
    paginator = Paginator(contact_details_data, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'contact_details_data':page_obj,
    }
    return render(request,"adminapp/contact-details.html",context=context)

def delete_contact_details(request,id):
    contact_data = Contact_us.objects.get(id=id)
    contact_data.delete()
    return redirect(contact_details)


def course_enrollment_data(request):
    query = request.GET.get('search', '')
    data = Course_Enrollment.objects.all()
    if query:
        data = data.filter(
            Q(student_id__username__icontains=query) | 
            Q(course_id__course_name__icontains=query) | 
            Q(course_id__course_type__icontains=query)
        )
    paginator = Paginator(data, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'course_enrollment_data': page_obj,
        'search_query': query
    }
    return render(request, "adminapp/course-enrollment-data.html", context)


def feedback_table(request):
    feedback_data = Feedback.objects.all()
    paginator = Paginator(feedback_data, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'feedback_data':page_obj
    }
    return render(request,"adminapp/feedback-table.html",context=context)

def delete_feedback(request,id):
    feedback_data = Feedback.objects.get(id=id)
    feedback_data.delete()
    return redirect(feedback_table)