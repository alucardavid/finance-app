from django.forms import ModelForm, TextInput, PasswordInput
from django.contrib.auth.models import User

class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password']
        widgets = {
            'username': TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'password': PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
        }