from django.urls import path
from devapp import views

urlpatterns = [
    path('dev-signup/',views.dev_signUp,name="dev_signUp"),
    path('dev-index/',views.index,name="devIndex"),
    path('dev-profile/',views.dev_profile,name="dev_profile"),
    path('dev-widget/',views.dev_widget,name="dev_widget"),
    path('dev-form/',views.dev_forms,name="dev_form"),
    path('dev-signout/',views.dev_signOut,name="dev_signOut"),
    path('dev-profile-bio-forms/',views.dev_profile_bio_forms,name="dev_profile_bio_forms"),
    path('add-quiz-category/',views.add_quiz_category,name="add_quiz_category"),
    path('add-questions/',views.add_questions,name="add_questions"),
    path('add-options/',views.add_options,name="add_options"),
]
