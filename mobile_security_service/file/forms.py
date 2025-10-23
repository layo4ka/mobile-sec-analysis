from django import forms
from .models import UploadFile

class UploadFileForm(forms.ModelForm):
    class Meta:
        model = UploadFile
        fields = ('file', 'results','status',)
    def clean_file(self):
        f = self.cleaned_data['file']
        name = f.name.lower()
        if not (name.endswith('.apk') or name.endswith('.ipa')):
            raise forms.ValidationError("Только .apk или .ipa")
        return f
        