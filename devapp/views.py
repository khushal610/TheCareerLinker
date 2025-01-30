from django.shortcuts import render,HttpResponse,redirect
from devapp import models,forms

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
    dev_name = request.session.get('dev_name')
    dev_data = models.DevList.objects.get(username=dev_name)
    current_dev_id = models.DevList.objects.get(id=dev_data.id)
    context = {
        'dev_data':dev_data,
        'dev_id':current_dev_id.id,
    }
    if request.method == "POST":
        dev_form = forms.DevBioForm(request.POST,request.FILES)
        if dev_form.is_valid():
            dev_bio_obj = dev_form.save(commit=False)
            dev_bio_obj.dev_id = current_dev_id
            dev_bio_obj.save()
            return redirect(dev_profile)
        else:
            print(dev_form.errors)
            return HttpResponse("Errors")
    return render(request,'devapp/dev-profile-bio.html',context=context)


def assessment(request):
    return render(request,'devapp/assessment.html')

def dev_profile(request):
    dev_name = request.session.get('dev_name')
    dev_data = models.DevList.objects.get(username=dev_name)
    dev_bio_data = models.DevBio.objects.get(dev_id=dev_data.id)
    context = {
        'dev_data':dev_data,
        'dev_bio_data':dev_bio_data,
    }
    return render(request,'devapp/dev-profile.html',context=context)

def dev_signIn(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            findUser = models.DevList.objects.get(email=email)
            if findUser.password != password:
                return render(request, "devapp/signin.html", {'auth_error': "Invalid password"})    
            if findUser.is_verified == False:
                print("--------------------------------------->", findUser.is_verified)
                return render(request, "devapp/signin.html", {'auth_error': "Wait until you are authorized"})
            request.session['dev_name'] = findUser.username
            return redirect(index)
        except:
            return render(request, "devapp/signin.html", {'auth_error': "User does not exist"})
    return render(request, "devapp/signin.html")

# ----------------------signup developer
def dev_signUp(request):
    if request.method == "POST":
        username = request.POST.get('username')
        company_name = request.POST.get('company_name')
        email = request.POST.get('email')
        contact = request.POST.get('contact')
        password = request.POST.get('password')
        try:
            ExistedUser = models.DevList.objects.get(username=username)
            return render(request,"devapp/signup.html",{'exist_dev_alert':"Username already exist"})
        except:
            devSignForm = forms.DevListForm(request.POST)
            if devSignForm.is_valid():
                dev_obj = devSignForm.save(commit=False)
                dev_obj.is_verified = False
                dev_obj.save()
                return redirect(dev_signIn)
            else:
                print(devSignForm.errors)
                return render(request,"devapp/signup.html",{'dev_signup_error':"Enter all valid data"})
    return render(request,"devapp/signup.html")

def dev_signOut(request):
    request.session.flush()
    return redirect(dev_signIn)