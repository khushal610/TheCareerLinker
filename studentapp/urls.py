from django.urls import path
from studentapp import views

urlpatterns = [
    path('',views.home,name="index"),
    path('about/',views.about,name="about"),
    path('contact/',views.contact,name="contact"),
    path('trainers/',views.trainers,name="trainers"),
    path('pricing/',views.pricing,name="pricing"),
    path('courses/',views.courses,name="courses"),
    path('course-details/',views.courseDetails,name="course-details"),
    path('profile/',views.profile,name="profile"),
    path('login/',views.loginview,name="login"),
    path('registration/',views.registration,name="registration"),
    path('logout/',views.signout,name="logout"),
]


# from django-documentation
# from django.contrib.auth import views as auth_views
# path('login/',auth_views.LoginView.as_view(),name="login"),