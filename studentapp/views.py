from django.shortcuts import render,HttpResponse,redirect
from studentapp import forms
from devapp import models as devModels
from django.core.mail import send_mail
from django.conf import settings
from studentapp.models import User,Quiz_attempt
from studentapp import models as studentModels
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.hashers import make_password
from devapp import views as dev_views
from adminapp import views as admin_views
import math,random,string
from TheCareerLinker import views as TCL_views
from django.core.paginator import Paginator
import datetime
from django.utils import timezone
from django.urls import reverse
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.http import HttpResponse,JsonResponse
from django.template.loader import render_to_string
from weasyprint import HTML
import tempfile
import os
import razorpay
from django.views.decorators.csrf import csrf_exempt
import json
from django.db.models import Q
from django.db.models import Avg


def home(request):
    course_data = devModels.Online_Certification_Course.objects.all()
    user_data = request.user
    context = {
        'course_data': course_data
    }
    if not user_data.is_authenticated:
        return render(request,'studentapp/index.html',context=context)

    if user_data.role == "Student":
        return render(request,'studentapp/index.html',context=context)
    elif user_data.role == "Developer":
        return redirect(dev_views.index)
    elif user_data.role == "Admin":
        return redirect(admin_views.index)
    return render(request,'studentapp/index.html',context=context)
    

def about(request):
    feedback_data = studentModels.Feedback.objects.all()
    context = {
        'feedback_data':feedback_data,
    }
    return render(request,'studentapp/about.html',context=context)

def chat(request):
    return render(request,'studentapp/chat.html')

def contact(request):
    user_data = request.user
    if not user_data.is_authenticated:
        return redirect('login')
    if request.method == "POST":
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        contact_us_data = studentModels.Contact_us.objects.create(
            user_id=request.user,
            subject=subject,
            message=message
        )
        contact_us_data.save()
        print("-------------------------------------------data saved to contact us page")
        return render(request,'studentapp/contact.html',{'alert':"Your data send successfully"})
    return render(request,'studentapp/contact.html')



