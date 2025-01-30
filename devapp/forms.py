from django import forms
from devapp import models

class DevListForm(forms.ModelForm):
    class Meta:
        model = models.DevList
        exclude = ['is_verified']
        # fields = "__all__"


class DevBioForm(forms.ModelForm):
    class Meta:
        model = models.DevBio
        exclude = ['dev_id']
        # fields = "__all__"