from django.urls import path
from adminapp import views

urlpatterns = [
    path('signout/',views.signout,name="signout"),
    path('index/',views.index,name="adminIndex"),
    path('forms/',views.formview,name="forms"),
    path('student-table/',views.studentTable,name="student-table"),
    path('chart/',views.chartview,name="chart"),
    path('widget/',views.widget,name="widget"),
    path('assessment/',views.assessment,name="assessment"),
    path('quiz-category-list-table/',views.quiz_category_list_table,name="quiz_category_list_table"),
    path('quiz-approve/<int:id>/',views.quiz_approve,name="quiz_approve"),
    path('quiz-disapprove/<int:id>/',views.quiz_disapprove,name="quiz_disapprove"),
    # path('quiz-review/<int:id>/',views.quiz_review,name="quiz_review"),
    path('delete-quiz-category/<int:id>/',views.delete_quiz_category,name="delete_quiz_category"),
    path('deleteUser/<int:id>/',views.deleteUser,name="deleteUser"),
    path('admin-add-form/',views.admin_add_form,name="admin-add-form"),
    path('dev-table/',views.dev_list_table,name="dev-table"),
    path('authorize-dev/<int:id>/',views.authorize_dev,name="authorize_dev"),
    path('unauthorize-dev/<int:id>/',views.unauthorize_dev,name="unauthorize_dev"),
    path('delete-dev/<int:id>/',views.deleteDev,name="deleteDev"),
]
