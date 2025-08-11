from django import forms
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

class URLForm(forms.Form):
    url = forms.URLField(
        max_length=500,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter URL to scrape (e.g., https://example.com)',
            'required': True
        }),
        label='Website URL'
    )

    def clean_url(self):
        url = self.cleaned_data['url']
        validator = URLValidator()
        try:
            validator(url)
        except ValidationError:
            raise forms.ValidationError("Please enter a valid URL")
        return url