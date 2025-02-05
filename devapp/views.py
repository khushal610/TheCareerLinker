from django.shortcuts import render,HttpResponse,redirect
from devapp import models
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
    # dev_name = request.session.get('dev_name')
    # dev_data = models.DevList.objects.get(username=dev_name)
    # current_dev_id = models.DevList.objects.get(id=dev_data.id)
    # context = {
    #     'dev_data':dev_data,
    #     'dev_id':current_dev_id.id,
    # }
    # if request.method == "POST":
    #     dev_form = forms.DevBioForm(request.POST,request.FILES)
    #     if dev_form.is_valid():
    #         dev_bio_obj = dev_form.save(commit=False)
    #         dev_bio_obj.dev_id = current_dev_id
    #         dev_bio_obj.save()
    #         return redirect(dev_profile)
    #     else:
    #         print(dev_form.errors)
    #         return HttpResponse("Errors")
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
                return redirect(dev_signIn)
            else:
                print(devSignForm.errors)
                return render(request,"devapp/signup.html",{'error':"Password Doesn't Match"})
    return render(request,"devapp/signup.html",{'role':User.DEVELOPER})

def dev_signOut(request):
    logout(request)
    return redirect(TCL_views.main_login)


def add_quiz_category(request):
    # if request.method == "POST":
    #     dev_name = request.session.get('dev_name')
    #     quiz_category_name = request.session.get('quiz_category_name')
    #     findUser = models.DevList.objects.get(username=dev_name)
    #     dev_id = findUser
    #     quiz_level = request.POST.get('quiz_level')
    #     if quiz_level == "None":
    #         return render(request,"devapp/add-quiz-category.html",{'quiz_undefine_error':"Please Select the quiz level"})
    #     quiz_cat_form = forms.QuizCategoryForm(request.POST)
    #     if quiz_cat_form.is_valid():
    #         quiz_cat_form_obj = quiz_cat_form.save(commit=False)
    #         quiz_cat_form_obj.dev_id = dev_id
    #         quiz_cat_form_obj.save()
    #         return redirect(add_questions)
    #     else:
    #         return render(request,"devapp/add-quiz-category.html",{'error':"Please Enter valid data"})
    return render(request,"devapp/add-quiz-category.html")


def add_questions(request):
    return render(request,'devapp/add-questions.html')

def add_options(request):
    return render(request,'devapp/add-options.html')