from django.urls import path
from studentapp import views

urlpatterns = [
    path('',views.home,name="index"),
    path('about/',views.about,name="about"),
    path('contact/',views.contact,name="contact"),
    path('trainers/',views.trainers,name="trainers"),
    path('pricing/',views.pricing,name="pricing"),
    
    path('courses/',views.courses,name="courses"),
    path('course-details/<int:id>/',views.course_details,name="course_details"),
    path('course-enrollment/<int:id>/',views.course_enrollment,name="course_enrollment"),

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
    path('<int:course_data_id>/course-document-content/<int:id>/',views.course_document_content,name="course_document_content"),
    path('<int:course_data_id>/course-final-assessment-result/<int:id>/',views.course_final_assessment_result,name="course_final_assessment_result"),
    path('<int:course_data_id>/next_documentation/<int:id>/',views.next_documentation,name="next_documentation"),
    path('<int:course_data_id>/previous_documentation/<int:id>/',views.previous_documentation,name="previous_documentation"),
    path('view-certificate/<int:course_data_id>',views.view_certificate,name="view_certificate"),
    path('generate-certificate/<int:course_data_id>/', views.generate_certificate_pdf, name='generate_certificate_pdf'),
    path('chat/',views.chat,name="chat"),
]
