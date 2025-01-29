from django import forms
from devapp import models

class DevListForm(forms.ModelForm):
    class Meta:
        model = models.DevList
        exclude = ['is_verified']
        # fields = "__all__"