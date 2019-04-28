from django import forms


class BaseRequestForm(forms.Form):
    main_str = forms.CharField(label='Request', max_length=100)
