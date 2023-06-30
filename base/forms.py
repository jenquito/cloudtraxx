from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import Room, User

class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['name','username', 'email', 'password1', 'password2']

class RoomForm(ModelForm): #inherit from Model Form
    class Meta:
        model = Room       #specifies the model we want to create a form for
        fields = '__all__' #specifies the field
        exclude = ['host', 'participants']

class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['avatar','name','username','email','bio']