def courses(request):
    user_data = request.user
    if not user_data.is_authenticated:
        return redirect('login')
    search_query = request.GET.get('search', '').strip()
    course_type_filter = request.GET.get('course_type', '')
    course_data = devModels.Online_Certification_Course.objects.filter(is_launched=True)
    if search_query:
        course_data = course_data.filter(course_name__icontains=search_query)
    if course_type_filter and course_type_filter != "None":
        course_data = course_data.filter(course_type=course_type_filter)
        
    course_enrollment_data = studentModels.Course_Enrollment.objects.filter(student_id=request.user)
    paginator = Paginator(course_data, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    paginator1 = Paginator(course_enrollment_data, 3)
    page_number1 = request.GET.get('page_enrolled')
    page_obj1 = paginator1.get_page(page_number1)

    quiz_attempted_data = {}
    for enrolled_course in course_enrollment_data:
        course_id = enrolled_course.course_id.id 
        course_module_data = devModels.Module_list.objects.filter(course_id=course_id)
        for module in course_module_data:
            module_stage_data = devModels.Module_Stage.objects.filter(module_id=module.id)
            for stage in module_stage_data:
                course_module_content_data = devModels.Course_Module_Content.objects.filter(stage_id=stage.id)
                for content in course_module_content_data:
                    if content.course_quiz: 
                        course_quiz = content.course_quiz
                        quiz_attempts = Quiz_attempt.objects.filter(student_id=request.user, quiz_category=course_quiz) 
                        if quiz_attempts.exists():
                            totalQuestions = devModels.QuizQuestions.objects.filter(quiz_category_id=course_quiz.id).count()
                            
                            if totalQuestions > 0:
                                avg_score = quiz_attempts.aggregate(Avg("score"))["score__avg"] or 0
                                avg_percentage = int((avg_score / totalQuestions) * 100)
                            else:
                                avg_percentage = 0

                            quiz_attempted_data[course_id] = {
                                "quiz_category": course_quiz,
                                "avg_percentage": avg_percentage,
                                "date_time": quiz_attempts.order_by('-date_time').first().date_time
                            }

    final_score_sum = sum(quiz["avg_percentage"] for quiz in quiz_attempted_data.values())
    total_quizzes = len(quiz_attempted_data)
    final_avg_score = int(final_score_sum / total_quizzes) if total_quizzes > 0 else 0
    print('----------------------------------score =======================',final_avg_score)

    context = {
        'course_data': page_obj,
        'course_enrollment_data': page_obj1,
        'search_query': search_query,
        'selected_course_type': course_type_filter,
        'quiz_attempted_data': quiz_attempted_data,
        'final_avg_score': final_avg_score,
    }
    return render(request, 'studentapp/courses.html', context)




razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

@csrf_exempt
def course_details(request, id):
    course_details = get_object_or_404(devModels.Online_Certification_Course, id=id, is_launched=True)
    dev_id = course_details.dev_id
    course_module_data = devModels.Module_list.objects.filter(course_id=id, dev_id=dev_id)

    student_data = User.objects.get(username=request.user)

    module_stage_data_details = {}
    for module_data in course_module_data:
        module_id = module_data.id
        module_stage_data = list(devModels.Module_Stage.objects.filter(module_id=module_id, dev_id=dev_id))  
        if module_stage_data:
            module_stage_data_details[module_id] = module_stage_data

    # Check if user is enrolled
    enrollment = None
    razorpay_order_id = None

    if request.user.is_authenticated:
        enrollment, created = studentModels.Course_Enrollment.objects.get_or_create(
            student_id=request.user,
            course_id=course_details,
            defaults={"is_payment_received": False}
        )

        if course_details.course_type == "Paid":
            if enrollment.is_payment_received:
                razorpay_order_id = enrollment.razorpay_order_id
            else:
                if not enrollment.razorpay_order_id:
                    order_data = {
                        "amount": int(float(course_details.course_charges) * 100),
                        "currency": "INR",
                        "payment_capture": "1"
                    }
                    order = razorpay_client.order.create(order_data)
                    enrollment.razorpay_order_id = order["id"]
                    enrollment.save()

                razorpay_order_id = enrollment.razorpay_order_id

    if request.method == "POST":
        razorpay_payment_id = request.POST.get("razorpay_payment_id")
        razorpay_order_id = request.POST.get("razorpay_order_id")
        razorpay_signature = request.POST.get("razorpay_signature")

        if all([razorpay_payment_id, razorpay_order_id, razorpay_signature]):
            try:
                razorpay_client.utility.verify_payment_signature({
                    "razorpay_order_id": razorpay_order_id,
                    "razorpay_payment_id": razorpay_payment_id,
                    "razorpay_signature": razorpay_signature,
                })
                enrollment.razorpay_payment_id = razorpay_payment_id
                enrollment.razorpay_signature = razorpay_signature
                enrollment.is_payment_received = True
                enrollment.save()
                payment_confirmation_email_to_student(course_details.course_name,course_details.course_charges,razorpay_payment_id,student_data.username,student_data.email)
                return redirect(reverse('course_details', args=[id]))
            except razorpay.errors.SignatureVerificationError:
                return JsonResponse({"status": "error", "message": "Invalid payment signature"})
        else:
            return JsonResponse({"status": "error", "message": "Missing required parameters"})

    context = {
        "course_details": course_details,
        "course_module_data": course_module_data,
        "module_stage_data": module_stage_data_details,
        "enrollment": enrollment,
        "razorpay_order_id": razorpay_order_id,
        "RAZORPAY_KEY_ID": settings.RAZORPAY_KEY_ID,
    }

    return render(request, "studentapp/course-details.html", context)


def payment_confirmation_email_to_student(course_name, course_charges, transaction_id, username, email):
    subject = f"Payment Confirmation – {course_name}"
    
    message = f"""
    <p>Dear {username},</p>
    
    <p>Thank you for your purchase! We are pleased to confirm that your payment for the course <strong>"{course_name}"</strong> has been successfully processed.</p>

    <h3>Order Summary:</h3>
    <ul>
        <li><strong>Course Name:</strong> {course_name}</li>
        <li><strong>Transaction ID:</strong> {transaction_id}</li>
        <li><strong>Amount Paid:</strong> {course_charges}</li>
        <li><strong>Payment Date:</strong> {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</li>
    </ul>

    <p>You now have full access to the course materials.</p>

    <p>If you have any questions or require assistance, feel free to reach out to us at <strong>The Career Linker</strong>.</p>

    <p>Thank you for choosing <strong>The Career Linker</strong>. We look forward to supporting you on your learning journey!</p>

    <p>Best regards,<br>
    <strong>The Career Linker Team</strong></p>
    """

    from_email = settings.EMAIL_HOST_USER
    to_email = [email]

    send_mail(subject, '', from_email, to_email, html_message=message)


def course_enrollment(request, id):
    course_data = devModels.Online_Certification_Course.objects.get(id=id)
    dev_id = course_data.dev_id
    course_module_data = devModels.Module_list.objects.filter(course_id=id, dev_id=dev_id)
    course_progress_tracker_data = studentModels.Course_Progress_Tracker.objects.filter(student_id=request.user,course_id=id)

    module_stage_data_details = {}
    module_content_data_details = {}

    for module_data in course_module_data:
        module_id = module_data.id
        module_stage_data = list(devModels.Module_Stage.objects.filter(module_id=module_id, dev_id=dev_id))
        if module_stage_data:
            module_stage_data_details[module_id] = module_stage_data

            for stage in module_stage_data:
                stage_id = stage.id
                course_module_content_data = list(devModels.Course_Module_Content.objects.filter(stage_id=stage_id,dev_id=dev_id))
                if course_module_content_data:
                    module_content_data_details[stage_id] = course_module_content_data
                print("------content_data---------------------------------------->\n",course_module_content_data)
                print("===module_content_data_details=====================>\n",module_content_data_details)
                print("===stage_id=====================>\n",module_content_data_details.keys())
                print("===content_data=====================>\n",module_content_data_details.values())
                print("===items()=====================>\n",module_content_data_details.items())

    context = {
        'course_data': course_data,
        'course_module_data': course_module_data,
        'module_stage_data': module_stage_data_details,
        'module_content_data': module_content_data_details,
        'course_progress_tracker_data': course_progress_tracker_data,
    }
    if studentModels.Course_Enrollment.objects.filter(student_id=request.user,course_id=id).exists():
        return render(request, "studentapp/course-enrollments.html",context=context)
    studentModels.Course_Enrollment.objects.create(
        student_id=request.user,
        course_id=course_data,
        is_payment_received=False
    )
    return render(request, "studentapp/course-enrollments.html", context=context)


def trainers(request):
    return render(request,'studentapp/trainers.html')

def pricing(request):
    return render(request,'studentapp/pricing.html')

def profile(request):
    user_data = request.user
    if not user_data.is_authenticated:
        return redirect('login')
    username = request.user
    data = User.objects.get(username=username)
    quiz_attempted_data = Quiz_attempt.objects.filter(student_id=request.user)
    enrolled_course_details = studentModels.Course_Enrollment.objects.filter(student_id=request.user)
    print("----------------------------------------->",enrolled_course_details)
    total_questions_as_quiz_category = {}
    for quiz_questions in quiz_attempted_data:
        quiz_category_id = quiz_questions.quiz_category.id
        total_questions = devModels.QuizQuestions.objects.filter(quiz_category_id=quiz_category_id).count()
        total_questions_as_quiz_category[quiz_category_id] = total_questions
    print("----------------------->",total_questions_as_quiz_category)
    context = {
        'userdata':data,
        'quiz_attempted_data':quiz_attempted_data,
        'total_questions':total_questions_as_quiz_category,
        'enrolled_course_details':enrolled_course_details
    }
    return render(request,'studentapp/profile.html',context=context)

def registration(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
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
        student_img = request.FILES.get('student_img')
        try:
            User.objects.get(email=email)
            return HttpResponse("Email is already existed")
        except:
            if password == confirmPassword:
                User.objects.create_user(
                    first_name=first_name,
                    last_name=last_name,
                    username=username,
                    email=email,
                    password=password,
                    contact=contact,
                    address=address,
                    institute_name=institute_name,
                    last_sem_marksheet=last_sem_marksheet,
                    student_resume=student_resume,
                    course=course,
                    student_img=student_img,
                    role=User.STUDENT
                )
                send_email_after_registration(username,email)
                return redirect(loginview)
            else:
                return render(request,"studentapp/registration.html",{'error':"Password Doesn't Match"})
    return render(request,'studentapp/registration.html')

def send_email_after_registration(username,email):
    subject = "Welcome to TCL – Your Journey to Success Begins!"
    message = f"""
    <p>Dear {username},
        <br><br>
        Congratulations! 🎉 You have successfully registered on The Career Linker (TCL) platform. We are excited to have you on board and look forward to helping you enhance your skills and career prospects.
        <br><br>
        At TCL, you can:<br>
        ✅ Attempt quizzes to test and improve your knowledge.<br>
        ✅ Join online sessions conducted by industry experts.<br>
        ✅ Access various resources to develop your skills and stay ahead in your career.<br>
        <br>
        Start exploring the platform today and make the most of the opportunities available to you! 🚀
        <br><br>
        If you have any questions or need assistance, feel free to reach out to us.
        <br><br>
        Best Regards,<br>
        The Career Linker Team<p>
    """
    from_email = settings.EMAIL_HOST_USER
    to_email = email
    send_mail(subject, '', from_email, [to_email],html_message=message)

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

def signout(request):
    logout(request)
    return redirect(TCL_views.main_login)

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

def send_otp_email(user_email):
    OTP = generate_otp()
    subject = "Reset Password"
    message = f"To reset your password your OTP is : {OTP}"
    from_email = settings.EMAIL_HOST_USER
    to_email = user_email
    print("send_otp_email : method ---------------------->",OTP)
    send_mail(subject, message, from_email, [to_email])
    return OTP

def generate_otp():
    numbers = "0123456789"
    OTP = ""
    for i in range(6):
        OTP += numbers[math.floor(random.random() * 10)]
    return OTP

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
    search_query = request.GET.get('search', '')
    quiz_level = request.GET.get('quiz_level', '')
    quiz_data_list = devModels.QuizCategory.objects.filter(is_approved=True, is_course_quiz=False)

    if search_query:
        quiz_data_list = quiz_data_list.filter(quiz_category_name__icontains=search_query)
    if quiz_level and quiz_level != "None":
        quiz_data_list = quiz_data_list.filter(quiz_level=quiz_level)
    paginator = Paginator(quiz_data_list, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    developer_data = User.objects.all()
    context = {
        'data': page_obj,
        'developer_data': developer_data,
        'search_query': search_query,
        'selected_level': quiz_level,
    }
    return render(request, "studentapp/quiz-list.html", context)



def quiz(request, id):
    user_data = request.user
    if not user_data.is_authenticated:
        return redirect('login')
    quiz_category_data = devModels.QuizCategory.objects.get(id=id)
    quiz_questions = list(devModels.QuizQuestions.objects.filter(quiz_category_id=id))
    random.shuffle(quiz_questions)

    quiz_questions_options = []

    for question in quiz_questions:
        try:
            option_obj = devModels.QuizOptions.objects.get(question_id=question.id)
            options = [
                option_obj.option_1,
                option_obj.option_2,
                option_obj.option_3,
                option_obj.option_4
            ]
            options = [opt for opt in options if opt] 
            random.shuffle(options)  
        except option_obj.ObjectDoesNotExist:
            options = []

        quiz_questions_options.append({
            "question": question,
            "options": options
        })

    context = {
        'quiz_questions_options': quiz_questions_options
    }

    if request.method == "POST":
        score = 0
        total_questions = len(quiz_questions)

        for question in quiz_questions:
            user_choice = request.POST.get(f"user_choice_{question.id}")
            try:
                quiz_answer = devModels.QuizOptions.objects.get(question_id=question.id)
                correct_answer = quiz_answer.option_1 
                if user_choice == correct_answer:
                    score += 1
            except quiz_answer.ObjectDoesNotExist:
                continue

        if total_questions > 0:
            average_score = int((score / total_questions) * 100)
        else:
            average_score = 0

        print("--------------- Score ------------------", score)
        print("Average Score:", average_score)

        if quiz_category_data.is_course_quiz:
            course_progress_tracker_data, created = studentModels.Course_Progress_Tracker.objects.get_or_create(
                student_id=request.user, quiz_id=quiz_category_data
            )
            course_progress_tracker_data.is_completed = True
            course_progress_tracker_data.save()

        quiz_attempt_form = forms.QuizAttemptForm(request.POST)
        if quiz_attempt_form.is_valid():
            quiz_attempt_obj = quiz_attempt_form.save(commit=False)
            quiz_attempt_obj.student_id = request.user
            quiz_attempt_obj.quiz_category = quiz_category_data
            quiz_attempt_obj.score = score
            quiz_attempt_obj.save()

            if not quiz_category_data.is_course_quiz:
                send_quiz_score_to_email(request.user, id, score, total_questions)

            return redirect("score_card")
        else:
            print(quiz_attempt_form.errors)

        context["score"] = score
        context["total_questions"] = total_questions
        context["average_score"] = average_score

    return render(request, "studentapp/quiz.html", context)



def send_quiz_score_to_email(username,id,score,total_questions):
    user_email = User.objects.get(username=username)
    quiz_name = devModels.QuizCategory.objects.get(id=id)
    subject = f"Your {quiz_name.quiz_category_name} Assessment Results"
    message = f"""
    Dear {user_email.username},
    <p>I hope this message finds you well.

    <h3>We are pleased to inform you that you have recently completed the {quiz_name.quiz_category_name} assessment on The Career Linker platform. Your score for the assessment is {score} / {total_questions}. Congratulations on your progress!</h3>

    If you have any questions or would like to review your answers, please feel free to log in to your account at your convenience.
    <br><br>
    Thank you for your continued efforts, and we look forward to supporting you in your career development.
    <br><br>
    Best regards,<br>
    The Career Linker Team</p>
    """
    from_email = settings.EMAIL_HOST_USER
    to_email = user_email.email
    send_mail(subject, '', from_email, [to_email],html_message=message)


def score_card(request):
    try:
        data = studentModels.Quiz_attempt.objects.filter(student_id=request.user).latest('date_time')
    except studentModels.Quiz_attempt.DoesNotExist:
        return render(request, "studentapp/score-card.html", {"error": "No quiz attempt found."})
    findQuizCatName = devModels.QuizCategory.objects.get(id=data.quiz_category.id)
    totalQuestions = devModels.QuizQuestions.objects.filter(quiz_category_id=findQuizCatName).count()
    if totalQuestions > 0:
        average = int((data.score / totalQuestions) * 100)
    else:
        average = 0
    print("Average Score:", average)
    print("Total Questions:", totalQuestions)
    context = {
        'data': data,
        'id':data.quiz_category,
        'quiz_category': findQuizCatName,
        'totalQuestions': totalQuestions,
        'average': average
    }
    return render(request, "studentapp/score-card.html", context=context)



def live_sessions(request):
    user_data = request.user
    if not user_data.is_authenticated:
        return redirect('login')
    session_data = devModels.Online_sessions.objects.all()
    company_filter = request.GET.get('company_filter')

    if company_filter and company_filter != 'all':
        session_data = session_data.filter(dev_name__company_name=company_filter)
    current_user = request.user
    bookmarked_sessions = studentModels.Bookmarked_session.objects.filter(student_id=current_user, is_bookmarked=True).values_list('session_id', flat=True)
    bookmarked_sessions_data = devModels.Online_sessions.objects.filter(id__in=bookmarked_sessions)
    company_data = User.objects.filter(role="Developer")

    paginator = Paginator(session_data, 2)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    paginator1 = Paginator(bookmarked_sessions_data, 1)
    page_number1 = request.GET.get('page')
    page_obj1 = paginator1.get_page(page_number1)

    context = {
        'session_data': page_obj,
        'bookmarked_sessions_data': page_obj1,
        'company_data': company_data,
        'selected_company': company_filter,
    }
    
    return render(request, "studentapp/live-sessions.html", context)


def join_session(request, id):
    session = devModels.Online_sessions.objects.get(id=id)
    meeting_link = session.meeting_link
    attempted_session_data = studentModels.Attempted_session.objects.filter(
        session_id=id, 
        student_name=request.user,
        is_attempted=True
    ).first()
    if attempted_session_data:
        if attempted_session_data.is_attempted:
            attempted_session_data.date_time = datetime.datetime.now()
            attempted_session_data.save()
    else:
        new_attempted_session_data = studentModels.Attempted_session.objects.create(
            session_id=session,
            student_name=request.user,
            is_attempted=True,
            date_time=datetime.datetime.now()
        )
        new_attempted_session_data.save()
    return redirect(meeting_link)

def bookmark_session(request, id):
    session_data = devModels.Online_sessions.objects.get(id=id)
    print("-------------------->", session_data)

    existing_bookmark = studentModels.Bookmarked_session.objects.filter(
        session_id=session_data, student_id=request.user
    ).first()

    if existing_bookmark:
        existing_bookmark.is_bookmarked = not existing_bookmark.is_bookmarked
        existing_bookmark.save()
    else:
        add_new_bookmark = studentModels.Bookmarked_session.objects.create(
            session_id=session_data,
            student_id=request.user,
            is_bookmarked=True
        )
        add_new_bookmark.save()
    return redirect(live_sessions)



def course_document_content(request, course_data_id, id):
    course_data = get_object_or_404(devModels.Online_Certification_Course, id=course_data_id)
    dev_id = course_data.dev_id
    course_module_data = devModels.Module_list.objects.filter(course_id=course_data_id, dev_id=dev_id)

    module_stage_data_details = {}
    module_content_data_details = {}
    course_quiz_id = None
    quiz_questions = []
    quiz_questions_options = []

    for module_data in course_module_data:
        module_id = module_data.id
        module_stage_data = list(devModels.Module_Stage.objects.filter(module_id=module_id, dev_id=dev_id))
        if module_stage_data:
            module_stage_data_details[module_id] = module_stage_data

            for stage in module_stage_data:
                stage_id = stage.id
                course_module_content_data = list(devModels.Course_Module_Content.objects.filter(stage_id=stage_id, dev_id=dev_id))
                if course_module_content_data:
                    module_content_data_details[stage_id] = course_module_content_data

                    for content in course_module_content_data:
                        if hasattr(content, 'course_quiz_id'):
                            course_quiz_id = content.course_quiz_id
                            quiz_questions = list(devModels.QuizQuestions.objects.filter(quiz_category_id=course_quiz_id))
                            random.shuffle(quiz_questions)

                            for question in quiz_questions:
                                try:
                                    option_obj = devModels.QuizOptions.objects.get(question_id=question.id)
                                    options = [
                                        option_obj.option_1,
                                        option_obj.option_2,
                                        option_obj.option_3,
                                        option_obj.option_4
                                    ]
                                    options = [opt for opt in options if opt] 
                                    random.shuffle(options) 
                                except devModels.QuizOptions.DoesNotExist:
                                    options = []

                                quiz_questions_options.append({
                                    "question": question,
                                    "options": options
                                })
                            break 

    course_document_content_data = get_object_or_404(devModels.Course_Module_Content, id=id)

    if request.method == "POST":
        score = 0
        total_questions = len(quiz_questions)

        for question in quiz_questions:
            user_choice = request.POST.get(f"user_choice_{question.id}")
            try:
                quiz_answer = devModels.QuizOptions.objects.get(question_id=question.id)
                correct_answer = quiz_answer.option_1  
                if user_choice == correct_answer:
                    score += 1
            except devModels.QuizOptions.DoesNotExist:
                continue

        if course_quiz_id:
            quiz_category = get_object_or_404(devModels.QuizCategory, id=course_quiz_id)
            quiz_attempt, created = Quiz_attempt.objects.update_or_create(
                student_id=request.user,
                quiz_category=quiz_category,
                defaults={"score": score, "date_time": timezone.now()}
            )

            if quiz_category.is_course_quiz:
                progress_tracker, _ = studentModels.Course_Progress_Tracker.objects.get_or_create(
                    student_id=request.user, quiz_id=quiz_category
                )
                progress_tracker.is_completed = True
                progress_tracker.save()

            enrolled_course_data = studentModels.Course_Enrollment.objects.get(student_id=request.user, course_id=course_data)
            enrolled_course_data.is_course_completed = True
            enrolled_course_data.save()

            return redirect(reverse('course_final_assessment_result', args=[course_data_id, id]))

    context = {
        "course_document_content_data": course_document_content_data,
        "course_data": course_data,
        "course_data_id": course_data.id,
        "course_module_data": course_module_data,
        "module_stage_data": module_stage_data_details,
        "module_content_data": module_content_data_details,
        "quiz_questions_options": quiz_questions_options, 
    }

    return render(request, "studentapp/course-document-content.html", context)



def course_final_assessment_result(request, course_data_id, id):
    course_data = devModels.Online_Certification_Course.objects.get(id=course_data_id)
    dev_id = course_data.dev_id
    course_module_data = devModels.Module_list.objects.filter(course_id=course_data_id, dev_id=dev_id)
    module_stage_data_details = {}
    module_content_data_details = {}
    course_quiz_id = None
    quiz_questions = []
    quiz_options = []
    document_quiz_id = None

    for module_data in course_module_data:
        module_id = module_data.id
        module_stage_data = list(devModels.Module_Stage.objects.filter(module_id=module_id, dev_id=dev_id))
        if module_stage_data:
            module_stage_data_details[module_id] = module_stage_data

            for stage in module_stage_data:
                stage_id = stage.id
                course_module_content_data = list(devModels.Course_Module_Content.objects.filter(stage_id=stage_id, dev_id=dev_id))
                if course_module_content_data:
                    module_content_data_details[stage_id] = course_module_content_data

                    for content in course_module_content_data:
                        if hasattr(content, 'course_quiz_id'):
                            course_quiz_id = content.course_quiz_id
                            quiz_questions = devModels.QuizQuestions.objects.filter(quiz_category_id=course_quiz_id)
                            quiz_options = devModels.QuizOptions.objects.all()
                            document = devModels.Course_Module_Content.objects.filter(course_quiz=course_quiz_id).first()
                            if document:
                                document_quiz_id = document.id 
                            break 

    course_document_content_data = devModels.Course_Module_Content.objects.get(id=id)
    try:
        data = studentModels.Quiz_attempt.objects.filter(student_id=request.user).latest('date_time')
    except studentModels.Quiz_attempt.DoesNotExist:
        return render(request, "studentapp/score-card.html", {"error": "No quiz attempt found."})

    findQuizCatName = devModels.QuizCategory.objects.get(id=data.quiz_category.id)
    totalQuestions = devModels.QuizQuestions.objects.filter(quiz_category_id=findQuizCatName).count()
    average = int((data.score / totalQuestions) * 100) if totalQuestions > 0 else 0

    print("Average Score:", average)
    print("Total Questions:", totalQuestions)
    context = {
        "course_document_content_data": course_document_content_data,
        'course_data': course_data,
        'course_data_id': course_data.id,
        'stage_data_id': stage_id,
        'course_module_data': course_module_data,
        'module_stage_data': module_stage_data_details,
        'module_content_data': module_content_data_details,
        'course_quiz_id': course_quiz_id, 
        'quiz_questions': quiz_questions,
        'quiz_options': quiz_options,
        'data': data,
        'quiz_category': findQuizCatName,
        'totalQuestions': totalQuestions,
        'average': average,
        'document_quiz_id': document_quiz_id,
    }
    return render(request, "studentapp/course-final-assessment-result.html", context=context)


def next_documentation(request, course_data_id, id):
    course_data = devModels.Online_Certification_Course.objects.get(id=course_data_id)
    dev_id = course_data.dev_id
    course_module_data = devModels.Module_list.objects.filter(course_id=course_data_id, dev_id=dev_id)
    
    module_stage_data_details = {}
    module_content_data_details = {}

    for module_data in course_module_data:
        module_id = module_data.id
        module_stage_data = list(devModels.Module_Stage.objects.filter(module_id=module_id, dev_id=dev_id))
        if module_stage_data:
            module_stage_data_details[module_id] = module_stage_data

            for stage in module_stage_data:
                stage_id = stage.id
                course_module_content_data = list(devModels.Course_Module_Content.objects.filter(stage_id=stage_id, dev_id=dev_id))
                if course_module_content_data:
                    module_content_data_details[stage_id] = course_module_content_data

    try:
        course_document_content_data = devModels.Course_Module_Content.objects.get(id=id)
    except devModels.Course_Module_Content.DoesNotExist:
        raise Http404("Content not found")

    stage_id = course_document_content_data.stage_id.id  

    last_stage = devModels.Module_Stage.objects.filter(
        module_id__in=course_module_data.values_list('id', flat=True), dev_id=dev_id
    ).order_by('-id').first()

    last_content = devModels.Course_Module_Content.objects.filter(
        stage_id=stage_id, dev_id=dev_id
    ).order_by('-id').first()

    is_last_content = (course_document_content_data.id == last_content.id) and (stage_id == last_stage.id)

    next_content = devModels.Course_Module_Content.objects.filter(
        stage_id=stage_id, dev_id=dev_id, id__gt=id
    ).order_by('id').first()

    if not next_content:
        next_stage = devModels.Module_Stage.objects.filter(
            module_id=course_module_data.first().id,
            dev_id=dev_id, id__gt=stage_id
        ).order_by('id').first()
        
        if next_stage:
            next_content = devModels.Course_Module_Content.objects.filter(
                stage_id=next_stage.id, dev_id=dev_id
            ).order_by('id').first()

    if next_content:
        id = next_content.id 
    else:
        return redirect(reverse('course_document_content', args=[course_data_id, id]))

    context = {
        "course_document_content_data": course_document_content_data,
        'course_data': course_data,
        'course_data_id': course_data.id,
        'stage_data_id': stage_id,
        'course_module_data': course_module_data,
        'module_stage_data': module_stage_data_details,
        'module_content_data': module_content_data_details,
        'is_last_content': is_last_content,
    }

    if studentModels.Course_Progress_Tracker.objects.filter(
        student_id=request.user, course_id=course_data_id, document_id=course_document_content_data
    ).exists():
        return redirect(reverse('course_document_content', args=[course_data_id, id]))

    studentModels.Course_Progress_Tracker.objects.create(
        student_id=request.user,
        course_id=course_data,
        document_id=course_document_content_data,
        is_completed=True
    )

    return redirect(reverse('course_document_content', args=[course_data_id, id]))


def previous_documentation(request, course_data_id, id):
    course_data = devModels.Online_Certification_Course.objects.get(id=course_data_id)
    dev_id = course_data.dev_id
    course_module_data = devModels.Module_list.objects.filter(course_id=course_data_id, dev_id=dev_id)

    module_stage_data_details = {}
    module_content_data_details = {}

    for module_data in course_module_data:
        module_id = module_data.id
        module_stage_data = list(devModels.Module_Stage.objects.filter(module_id=module_id, dev_id=dev_id))
        if module_stage_data:
            module_stage_data_details[module_id] = module_stage_data

            for stage in module_stage_data:
                stage_id = stage.id
                course_module_content_data = list(devModels.Course_Module_Content.objects.filter(stage_id=stage_id, dev_id=dev_id))
                if course_module_content_data:
                    module_content_data_details[stage_id] = course_module_content_data

    try:
        course_document_content_data = devModels.Course_Module_Content.objects.get(id=id)
    except devModels.Course_Module_Content.DoesNotExist:
        raise Http404("Content not found")

    stage_id = course_document_content_data.stage_id.id  

    first_content = devModels.Course_Module_Content.objects.filter(
        stage_id=stage_id, dev_id=dev_id
    ).order_by('id').first()

    is_first_content = (course_document_content_data.id == first_content.id)

    prev_content = devModels.Course_Module_Content.objects.filter(
        stage_id=stage_id, dev_id=dev_id, id__lt=id
    ).order_by('-id').first()

    if not prev_content:
        prev_stage = devModels.Module_Stage.objects.filter(
            module_id__in=course_module_data.values_list('id', flat=True), dev_id=dev_id, id__lt=stage_id
        ).order_by('-id').first()

        if prev_stage:
            prev_content = devModels.Course_Module_Content.objects.filter(
                stage_id=prev_stage.id, dev_id=dev_id
            ).order_by('-id').first()

    if prev_content:
        id = prev_content.id
    else:
        return redirect(reverse('course_document_content', args=[course_data_id, id]))

    context = {
        "course_document_content_data": course_document_content_data,
        'course_data': course_data,
        'course_data_id': course_data.id,
        'stage_data_id': stage_id,
        'course_module_data': course_module_data,
        'module_stage_data': module_stage_data_details,
        'module_content_data': module_content_data_details,
        'is_first_content': is_first_content,
    }
    
    if studentModels.Course_Progress_Tracker.objects.filter(
        student_id=request.user, course_id=course_data_id, document_id=course_document_content_data
    ).exists():
        return redirect(reverse('course_document_content', args=[course_data_id, id]))

    studentModels.Course_Progress_Tracker.objects.create(
        student_id=request.user,
        course_id=course_data,
        document_id=course_document_content_data,
        is_completed=True
    )

    return redirect(reverse('course_document_content', args=[course_data_id, id]))


def view_certificate(request, course_data_id):
    user_data = request.user
    if not user_data.is_authenticated:
        return redirect('login')
    try:
        course_data = devModels.Online_Certification_Course.objects.get(id=course_data_id)
    except devModels.Online_Certification_Course.DoesNotExist:
        return render(request, "studentapp/view-certificate.html", {"message": "Course not found"})
    try:
        certificate_details = devModels.Certificate_Details.objects.get(dev_id=course_data.dev_id)
    except devModels.Certificate_Details.DoesNotExist:
        return render(request, "studentapp/view-certificate.html", {"message": "Certificate details not found"})
    issued_certificate = devModels.Issued_Certificate.objects.filter(student_id=request.user, course_id=course_data).first()
    if issued_certificate:
        digital_signature = issued_certificate.digital_signature
    else:
        digital_signature = dev_views.generate_digital_signature(request.user, course_data_id, certificate_details.id)
    context = {
        "first_name": request.user.first_name,
        "last_name": request.user.last_name,
        "course": course_data,
        "course_data_id": course_data.id,
        "company_logo": certificate_details.company_logo.url if certificate_details.company_logo else "",
        "dev_signature": certificate_details.dev_signature.url if certificate_details.dev_signature else "",
        "dev_first_name": certificate_details.dev_id.first_name,
        "dev_last_name": certificate_details.dev_id.last_name,
        "dev_company_name": certificate_details.dev_id.company_name,
        "digital_signature": digital_signature,
    }
    return render(request, "studentapp/view-certificate.html", context)


def generate_certificate_pdf(request, course_data_id):
    try:
        course_data = devModels.Online_Certification_Course.objects.get(id=course_data_id)
    except devModels.Online_Certification_Course.DoesNotExist:
        return HttpResponse("Course not found", status=404)

    try:
        certificate_details = devModels.Certificate_Details.objects.get(dev_id=course_data.dev_id)
    except devModels.Certificate_Details.DoesNotExist:
        return HttpResponse("Certificate details not found", status=404)

    issued_certificate = devModels.Issued_Certificate.objects.filter(
        student_id=request.user, course_id=course_data
    ).first()

    if issued_certificate:
        digital_signature = issued_certificate.digital_signature
    else:
        digital_signature = dev_views.generate_digital_signature(
            request.user, course_data_id, certificate_details.id
        )

    def get_file_url(media_file):
        if media_file:
            abs_path = os.path.join(settings.MEDIA_ROOT, str(media_file))
            abs_path = abs_path.replace("\\", "/") 
            return f"file:///{abs_path}"
        return ""

    context = {
        "student_name": request.user.username,
        "course_name": course_data.course_name,
        "course_id": course_data.id,
        "company_logo": get_file_url(certificate_details.company_logo),
        "dev_signature": get_file_url(certificate_details.dev_signature),
        "dev_name": certificate_details.dev_id.username,
        "digital_signature": digital_signature,
        "certificate_id": issued_certificate.id if issued_certificate else "Not Issued",
    }

    print("dev_signature path =>", context["dev_signature"])  # Check the path

    html_string = render_to_string('studentapp/certificate_pdf.html', context)

    pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf()

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{request.user.username}_certificate.pdf"'
    return response


def student_course_query_form(request, course_data_id, id):
    course_data = devModels.Online_Certification_Course.objects.get(id=course_data_id)
    course_topic_data = devModels.Course_Module_Content.objects.get(id=id)

    if request.method == "POST":
        course_name = request.POST.get('course_name')
        document_name = request.POST.get('document_name')
        student_query_content = request.POST.get('student_query_content')
        newStudentQuery = studentModels.Student_Course_Query.objects.create(
            student_id=request.user,
            course_name=course_data,
            document_name=course_topic_data,
            student_query_content=student_query_content
        )
        newStudentQuery.save()
        return redirect(reverse('course_document_content', args=[course_data_id, id]))
    context = {
        'course_data': course_data,
        'course_data_id': course_data_id,
        'course_document_content_data': id,
        'course_topic_data': course_topic_data,
    }
    return render(request, "studentapp/student-course-query-form.html", context=context)

def feedback(request):
    user_data = request.user
    if not user_data.is_authenticated:
        return redirect('login')
    if request.method == "POST":
        rating = request.POST.get('rating')
        feedback_content = request.POST.get('feedback_content')
        add_new_feedback = studentModels.Feedback.objects.create(
            user_id = request.user,
            rating = rating,
            feedback_content = feedback_content
        )
        add_new_feedback.save()
        return redirect(home)
    return render(request,"studentapp/feedback.html")


def update_profile(request,id):
    user_data = request.user
    if not user_data.is_authenticated:
        return redirect('login')
    student_data = User.objects.get(id=id)
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        contact = request.POST.get('contact')
        address = request.POST.get('address')
        institute_name = request.POST.get('institute_name')
        last_sem_marksheet = request.FILES.get('last_sem_marksheet')
        student_resume = request.FILES.get('student_resume')
        course = request.POST.get('course')
        student_img = request.FILES.get('student_img')

        if User.objects.filter(username=username).exclude(id=id).exists():
            return render(request, "studentapp/update-profile.html", {
                'name_alert': "That Username is already taken.",
                'student_data': student_data,
            })

        student_data.first_name=first_name
        student_data.last_name=last_name
        student_data.username=username
        student_data.contact=contact
        student_data.address=address
        student_data.institute_name=institute_name
        student_data.course=course
        if last_sem_marksheet:
            student_data.last_sem_marksheet = last_sem_marksheet

        if student_resume:
            student_data.student_resume = student_resume

        if student_img:
            student_data.student_img = student_img
        student_data.save()
        return redirect(profile)
    context = {
        'student_data':student_data,
    }
    return render(request,"studentapp/update-profile.html",context=context)


def delete_profile_image(request,id):
    student_data = User.objects.get(id=id)
    student_data.student_img = None
    student_data.save()
    return redirect(profile)


def student_query_details(request):
    query_data = studentModels.Student_Course_Query.objects.filter(student_id=request.user)
    query_response_data = devModels.Response_Student_Query.objects.filter(query_id__in=query_data)
    paginator = Paginator(query_data, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'student_query_data':page_obj,
        'query_response_data':query_response_data,
    }
    return render(request,"studentapp/student-query-table-data.html",context=context)