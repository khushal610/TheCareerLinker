from django import forms
from devapp import models

class QuizCategoryForm(forms.ModelForm):
    class Meta:
        model = models.QuizCategory
        fields = "__all__"
        exclude = ['dev_id']


class QuizQuestionForm(forms.ModelForm):
    class Meta:
        model = models.QuizQuestions
        exclude = ['quiz_category_id','is_option_added']
        # fields = "__all__"


class QuizOptionsForm(forms.ModelForm):
    class Meta:
        model = models.QuizOptions
        exclude = ['question_id']
        # fields = "__all__"


class CourseForm(forms.ModelForm):
    class Meta:
        model = models.Online_Certification_Course
        fields = ['course_name','course_duration','course_type','course_charges']
        exclude = ['dev_id']