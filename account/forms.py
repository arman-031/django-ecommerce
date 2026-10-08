from django.core import validators
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.password_validation import validate_password
from django import forms
from .models import User, Address


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""

    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="Password confirmation", widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ["phone", ]

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("رمزهای عبور یکسان نیستند.")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    disabled password hash display field.
    """

    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ["phone", "password", "is_active", "is_admin"]


class LoginForm(forms.Form):
    phone = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), validators=[validators.MaxLengthValidator(50)])
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class RegisterForm(forms.Form):
    phone = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), validators=[validators.MaxLengthValidator(50)])
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def clean_phone(self):
        phone = self.cleaned_data['phone'].strip()
        if len(phone) != 11 or not phone.isascii() or not phone.isdigit() or not phone.startswith('09'):
            raise ValidationError('شماره همراه باید ۱۱ رقم و با ۰۹ شروع شود.')
        if User.objects.filter(phone=phone).exists():
            raise ValidationError('این شماره همراه قبلاً ثبت شده است.')
        return phone

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get('password')
        password2 = cleaned_data.get('password2')

        if password and password2 and password != password2:
            raise ValidationError("رمزهای عبور یکسان نیستند.")

        if password:
            validate_password(password, User(phone=cleaned_data.get('phone', '')))
        return cleaned_data


class AddressCreationForm(forms.ModelForm):
    class Meta:
        model = Address
        exclude = ['user']
