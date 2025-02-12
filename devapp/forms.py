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