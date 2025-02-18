from django.shortcuts import render,HttpResponse,redirect
from studentapp import forms
from devapp import models as devModels
from django.core.mail import send_mail
from django.conf import settings
from studentapp.models import User,Quiz_attempt
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.hashers import make_password
from devapp import views as dev_views
from adminapp import views as admin_views
import math,random
from TheCareerLinker import views as TCL_views

# Create your views here.
# index page 
def home(request):
    return render(request,'studentapp/index.html')

# about page
def about(request):
    return render(request,'studentapp/about.html')

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

# student profile page
def profile(request):
    username = request.user
    data = User.objects.get(username=username)
    context = {
        'userdata':data
    }
    return render(request,'studentapp/profile.html',context=context)

# student registration page
def registration(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirmPassword = request.POST.get('confirmPassword')
        contact = request.POST.get('contact')
        address = request.POST.get('address')
        institute_name = request.POST.get('institute_name')
        last_sem_marksheet = request.FILES.get('last_sem_marksheet')
        student_resume = request.FILES.get('student_resume')
        course = request.POST.get('course')
        try:
            User.objects.get(email=email)
            return HttpResponse("Email is already existed")
        except:
            if password == confirmPassword:
                User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    contact=contact,
                    address=address,
                    institute_name=institute_name,
                    last_sem_marksheet=last_sem_marksheet,
                    student_resume=student_resume,
                    course=course,
                    role=User.STUDENT
                )
                return redirect(loginview)
            else:
                return render(request,"studentapp/registration.html",{'error':"Password Doesn't Match"})
    return render(request,'studentapp/registration.html')

# login
def loginview(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request,username=username,password=password)
        if user is not None and user.role == "Student":
            login(request,user)
            return redirect(home)
        elif user is not None and user.role == "Developer":
            if user.is_verified == True:
                login(request,user)
                return redirect(dev_views.index)
            else:
                print("developer is not authorized")
                return render(request,'studentapp/login.html',{'error':"Wait until you are authorize"})
        elif user is not None and user.role == "Admin":
            login(request,user)
            return redirect(admin_views.index)
        else:
            return render(request,'studentapp/login.html',{'error':"User doesn't exist"})
    return render(request,'studentapp/login.html')

# logout
def signout(request):
    logout(request)
    return redirect(TCL_views.main_login)

# forgot password
def forgot_password(request):
    if request.method == "POST":
        user_email = request.POST.get('email')
        try:
            check_user_exist = User.objects.get(email=user_email)
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
            try:
                check_user_exist = User.objects.get(email=user_email)
                check_user_exist.set_password(new_pass)
                check_user_exist.save()
                request.session.flush()
                return redirect(loginview)
            except:
                return render(request,"studentapp/reset-password.html",{'error':"User Not Found"})
        else:
            return render(request,"studentapp/reset-password.html",{'error':"Password doesn't match"})
    return render(request,"studentapp/reset-password.html")


def quiz_list(request):
    quiz_data_list = devModels.QuizCategory.objects.all()
    context = {
        'data':quiz_data_list
    }
    return render(request,"studentapp/quiz-list.html",context=context)


def quiz(request, id):
    quiz_questions = devModels.QuizQuestions.objects.filter(quiz_category_id=id)
    quiz_questions_options = devModels.QuizOptions.objects.all()

    context = {
        'data': quiz_questions,
        'options': quiz_questions_options
    }

    if request.method == "POST":
        score = 0  # Initialize score
        total_questions = quiz_questions.count()

        for question in quiz_questions:
            user_choice = request.POST.get(f"user_choice_{question.id}")  # Get user answer
            try:
                quiz_answer = devModels.QuizOptions.objects.get(question_id=question.id)
                
                # Assuming option_1 is the correct answer (modify if needed)
                correct_answer = quiz_answer.option_1

                if user_choice == correct_answer:
                    score += 1  # Increase score for correct answers
                    
            except devModels.QuizOptions.DoesNotExist:
                continue  # Skip if the question has no options
        
        quiz_category = devModels.QuizCategory.objects.get(id=id)

        quiz_attempt_form = forms.QuizAttemptForm(request.POST)
        if quiz_attempt_form.is_valid():
            quiz_attempt_obj = quiz_attempt_form.save(commit=False)
            quiz_attempt_obj.student_id = request.user
            quiz_attempt_obj.quiz_category = quiz_category
            quiz_attempt_obj.score = score
            quiz_attempt_obj.save()
            return redirect(score_card)
        else:
            print(quiz_attempt_form.errors)

        # Pass the score to the template
        context["score"] = score
        context["total_questions"] = total_questions

    return render(request, "studentapp/quiz.html", context=context)


def score_card(request):
    data = Quiz_attempt.objects.get(student_id=request.user)
    findQuizCatName = devModels.QuizCategory.objects.get(id=data.quiz_category.id)
    totalQuestions = devModels.QuizQuestions.objects.filter(quiz_category_id=findQuizCatName).count()
    print(totalQuestions)
    context = {
        'data':data,
        'quiz_category':findQuizCatName,
        'totalQuestions':totalQuestions
    }
    return render(request,"studentapp/score-card.html",context=context)


# def quiz(request,id):
#     quiz_questions = devModels.QuizQuestions.objects.filter(quiz_category_id=id)
#     quiz_questions_options = devModels.QuizOptions.objects.all()
#     context = {
#         'data':quiz_questions,
#         'options':quiz_questions_options
#     }

#     if request.method == "POST":
#         user_choice = request.POST.get('user_choice')
#         question_id = request.POST.get('question_id')
#         print("user_choice==================================>",user_choice)
#         print("question_id==================================>",question_id)
#         quiz_answer = devModels.QuizOptions.objects.get(question_id=question_id)
#         print("================quiz_answer==================>",quiz_answer)
#         if user_choice == quiz_answer.option_1:
#             print("score increase by 1")
#             return render(request,"studentapp/quiz.html",context=context)
#         else:
#             print("incorrect answer")
#             return render(request,"studentapp/quiz.html",context=context)
#     return render(request,"studentapp/quiz.html",context=context)


