from django.urls import path
from devapp import views

urlpatterns = [
    path('dev-signup/',views.dev_signUp,name="dev_signUp"),
    path('dev-index/',views.index,name="devIndex"),
    path('dev-profile/',views.dev_profile,name="dev_profile"),
    path('edit-profile/<int:id>/',views.edit_profile,name="edit_profile"),
    path('dev-widget/',views.dev_widget,name="dev_widget"),
    path('dev-form/',views.dev_forms,name="dev_form"),
    path('dev-signout/',views.dev_signOut,name="dev_signOut"),
    path('dev-profile-bio-forms/',views.dev_profile_bio_forms,name="dev_profile_bio_forms"),
    path('add-quiz-category/',views.add_quiz_category,name="add_quiz_category"),
    path('update-quiz-category/<int:id>',views.update_quiz_category,name="update_quiz_category"),
    path('add-questions/',views.add_questions,name="add_questions"),
    path('delete-question/<int:id>/',views.delete_question,name="delete_question"),
    path('add-options/<int:id>/',views.add_options,name="add_options"),
    path('update-options/<int:id>/',views.update_options,name="update_options"),
    path('table/',views.table,name="table"),
]
