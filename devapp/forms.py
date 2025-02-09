from django import forms
from devapp import models

class QuizCategoryForm(forms.ModelForm):
    class Meta:
        model = models.QuizCategory
        fields = "__all__"
        exclude = ['dev_id']