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
    path('student/registration/',views.registration,name="registration"),
    path('logout/',views.signout,name="logout"),
    path('forgot-password/',views.forgot_password,name="forgot_password"),
    path('verify-otp/',views.compare_otp,name="compare_otp"),
    path('reset-password/',views.reset_password,name="reset_password"),
    path('quiz-list/',views.quiz_list,name="quiz_list"),
    path('quiz/<int:id>/',views.quiz,name="quiz"),
    path('score-card/',views.score_card,name="score_card"),
    path('live-sessions/',views.live_sessions,name="live_sessions"),
    path('join-session/<int:id>/',views.join_session,name="join_session"),
    path('bookmark-session/<int:id>/',views.bookmark_session,name="bookmark_session"),
]
