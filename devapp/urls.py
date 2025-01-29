from django.urls import path
from devapp import views

urlpatterns = [
    path('',views.dev_signIn,name="dev_signIn"),
    path('dev-signup/',views.dev_signUp,name="dev_signUp"),
    path('dev-index/',views.index,name="devIndex"),
    path('dev-widget/',views.dev_widget,name="dev_widget"),
    path('dev-form/',views.dev_forms,name="dev_form"),
    path('assessment/',views.assessment,name="assessment"),
]
