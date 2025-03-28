from django.shortcuts import render,HttpResponse,redirect
from devapp import models,forms
from studentapp.models import User,Attempted_session,Quiz_attempt,Student_Course_Query,Feedback
from TheCareerLinker import views as TCL_views
from django.contrib.auth import logout
from django.core.paginator import Paginator
from django.conf import settings
from django.core.mail import send_mail
from django.contrib import messages
from django.urls import reverse
import base64
import uuid
from django.core.files.base import ContentFile
import random,string
from django.db.models import Q
from django.db.models import Count
import json
# for celery worker
# from devapp.tasks import send_online_session_email

# Create your views here.
def index(request):
    dev_name = request.user
    totalQuizCategory = models.QuizCategory.objects.filter(dev_id=request.user,is_course_quiz=False).count()
    totalOnlineSessions = models.Online_sessions.objects.filter(dev_name=request.user).count()
    totalUnselectedStudents = User.objects.filter(is_selected=False,role="Student").count()
    totalSelectedStudents = User.objects.filter(is_selected=True,role="Student").count()
    quiz_data = (
        Quiz_attempt.objects
        .filter(quiz_category__is_course_quiz=False)
        .values('quiz_category__quiz_category_name')
        .annotate(count=Count('quiz_category'))
    )
    categories = [item['quiz_category__quiz_category_name'] for item in quiz_data]
    attempts = [item['count'] for item in quiz_data]
    print("-----------------------------------categories",categories)
    print("-----------------------------------attmptes",attempts)
    context = {
        'categories': json.dumps(categories),
        'attempts': json.dumps(attempts),
        'dev_name': dev_name,
        'totalQuizCategory':totalQuizCategory,
        'totalOnlineSessions':totalOnlineSessions,
        'totalUnselectedStudents':totalUnselectedStudents,
        'totalSelectedStudents':totalSelectedStudents
    }
    return render(request, 'devapp/index.html', context=context)


def dev_widget(request):
    return render(request,'devapp/widget.html')

def dev_forms(request):
    return render(request,'devapp/form.html')


def dev_profile_bio_forms(request):
    return render(request,'devapp/dev-profile-bio.html')


def dev_profile(request):
    totalCertificationCourse = models.Online_Certification_Course.objects.filter(dev_id=request.user,is_launched=True).count()
    totalQuiz = models.QuizCategory.objects.filter(dev_id=request.user,is_approved=True).count()
    totalOnlineSessions = models.Online_sessions.objects.filter(dev_name=request.user).count()
    totalSelectedStudent = User.objects.filter(role="Student",is_selected=True,company_name=request.user.company_name).count()
    context = {
        'totalCertificationCourse':totalCertificationCourse,
        'totalQuiz':totalQuiz,
        'totalOnlineSessions':totalOnlineSessions,
        'totalSelectedStudent':totalSelectedStudent,
    }
    return render(request,'devapp/dev-profile.html',context=context)


