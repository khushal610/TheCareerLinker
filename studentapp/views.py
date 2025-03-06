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
import math,random
from TheCareerLinker import views as TCL_views
from django.core.paginator import Paginator
import datetime
from django.urls import reverse
from django.http import Http404

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
    course_data = devModels.Online_Certification_Course.objects.filter(is_launched=True)
    course_enrollment_data = studentModels.Course_Enrollment.objects.filter(student_id=request.user)
    context = {
        'course_data':course_data,
        'course_enrollment_data':course_enrollment_data,
    }
    return render(request,'studentapp/courses.html',context=context)

# course-details page
def course_details(request, id):
    course_details = devModels.Online_Certification_Course.objects.get(id=id, is_launched=True)
    dev_id = course_details.dev_id
    course_module_data = devModels.Module_list.objects.filter(course_id=id, dev_id=dev_id)

    module_stage_data_details = {}
    for module_data in course_module_data:
        module_id = module_data.id
        module_stage_data = list(devModels.Module_Stage.objects.filter(module_id=module_id, dev_id=dev_id))  
        if module_stage_data:
            module_stage_data_details[module_id] = module_stage_data
            print("=============================>",module_stage_data_details)

    context = {
        'course_details': course_details,
        'course_module_data': course_module_data,
        'module_stage_data': module_stage_data_details
    }
    return render(request, 'studentapp/course-details.html', context)


