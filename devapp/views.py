from django.shortcuts import render,HttpResponse,redirect
from devapp import models,forms
from studentapp.models import User
from TheCareerLinker import views as TCL_views
from django.contrib.auth import logout

# Create your views here.
def index(request):
    dev_name = request.session.get('dev_name')
    context = {'dev_name':dev_name}
    return render(request,'devapp/index.html',context=context)

def dev_widget(request):
    return render(request,'devapp/widget.html')

def dev_forms(request):
    return render(request,'devapp/form.html')


def dev_profile_bio_forms(request):
    return render(request,'devapp/dev-profile-bio.html')


def dev_profile(request):
    return render(request,'devapp/dev-profile.html')


# ----------------------signup developer
def dev_signUp(request):
    if request.method == "POST":
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
    context = {'data':data}
    if request.method == "POST":
        quiz_question = request.POST.get('quiz_question')
        quiz_category_id = request.POST.get('quiz_category_id')
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
            form_question_obj.save()
            return redirect(add_questions)
        else:
            print(form_question.errors)
    return render(request,'devapp/add-questions.html',context=context)



def add_options(request,id):
    questions = models.QuizQuestions.objects.filter(quiz_category_id=id)
    options = models.QuizOptions.objects.all()
    # print(questions)
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
    context = {
        'data':questions,
        'options':options
        }
    return render(request,'devapp/add-options.html',context=context)


def update_options(request,id):
    question_data = models.QuizQuestions.objects.get(id=id)
    options = models.QuizOptions.objects.get(question_id=question_data)
    if request.method == "POST":
        quiz_question = request.POST.get('quiz_question')
        option_1 = request.POST.get('option_1')
        option_2 = request.POST.get('option_2')
        option_3 = request.POST.get('option_3')
        option_4 = request.POST.get('option_4')
        print(quiz_question)
        question_data.quiz_question = quiz_question
        question_data.save()
        options.option_1 = option_1
        options.option_2 = option_2
        options.option_3 = option_3
        options.option_4 = option_4
        options.save()
        return redirect(add_questions)
    context = {
        'data':question_data,
        'options':options
    }
    return render(request,"devapp/update-options.html",context=context)


def delete_question(request,id):
    question_data = models.QuizQuestions.objects.get(id=id)
    question_data.delete()
    return redirect(add_questions)



def edit_profile(request,id):
    dev_data = User.objects.get(id=id)
    context = { 
        'dev_data':dev_data,
    }
    return render(request,"devapp/update-profile.html",context=context)

def table(request):
    data = models.QuizCategory.objects.filter(dev_id=request.user)
    context = {'data': data}
    return render(request, "devapp/table.html", context=context)


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
        return redirect(table)
    return render(request,"devapp/update-quiz-category.html",context=context)

# def