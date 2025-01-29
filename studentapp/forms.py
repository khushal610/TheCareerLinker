from django import forms
from studentapp import models

class RegistrationForm(forms.ModelForm):
    class Meta:
        model = models.Registration
        fields = "__all__"