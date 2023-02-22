from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms


# Reordering Form and View


class PositionForm(forms.Form):
    position = forms.CharField()

class SignUpForm(UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control'}))

    class Meta:
        model = User
        fields = ('username','email','password1' ,'password2')


    def __init__(self , *args , **kwargs):
        super(SignUpForm,self).__init__(*args , **kwargs)
        self.fields['email'].widget.attrs['class'] = 'form-control'