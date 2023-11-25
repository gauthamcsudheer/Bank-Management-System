# banking/forms.py

from django import forms

class SignupForm(forms.Form):
    name = forms.CharField(label='Full Name', max_length=100)
    email = forms.EmailField(label='Email')
    username = forms.CharField(label='Username', max_length=100)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    confirm_password = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)
    photo = forms.ImageField(label='Profile Photo', required=False)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match. Please enter matching passwords.")

class LoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=100)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

class DepositForm(forms.Form):
    amount = forms.DecimalField(label='Amount', min_value=0.01)

class WithdrawalForm(forms.Form):
    amount = forms.DecimalField(label='Amount', min_value=0.01)

class TransferForm(forms.Form):
    recipient_username = forms.CharField(label='Recipient Username', max_length=100)
    amount = forms.DecimalField(label='Amount', min_value=0.01)