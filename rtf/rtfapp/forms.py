from django import forms
from .models import User, UserProfile, TrailSegment

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

class UserEditForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('username', 'email')

class UserProfileForm(forms.ModelForm):

    class Meta:
        model = UserProfile
        fields = ('phone_number',)

class TrailAnnotationForm(forms.ModelForm):

    class Meta: 
        model = TrailSegment
        fields = ('name', 'description', 'difficulty', 'trail_status', 'current_conditions')