def course_enrollment(request, id):
    course_data = devModels.Online_Certification_Course.objects.get(id=id)
    dev_id = course_data.dev_id
    course_module_data = devModels.Module_list.objects.filter(course_id=id, dev_id=dev_id)

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
                # quiz_id = course_module_content_data.course_quiz
                # quiz_questions = devModels.QuizQuestions.objects.filter(quiz_category_id=quiz_id)
                # print("---------quiz questions--------------------------------------->",quiz_questions)
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
    }
    if studentModels.Course_Enrollment.objects.filter(student_id=request.user,course_id=id).exists():
        return render(request, "studentapp/course-enrollments.html",context=context)
    studentModels.Course_Enrollment.objects.create(
        student_id=request.user,
        course_id=course_data,
        is_payment_received=False
    )
    return render(request, "studentapp/course-enrollments.html", context=context)


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
    quiz_attempted_data = Quiz_attempt.objects.filter(student_id=request.user)
    total_questions_as_quiz_category = {}
    for quiz_questions in quiz_attempted_data:
        quiz_category_id = quiz_questions.quiz_category.id
        total_questions = devModels.QuizQuestions.objects.filter(quiz_category_id=quiz_category_id).count()
        total_questions_as_quiz_category[quiz_category_id] = total_questions
    print("----------------------->",total_questions_as_quiz_category)
    context = {
        'userdata':data,
        'quiz_attempted_data':quiz_attempted_data,
        'total_questions':total_questions_as_quiz_category
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
    quiz_data_list = devModels.QuizCategory.objects.filter(is_approved=True,is_course_quiz=False)
    developer_data = User.objects.all()
    context = {
        'data':quiz_data_list,
        'developer_data':developer_data
    }
    return render(request,"studentapp/quiz-list.html",context=context)


def quiz(request, id):
    quiz_category_data = devModels.QuizCategory.objects.get(id=id)
    quiz_questions = devModels.QuizQuestions.objects.filter(quiz_category_id=id)
    quiz_questions_options = devModels.QuizOptions.objects.all()
    context = {
        'data': quiz_questions,
        'options': quiz_questions_options
    }
    if request.method == "POST":
        score = 0
        total_questions = quiz_questions.count()
        for question in quiz_questions:
            user_choice = request.POST.get(f"user_choice_{question.id}")
            try:
                quiz_answer = devModels.QuizOptions.objects.get(question_id=question.id)
                correct_answer = quiz_answer.option_1
                if user_choice == correct_answer:
                    score += 1
            except devModels.QuizOptions.DoesNotExist:
                continue
        quiz_category = devModels.QuizCategory.objects.get(id=id)
        quiz_attempt_form = forms.QuizAttemptForm(request.POST)
        if quiz_attempt_form.is_valid():
            quiz_attempt_obj = quiz_attempt_form.save(commit=False)
            quiz_attempt_obj.student_id = request.user
            quiz_attempt_obj.quiz_category = quiz_category
            quiz_attempt_obj.score = score
            quiz_attempt_obj.save()
            if quiz_category_data.is_course_quiz == False:
                send_quiz_score_to_email(request.user,id,score,total_questions)
            return redirect(score_card)
        else:
            print(quiz_attempt_form.errors)
        context["score"] = score
        context["total_questions"] = total_questions
    return render(request, "studentapp/quiz.html", context=context)


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
    if data.score != 0:
        average = totalQuestions / data.score
    else:
        average = 0
    print("Average score:", average)
    print("Total Questions:", totalQuestions)
    context = {
        'data': data,
        'quiz_category': findQuizCatName,
        'totalQuestions': totalQuestions,
        'average': average
    }
    return render(request, "studentapp/score-card.html", context=context)


def live_sessions(request):
    session_data = devModels.Online_sessions.objects.all()
    company_filter = request.GET.get('company_filter')

    if company_filter and company_filter != 'all':
        session_data = session_data.filter(dev_name__company_name=company_filter)
    company_data = User.objects.filter(role="Developer")
    paginator = Paginator(session_data, 2)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'session_data': page_obj,
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


def course_document_content(request,course_data_id,id):
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
                course_module_content_data = list(devModels.Course_Module_Content.objects.filter(stage_id=stage_id,dev_id=dev_id))
                if course_module_content_data:
                    module_content_data_details[stage_id] = course_module_content_data
                print("------content_data---------------------------------------->\n",course_module_content_data)
                print("===module_content_data_details=====================>\n",module_content_data_details)
                print("===stage_id=====================>\n",module_content_data_details.keys())
                print("===content_data=====================>\n",module_content_data_details.values())
                print("===items()=====================>\n",module_content_data_details.items())

    course_document_content_data = devModels.Course_Module_Content.objects.get(id=id)
    context = {
        "course_document_content_data":course_document_content_data,
        'course_data': course_data,
        'course_data_id':course_data.id,
        'stage_data_id':stage_id,
        'course_module_data': course_module_data,
        'module_stage_data': module_stage_data_details,
        'module_content_data': module_content_data_details,
    }
    return render(request,"studentapp/course-document-content.html",context=context)


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

    # ✅ Extract stage_id properly
    stage_id = course_document_content_data.stage_id.id  

    # Get the last stage and last content of the course
    last_stage = devModels.Module_Stage.objects.filter(
        module_id__in=course_module_data.values_list('id', flat=True), dev_id=dev_id
    ).order_by('-id').first()

    last_content = devModels.Course_Module_Content.objects.filter(
        stage_id=stage_id, dev_id=dev_id
    ).order_by('-id').first()

    # Check if the current content is the last in the course
    is_last_content = (course_document_content_data.id == last_content.id) and (stage_id == last_stage.id)

    # Find the next content
    next_content = devModels.Course_Module_Content.objects.filter(
        stage_id=stage_id, dev_id=dev_id, id__gt=id
    ).order_by('id').first()

    if not next_content:
        # If no next content, move to the first content of the next stage
        next_stage = devModels.Module_Stage.objects.filter(id__gt=stage_id, dev_id=dev_id).order_by('id').first()
        if next_stage:
            next_content = devModels.Course_Module_Content.objects.filter(
                stage_id=next_stage.id, dev_id=dev_id
            ).order_by('id').first()

    if next_content:
        id = next_content.id  # Update to the next content's ID
    else:
        # If no next content exists, stay on the same page
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

    # add student id ,course id, document id to database
    if studentModels.Course_Progress_Tracker.objects.filter(student_id=request.user,course_id=course_data_id,document_id=course_document_content_data).exists():
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

    # ✅ Extract stage_id properly
    stage_id = course_document_content_data.stage_id.id  

    # Get the first stage and first content of the course
    first_stage = devModels.Module_Stage.objects.filter(
        module_id__in=course_module_data.values_list('id', flat=True), dev_id=dev_id
    ).order_by('id').first()

    first_content = devModels.Course_Module_Content.objects.filter(
        stage_id=stage_id, dev_id=dev_id
    ).order_by('id').first()

    # Check if the current content is the first in the stage
    is_first_content = (course_document_content_data.id == first_content.id) and (stage_id == first_stage.id)

    # Find the previous content
    prev_content = devModels.Course_Module_Content.objects.filter(
        stage_id=stage_id, dev_id=dev_id, id__lt=id
    ).order_by('-id').first()

    if not prev_content:
        # If there is no previous content, move to the last content of the previous stage
        prev_stage = devModels.Module_Stage.objects.filter(id__lt=stage_id, dev_id=dev_id).order_by('-id').first()
        if prev_stage:
            prev_content = devModels.Course_Module_Content.objects.filter(
                stage_id=prev_stage.id, dev_id=dev_id
            ).order_by('-id').first()

    if prev_content:
        id = prev_content.id  # Update to the previous content's ID
    else:
        # If no previous content exists, stay on the same page
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
    return redirect(reverse('course_document_content', args=[course_data_id, id]))