# ----------------------signup developer
def dev_signUp(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        contact = request.POST.get('contact')
        password = request.POST.get('password')
        confirmPassword = request.POST.get('confirmPassword')
        company_name = request.POST.get('company_name')
        bio_title = request.POST.get('bio_title')
        bio_detail = request.POST.get('bio_detail')
        experties = request.POST.get('experties')
        experience = request.POST.get('experience')
        dev_img = request.FILES.get('dev_img')

        try:
            User.objects.get(username=username)
            return render(request,"devapp/signup.html",{'exist_dev_alert':"Username already exist"})
        except:
            if password == confirmPassword:
                User.objects.create_user(
                    first_name=first_name,
                    last_name=last_name,
                    username=username,
                    email=email,
                    contact=contact,
                    password=password,
                    company_name=company_name,
                    bio_title=bio_title,
                    bio_detail=bio_detail,
                    experties=experties,
                    experience=experience,
                    dev_img=dev_img,
                    role=User.DEVELOPER,
                    is_verified=False
                )
                return redirect(TCL_views.main_login)
            else:
                return render(request,"devapp/signup.html",{'error':"Password Doesn't Match"})
    return render(request,"devapp/signup.html",{'role':User.DEVELOPER})

def dev_signOut(request):
    logout(request)
    return redirect(TCL_views.main_login)

def add_quiz_category(request):
    if request.method == "POST":
        quiz_category_name = request.POST.get('quiz_category_name')
        quiz_level = request.POST.get('quiz_level')
        if quiz_level == "None":
            return render(request,"devapp/add-quiz-category.html",{'level_error':"Please Define the quiz level"})
        findQuiz = models.QuizCategory.objects.filter(
            quiz_category_name = quiz_category_name,
            quiz_level = quiz_level,
            dev_id=request.user
        )
        if findQuiz.exists():
            return render(request,"devapp/add-quiz-category.html",{'quiz_name_error':"Quiz Category with same level already existed"})
        else:
            form = forms.QuizCategoryForm(request.POST)
            if form.is_valid():
                form_obj = form.save(commit=False)
                form_obj.is_approved = False
                form_obj.dev_id = request.user
                form_obj.save()
                return render(request,"devapp/add-quiz-category.html",{'alert':"New category added"})
            else:
                print(form.errors)
                return HttpResponse("Error")
    return render(request,"devapp/add-quiz-category.html")


def add_questions(request):
    data = models.QuizCategory.objects.filter(dev_id=request.user)
    paginator = Paginator(data, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'data':page_obj}
    if request.method == "POST":
        quiz_question = request.POST.get('quiz_question')
        quiz_category_id = request.POST.get('quiz_category_id')
        quiz_question_summary = request.POST.get('quiz_question_summary')
        if quiz_question == "":
            return render(request,"devapp/add-questions.html",{
                'question_error':"Please enter the value",
                'data':data
            })
        if quiz_category_id == "None":
            return render(request,"devapp/add-questions.html",{
                'quiz_cat_id_error':"Please select the quiz category",
                'data':data
            })
        quiz_cat_id_instance = models.QuizCategory.objects.get(id=quiz_category_id)
        form_question = forms.QuizQuestionForm(request.POST)
        if form_question.is_valid():
            form_question_obj = form_question.save(commit=False)
            form_question_obj.quiz_category_id = quiz_cat_id_instance
            form_question_obj.quiz_question_summary = quiz_question_summary
            form_question_obj.save()
            return redirect(add_questions)
        else:
            print(form_question.errors)
    return render(request,'devapp/add-questions.html',context=context)



def add_options(request,id):
    questions = models.QuizQuestions.objects.filter(quiz_category_id=id)
    options = models.QuizOptions.objects.all()
    if request.method == "POST":
        option_1 = request.POST.get('option_1')
        option_2 = request.POST.get('option_2')
        option_3 = request.POST.get('option_3')
        option_4 = request.POST.get('option_4')
        question_id = request.POST.get('question_id')
        question_id_instance = models.QuizQuestions.objects.get(id=question_id)
        print(option_1,option_2,option_3,option_4)
        print("---------------------------------------------->",question_id)
        options_form = forms.QuizOptionsForm(request.POST)
        findQuestion = models.QuizQuestions.objects.get(id=question_id)
        print("---------------------------------------------->",question_id_instance)
        if options_form.is_valid():
            option_form_obj = options_form.save(commit=False)
            option_form_obj.question_id = question_id_instance
            option_form_obj.save()
            findQuestion.is_option_added = True
            findQuestion.save()
        else:
            print(options_form.errors)
    paginator = Paginator(questions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        # 'data':questions,
        'data':page_obj,
        'options':options
        }
    return render(request,'devapp/add-options.html',context=context)


def update_options(request,id):
    question_data = models.QuizQuestions.objects.get(id=id)
    quiz_category_id = question_data.quiz_category_id.id
    options = models.QuizOptions.objects.get(question_id=question_data)
    if request.method == "POST":
        quiz_question = request.POST.get('quiz_question')
        quiz_question_summary = request.POST.get('quiz_question_summary')
        option_1 = request.POST.get('option_1')
        option_2 = request.POST.get('option_2')
        option_3 = request.POST.get('option_3')
        option_4 = request.POST.get('option_4')
        print(quiz_question)
        question_data.quiz_question = quiz_question
        question_data.quiz_question_summary = quiz_question_summary
        question_data.save()
        options.option_1 = option_1
        options.option_2 = option_2
        options.option_3 = option_3
        options.option_4 = option_4
        options.save()
        return redirect(reverse('add_options', args=[quiz_category_id]))
        # return redirect(add_questions)
    context = {
        'data':question_data,
        'options':options,
    }
    return render(request,"devapp/update-options.html",context=context)


def delete_question(request,id):
    question_data = models.QuizQuestions.objects.get(id=id)
    question_data.delete()
    return redirect(add_questions)



def edit_profile(request,id):
    dev_data = User.objects.get(id=id)
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        contact = request.POST.get('contact')
        company_name = request.POST.get('company_name')
        bio_title = request.POST.get('bio_title')
        bio_detail = request.POST.get('bio_detail')
        experties = request.POST.get('experties')
        experience = request.POST.get('experience')
        dev_img = request.FILES.get('dev_img')

        dev_data.first_name = first_name
        dev_data.last_name = last_name
        dev_data.username = username
        dev_data.contact = contact
        dev_data.company_name = company_name
        dev_data.bio_title = bio_title
        dev_data.bio_detail = bio_detail
        dev_data.experties = experties
        dev_data.experience = experience
        if dev_img:
            dev_data.dev_img = dev_img
        dev_data.save()
        return redirect(dev_profile)
    context = { 
        'dev_data':dev_data,
    }
    return render(request,"devapp/update-profile.html",context=context)

def quiz_category_table(request):
    data = models.QuizCategory.objects.filter(dev_id=request.user)
    paginator = Paginator(data, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'data': page_obj}
    return render(request, "devapp/quiz-category-table.html", context=context)


def update_quiz_category(request,id):
    data = models.QuizCategory.objects.get(id=id)
    context = {'data':data}
    if request.method == "POST":
        quiz_category_name = request.POST.get('quiz_category_name')
        quiz_level = request.POST.get('quiz_level')
        findQuiz = models.QuizCategory.objects.filter(
                    quiz_category_name = quiz_category_name,
                    quiz_level = quiz_level,
                    dev_id=request.user
                ).exclude(id=id)
        
        if quiz_level == "None":
            return render(request,"devapp/update-quiz-category.html",{
                'data':data,
                'level_error':"Please Define the quiz level"
            })

        if findQuiz.exists():
            return render(request,"devapp/update-quiz-category.html",{
                'data':data,
                'alert':"Quiz Category with same level already existed"
            })

        data.quiz_category_name = quiz_category_name
        data.quiz_level = quiz_level
        data.save()
        return redirect(quiz_category_table)
    return render(request,"devapp/update-quiz-category.html",context=context)

def quiz_approve(request,id):
    data = models.QuizCategory.objects.get(id=id)
    data.is_approved = True
    data.save()
    return redirect(quiz_category_table)

def quiz_disapprove(request,id):
    data = models.QuizCategory.objects.get(id=id)
    data.is_approved = False
    data.save()
    return redirect(quiz_category_table)

def add_to_course_quiz(request,id):
    data = models.QuizCategory.objects.get(id=id)
    data.is_course_quiz = True
    data.save()
    return redirect(quiz_category_table)

def remove_from_course_quiz(request,id):
    data = models.QuizCategory.objects.get(id=id)
    data.is_course_quiz = False
    data.save()
    return redirect(quiz_category_table)

def add_online_session(request):
    if request.method == "POST":
        dev_name = request.user
        topic_name = request.POST.get('topic_name')
        meeting_link = request.POST.get('meeting_link')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        week_days = request.POST.getlist('week_days')

        session = models.Online_sessions.objects.create(
            dev_name=dev_name,
            topic_name=topic_name,
            meeting_link=meeting_link,
            start_time=start_time,
            end_time=end_time,
            is_live=False,
            week_days=week_days,
        )
        session.save()
        return render(request,"devapp/add-online-sessions.html",{'alert':"Class created"})
    return render(request,"devapp/add-online-sessions.html")


def online_session_table(request):
    class_data = models.Online_sessions.objects.filter(dev_name=request.user)
    context = {
        'class_data':class_data
    }
    return render(request,"devapp/online-session-table.html",context=context)


def update_online_sessions(request,id):
    online_session_data = models.Online_sessions.objects.get(id=id)
    context = {
        'class_data':online_session_data
    }
    if request.method == "POST":
        topic_name = request.POST.get('topic_name')
        meeting_link = request.POST.get('meeting_link')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        week_days = request.POST.getlist('week_days')

        online_session_data.topic_name = topic_name
        online_session_data.meeting_link = meeting_link
        online_session_data.start_time = start_time
        online_session_data.end_time = end_time
        online_session_data.week_days = week_days
        online_session_data.save()
        return redirect(online_session_table)
    return render(request,"devapp/update-online-sessions.html",context=context)


def delete_online_session(request,id):
    session_data = models.Online_sessions.objects.get(id=id)
    session_data.delete()
    return redirect(online_session_table)


def activate_online_session(request,id):
    session_data = models.Online_sessions.objects.get(id=id)
    meeting_link = session_data.meeting_link
    session_data.is_live = True
    session_data.save()
    return redirect(meeting_link)

def deactivate_online_session(request,id):
    session_data = models.Online_sessions.objects.get(id=id)
    session_data.is_live = False
    session_data.save()
    return redirect(online_session_table)


def notify_students(request, id):
    all_students = User.objects.filter(role="Student")
    session_data = models.Online_sessions.objects.get(id=id)
    company_data = User.objects.get(username=session_data.dev_name)
    topic_name = session_data.topic_name
    start_time = session_data.start_time
    end_time = session_data.end_time
    dev_name = session_data.dev_name
    company_name = company_data.company_name
    print(topic_name)
    print(start_time)
    print(end_time)
    print("------------------->", dev_name)
    print("------------------->", company_name)
    print("--------------------------------->", all_students)
    for student in all_students:
        student_email = student.email
        online_session_email_notification(student_email, topic_name, student.username, start_time, end_time, dev_name, company_name)
        print(student.username, " -- ", student_email)
    return redirect(online_session_table)


def online_session_email_notification(student_email, topic_name, student_name, start_time, end_time, dev_name, company_name):
    subject = f"Reminder - {topic_name}"
    message = f"""
    <p>Dear {student_name},</p>

    <p>I hope this message finds you well.</p>

    <p>I am writing to remind you about the upcoming session scheduled to start within the next 5 minutes or soon. Please find the session details below:</p>

    <h4>{topic_name} Session starts at {start_time} and will end at {end_time}. This session is scheduled by {dev_name} from {company_name}.</h4>

    <p>Instructions for the Student: Please stay active and check for notifications to find and join suitable online sessions according to your needs. It is essential to ensure that you are prepared and ready to join the session promptly.</p>

    <p>Thank you for your attention to this matter. Should you have any questions or require further assistance, please do not hesitate to reach out.</p>
    <br>
    Best regards,<br>
    The Career Linker Team
    </p>
    """
    from_email = settings.EMAIL_HOST_USER
    to_email = student_email
    send_mail(subject, '', from_email, [to_email], html_message=message)


# # for celery worker 
# def notify_students(request, id):
#     all_students = User.objects.filter(role="Student")
#     session_data = models.Online_sessions.objects.get(id=id)
#     company_data = User.objects.get(username=session_data.dev_name)
#     topic_name = session_data.topic_name
#     start_time = str(session_data.start_time)
#     end_time = str(session_data.end_time)
#     dev_name = str(session_data.dev_name)
#     company_name = str(company_data.company_name)

#     for student in all_students:
#         # Send the email task asynchronously
#         send_online_session_email.delay(student.email, topic_name, student.username, start_time, end_time, dev_name, company_name)

#     messages.success(request, "Notifications sent successfully.")
#     return redirect('online_session_table')


def view_attempted_session_student(request,id):
    session_data = models.Online_sessions.objects.get(id=id)
    attempted_session_data = Attempted_session.objects.filter(session_id=id)
    paginator = Paginator(attempted_session_data, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'attempted_session_data':page_obj,
        'session_data':session_data
    }
    return render(request,"devapp/attempted-session-table.html",context=context)


def view_quiz_attempted_student(request,id):
    quiz_data = models.QuizCategory.objects.get(id=id)
    attempted_quiz_data = Quiz_attempt.objects.filter(quiz_category=id)
    total_questions = models.QuizQuestions.objects.filter(quiz_category_id=id).count()
    paginator = Paginator(attempted_quiz_data, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'attempted_quiz_data':page_obj,
        'quiz_data':quiz_data,
        'total_questions':total_questions
    }
    return render(request,"devapp/quiz-attempted-students-table.html",context=context)



def shortlisting_student(request):
    query = request.GET.get('search', '')
    student_data = User.objects.filter(role="Student",is_selected=False)

    if query:
        student_data = student_data.filter(
            Q(username__icontains=query) | Q(institute_name__icontains=query) | Q(course__icontains=query)
        )

    paginator = Paginator(student_data, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'student_data': page_obj,
        'search_query': query
    }
    return render(request, "devapp/shortlisting-table.html", context)


def student_quiz_attempts(request,id):
    username = User.objects.get(id=id)
    quiz_attempted_data = Quiz_attempt.objects.filter(student_id=username.id)
    totalQuestions = {}
    for attempt in quiz_attempted_data:
        quiz_category_id = attempt.quiz_category
        total_questions = models.QuizQuestions.objects.filter(quiz_category_id=quiz_category_id).count()
        totalQuestions[quiz_category_id] = total_questions
    print("--------------------------->", totalQuestions)
    paginator = Paginator(quiz_attempted_data, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'student_quiz_data':page_obj,
        'totalQuestions':totalQuestions,
    }
    return render(request,"devapp/specific-student-quiz-attempt.html",context=context)


def student_session_attempts(request,id):
    username = User.objects.get(id=id)
    print("------------------------------------->",username)
    session_attempted_data = Attempted_session.objects.filter(student_name=username)
    print("=============================================>",session_attempted_data)
    paginator = Paginator(session_attempted_data, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'session_attempted_data':page_obj
    }
    return render(request,"devapp/specific-student-session-attempt.html",context=context)

def shortlisting_student_selection(request,id):
    dev_name = request.user
    user_data = User.objects.get(username=dev_name)
    company_name = user_data.company_name
    student_data = User.objects.get(id=id)
    print("------------------------------------------->",student_data) # 20 student id
    print("------------------------------------------->",company_name) # dev_company_name
    if student_data.is_selected == False:
        student_data.is_selected = True
        student_data.company_name = company_name
        student_data.save()
        send_shortlisting_email_to_student(student_data.email,student_data.username,company_name)
    else:
        student_data.is_selected = False
        student_data.company_name = ""
        student_data.save()
    return redirect(shortlisting_student)


def send_shortlisting_email_to_student(student_email,student_name,company_name):
    subject = f"Congratulations! You Have Been Selected by {company_name}"
    message = f"""
    <p>Dear {student_name},
    <br><br>
    We are pleased to inform you that you have been selected by <b>{company_name}</b> for an opportunity within their organization. After careful evaluation, the developer from <b>{company_name}</b> has chosen you based on your skills and performance.
    <br><br>
    Next Steps:
    <br><br>
    • You will receive further communication from the company regarding the onboarding process.<br><br>
    • Please ensure that you check your email regularly for any updates.<br><br>
    • If you have any questions, feel free to reach out.<br><br>
    <br><br>
    Congratulations once again! We wish you great success in your new journey.
    <br><br>
    Best Regards,<br>
    The Career Linker Team
    </p>
    """
    from_email = settings.EMAIL_HOST_USER
    to_email = student_email
    send_mail(subject, '', from_email, [to_email], html_message=message)
    return


def add_online_courses(request):
    if request.method == "POST":
        course_type = request.POST.get('course_type')
        course_charges = request.POST.get('course_charges')
        if course_type == "Free":
            if course_charges != "0":
                return render(request,"devapp/update-certification-course.html",{"error":"You cannot select any charges for free course"})
            
        if course_type == "Paid":
            if course_charges == "0":
                return render(request,"devapp/update-certification-course.html",{"error":"You cannot select 0 rupee for paid course"})
            
        course_form = forms.CourseForm(request.POST)
        if course_form.is_valid():
            course_form_obj = course_form.save(commit=False)
            course_form_obj.dev_id = request.user
            course_form_obj.save()
            return redirect(certification_course_list)
        else:
            print(course_form.errors)
    return render(request,"devapp/add-online-courses.html")

def update_certification_course(request,id):
    course_data = models.Online_Certification_Course.objects.get(id=id)
    context = {
        'course_data':course_data
    }
    if request.method == "POST":
        course_name = request.POST.get('course_name')
        course_thumbnail_image = request.FILES.get('course_thumbnail_image')
        course_summary = request.POST.get('course_summary')
        course_duration = request.POST.get('course_duration')
        course_type = request.POST.get('course_type')
        course_charges = request.POST.get('course_charges')
        if course_type == "Free":
            if course_charges != "0":
                return render(request,"devapp/update-certification-course.html",{"error":"You cannot select any charges for free course",'course_data':course_data})
            
        if course_type == "Paid":
            if course_charges == "0":
                return render(request,"devapp/update-certification-course.html",{"error":"You cannot select 0 rupee for paid course",'course_data':course_data})

        course_data.course_name = course_name
        course_data.course_thumbnail_image = course_thumbnail_image
        course_data.course_summary = course_summary
        course_data.course_duration = course_duration
        course_data.course_type = course_type
        course_data.course_charges = course_charges
        course_data.save()
        return redirect(certification_course_list)
    return render(request,"devapp/update-certification-course.html",context=context)

def delete_online_certification_course(request,id):
    course_data = models.Online_Certification_Course.objects.get(id=id)
    course_data.delete()
    return redirect(certification_course_list)

def certification_course_list(request):
    course_data = models.Online_Certification_Course.objects.filter(dev_id=request.user)
    paginator = Paginator(course_data, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'course_data':page_obj
    }
    return render(request,"devapp/certification-course-table.html",context=context)

def launch_course(request,id):
    course_data = models.Online_Certification_Course.objects.get(id=id,dev_id=request.user)
    course_data.is_launched = True
    course_data.save()
    return redirect(certification_course_list)

def unlaunch_course(request,id):
    course_data = models.Online_Certification_Course.objects.get(id=id,dev_id=request.user)
    course_data.is_launched = False
    course_data.save()
    return redirect(certification_course_list)

def add_course_module(request,course_id):
    module_data = models.Module_list.objects.filter(course_id=course_id,dev_id=request.user)
    course_data = models.Online_Certification_Course.objects.get(id=course_id,dev_id=request.user)
    context = {
        'module_data':module_data,
        'course_data':course_data,
    }
    if request.method == "POST":
        module_name = request.POST.get('module_name')
        module_name_list = ['Module 1', 'Module 2', 'Module 3', 'Module 4', 'Module 5', 'Module 6', 'Module 7', 'Module 8', 'Module 9', 'Module 10']
        get_course_data = models.Online_Certification_Course.objects.get(id=course_id)
        if module_name not in module_name_list:
            return render(request, "devapp/add-course-modules.html", {"check_name": "Give valid module name",'module_data':module_data})
        try:
            get_existing_module_name = models.Module_list.objects.filter(module_name=module_name, dev_id=request.user, course_id=course_id)
            if get_existing_module_name.exists():
                return render(request, "devapp/add-course-modules.html", {"module_exist": "That module name already exists",'module_data':module_data})
            add_new_module = models.Module_list.objects.create(
                module_name=module_name,
                course_id=get_course_data,
                dev_id=request.user
            )
            add_new_module.save()
            return render(request, "devapp/add-course-modules.html", {"module_alert": "New module added",'module_data':module_data})
        
        except Exception as e:
            return render(request, "devapp/add-course-modules.html", {"error_message": str(e),'module_data':module_data})
    return render(request, "devapp/add-course-modules.html",context=context)

def delete_course_module(request,id):
    course_module_data = models.Module_list.objects.get(id=id)
    course_id = course_module_data.course_id.id
    course_module_data.delete()
    return redirect(reverse('add_course_module', args=[course_id]))
    # return redirect(add_course_module)


def add_module_stages(request, module_id):
    module_data = models.Module_list.objects.get(id=module_id, dev_id=request.user)
    module_stage_data = models.Module_Stage.objects.filter(module_id=module_id, dev_id=request.user)
    context = {
        'module_stage_data': module_stage_data,
        'module_data': module_data,
    }
    if request.method == "POST":
        stage_name = request.POST.get('stage_name')
        if models.Module_Stage.objects.filter(stage_name=stage_name, module_id=module_id, dev_id=request.user).exists():
            context['stage_exist'] = "That stage name already exists."
            return render(request, "devapp/add-module-stages.html", context)
        models.Module_Stage.objects.create(
            stage_name=stage_name,
            module_id=module_data,
            dev_id=request.user
        )
        context['stage_alert'] = "New Stage added successfully"
        return render(request, "devapp/add-module-stages.html", context)
    return render(request, "devapp/add-module-stages.html", context)

def delete_module_stage(request,id):
    module_stage_data = models.Module_Stage.objects.get(id=id)
    module_id = module_stage_data.module_id.id
    module_stage_data.delete()
    return redirect(reverse('add_module_stages', args=[module_id]))

def add_course_items(request,stage_id):
    module_stage_data = models.Module_Stage.objects.get(id=stage_id,dev_id=request.user)
    course_module_content_data = models.Course_Module_Content.objects.filter(stage_id=stage_id,dev_id=request.user)
    quiz_category_data = models.QuizCategory.objects.filter(is_course_quiz=True,dev_id=request.user)
    context = {
        'module_stage_data':module_stage_data,
        'course_module_content_data':course_module_content_data,
        'quiz_category_data':quiz_category_data,
    }
    if request.method == "POST":
        documentation_name = request.POST.get('documentation_name')
        course_documentation = request.POST.get('course_documentation')
        course_images = request.FILES.get('course_images')
        course_pdf = request.FILES.get('course_pdf')
        course_video = request.FILES.get('course_video')
        course_quiz_id = request.POST.get('course_quiz')
        if course_quiz_id != "None":
            course_quiz = models.QuizCategory.objects.get(id=course_quiz_id,dev_id=request.user)
            print("------------------------------>",course_quiz)
        if models.Course_Module_Content.objects.filter(documentation_name=documentation_name,stage_id=stage_id, dev_id=request.user).exists():
            return render(request, "devapp/add-course-contents.html", {
                'exist_doc':"That documentation name already exists.",
                'module_stage_data':module_stage_data,
                'course_module_content_data':course_module_content_data,
                'quiz_category_data':quiz_category_data,
            })
        if course_quiz_id == "None":
            models.Course_Module_Content.objects.create(
                documentation_name=documentation_name,
                course_documentation=course_documentation,
                course_images=course_images,
                course_pdf=course_pdf,
                course_video=course_video,
                stage_id=module_stage_data,
                dev_id=request.user
            )
            return render(request,"devapp/add-course-contents.html",{
                'alert':"New course module docmentation created",
                'module_stage_data':module_stage_data,
                'course_module_content_data':course_module_content_data,
                'quiz_category_data':quiz_category_data,
            })
        else:
            models.Course_Module_Content.objects.create(
                documentation_name=documentation_name,
                course_documentation=course_documentation,
                course_images=course_images,
                course_pdf=course_pdf,
                course_video=course_video,
                course_quiz=course_quiz,    
                stage_id=module_stage_data,
                dev_id=request.user
            )
            return render(request,"devapp/add-course-contents.html",{
                'alert':"New course module docmentation created",
                'module_stage_data':module_stage_data,
                'course_module_content_data':course_module_content_data,
                'quiz_category_data':quiz_category_data,
            })
    return render(request,"devapp/add-course-contents.html",context=context)


def update_course_items(request, id):
    course_content_data = models.Course_Module_Content.objects.get(id=id)
    quiz_category_data = models.QuizCategory.objects.filter(is_course_quiz=True, dev_id=request.user)
    stage_id = course_content_data.stage_id.id

    # Ensure course_quiz is passed correctly
    course_quiz_id = course_content_data.course_quiz.id if course_content_data.course_quiz else None

    context = {
        'course_content_data': course_content_data,
        'quiz_category_data': quiz_category_data,
        'course_quiz': course_quiz_id,  # Pass only the ID for comparison
    }

    if request.method == "POST":
        documentation_name = request.POST.get('documentation_name')
        course_documentation = request.POST.get('course_documentation')
        course_images = request.FILES.get('course_images')
        course_pdf = request.FILES.get('course_pdf')
        course_video = request.FILES.get('course_video')
        course_quiz_id = request.POST.get('course_quiz')

        course_content_data.documentation_name = documentation_name
        course_content_data.course_documentation = course_documentation
        if course_images:
            course_content_data.course_images = course_images
        if course_pdf:
            course_content_data.course_pdf = course_pdf
        if course_video:
            course_content_data.course_video = course_video

        # Update course_quiz if selected
        if course_quiz_id and course_quiz_id != "None":
            course_content_data.course_quiz = models.QuizCategory.objects.get(id=course_quiz_id)
        else:
            course_content_data.course_quiz = None

        course_content_data.save()
        return redirect(reverse('add_course_items', args=[stage_id]))

    return render(request, "devapp/update-course-content.html", context)


def delete_course_items(request,id):
    course_module_content_data = models.Course_Module_Content.objects.get(id=id)
    stage_id = course_module_content_data.stage_id.id
    course_module_content_data.delete()
    return redirect(reverse('add_course_items', args=[stage_id]))

def detailedview_course_module_content(request,id):
    module_content_data = models.Course_Module_Content.objects.get(id=id,dev_id=request.user)
    course_quiz_id = module_content_data.course_quiz
    course_quiz_questions = models.QuizQuestions.objects.filter(quiz_category_id=course_quiz_id)
    context = {
        'module_content_data':module_content_data,
        'course_quiz_questions':course_quiz_questions,
    }
    return render(request,"devapp/course-module-content-review.html",context=context)



def add_certificate_details(request):
    certificate_data = None
    if models.Certificate_Details.objects.filter(dev_id=request.user).exists():
        certificate_data = models.Certificate_Details.objects.get(dev_id=request.user)
        print("----------------------------->", certificate_data)

    if request.method == "POST":
        company_logo = request.FILES.get("company_logo")
        signature_data = request.POST.get("dev_signature")
        format, imgstr = signature_data.split(';base64,') if signature_data else (None, None)
        if imgstr:
            ext = format.split('/')[-1] if format else 'png'
            signature_file = ContentFile(base64.b64decode(imgstr), name=f"signature_{uuid.uuid4()}.{ext}")
        else:
            signature_file = None
            
        certificate = models.Certificate_Details(
            company_logo=company_logo,
            dev_signature=signature_file,
            dev_id=request.user
        )
        certificate.save()

        return redirect("add_certificate_details")
    context = {
        'certificate_data': certificate_data
    }
    return render(request, "devapp/add-certificate-details.html", context=context)


def update_certificate_details(request,id):
    if request.method == "POST":
        company_logo = request.FILES.get("company_logo")
        signature_data = request.POST.get("dev_signature")

        format, imgstr = signature_data.split(';base64,') if signature_data else (None, None)
        if imgstr:
            ext = format.split('/')[-1] if format else 'png'
            signature_file = ContentFile(base64.b64decode(imgstr), name=f"signature_{uuid.uuid4()}.{ext}")
        else:
            signature_file = None

        certificate_detail_data = models.Certificate_Details.objects.get(id=id)
        certificate_detail_data.company_logo = company_logo
        certificate_detail_data.dev_signature = signature_file
        certificate_detail_data.save()
        return redirect(add_certificate_details)

    return render(request,"devapp/update-certificate-details.html")



def generate_digital_signature(student, course_id, certificate_detail_id):
    try:
        course_data = models.Online_Certification_Course.objects.get(id=course_id)
        student_data = User.objects.get(username=student)
        certificate_details_data = models.Certificate_Details.objects.get(id=certificate_detail_id)
    except models.Online_Certification_Course.DoesNotExist:
        return f"Course with ID {course_id} not found."
    except User.DoesNotExist:
        return f"Student with username {student} not found."
    except models.Certificate_Details.DoesNotExist:
        return f"Certificate Details with ID {certificate_detail_id} not found."
    print("---course_data--------------------------------->", course_data)
    print("---student_data--------------------------------->", student_data)
    print("---certificate_details_data--------------------------------->", certificate_details_data)
    issued_certificate = models.Issued_Certificate.objects.filter(student_id=student_data, course_id=course_data).first()

    if issued_certificate:
        print("Certificate already issued:")
        print(f"Digital Signature: {issued_certificate.digital_signature}")
        print(f"Certificate Details: {issued_certificate.certificate_details}")
        return issued_certificate

    length = 20
    digital_signature = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    issue_new_certificate = models.Issued_Certificate.objects.create(
        student_id=student_data,
        course_id=course_data,
        certificate_details=certificate_details_data,
        digital_signature=digital_signature
    )
    
    issue_new_certificate.save()
    print("----------------digital signature---------------", digital_signature)
    return digital_signature


def selected_student_table(request):
    dev_details = User.objects.get(username=request.user)
    query = request.GET.get('search', '') 
    selected_student_data = User.objects.filter(is_selected=True, company_name=dev_details.company_name)
    if query:
        selected_student_data = selected_student_data.filter(
            Q(username__icontains=query) | Q(course__icontains=query) | Q(institute_name__icontains=query)
        )
    paginator = Paginator(selected_student_data, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'selected_student_data': page_obj,
        'search_query': query
    }
    return render(request, "devapp/selected-student-table.html", context)

def unselect_student(request,id):
    student_data = User.objects.get(id=id)
    student_data.is_selected = False
    student_data.company_name = ""
    student_data.save()
    return redirect(selected_student_table)


def student_course_query_table(request):
    developer_user = request.user
    course_developer = models.Online_Certification_Course.objects.filter(dev_id=developer_user)
    queries_for_developer_courses = Student_Course_Query.objects.filter(course_name__in=course_developer)
    paginator = Paginator(queries_for_developer_courses, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'student_course_query_data':page_obj
    }
    return render(request,"devapp/student-course-query-table.html",context=context)

def delete_student_course_query(request,id):
    data = Student_Course_Query.objects.get(id=id)
    data.delete()
    return redirect(student_course_query_table)


def student_query_response(request,id):
    student_query_data = Student_Course_Query.objects.get(id=id)
    if request.method == "POST":
        response_content = request.POST.get('response_content')
        add_student_query_response = models.Response_Student_Query.objects.create(
            query_id = student_query_data,
            dev_id = request.user,
            response_content = response_content
        )
        add_student_query_response.save()
        student_query_data.query_status = True
        student_query_data.save()
        return redirect(student_course_query_table)
    context = {
        'student_query_data':student_query_data
    }
    return render(request,"devapp/student-query-response-form.html",context=context)


def dev_feedback(request):
    if request.method == "POST":
        rating = request.POST.get('rating')
        feedback_content = request.POST.get('feedback_content')
        add_new_feedback = Feedback.objects.create(
            user_id = request.user,
            rating = rating,
            feedback_content = feedback_content
        )
        add_new_feedback.save()
        return redirect(index)
    return render(request,"devapp/dev-feedback.html")


def delete_profile_image(request,id):
    data = User.objects.get(id=id)
    data.dev_img = None
    data.save()
    return redirect(dev_profile)