from django import forms
from .models import Order
from django.contrib.auth.models import User
from .models import Profile

class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['name', 'phone', 'address']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # получим пользователя, если передали
        super().__init__(*args, **kwargs)

        # Стилизация Bootstrap
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

        # Автозаполнение
        if user and user.is_authenticated:
            self.fields['name'].initial = user.username
            self.fields['phone'].initial = getattr(user, 'profile.phone', '') if hasattr(user, 'profile') else ''


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }