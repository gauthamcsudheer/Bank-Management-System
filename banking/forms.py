# banking/forms.py

from django import forms

class SignupForm(forms.Form):
    name = forms.CharField(label='Full Name', max_length=100)
    email = forms.EmailField(label='Email')
    username = forms.CharField(label='Username', max_length=100)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    photo = forms.ImageField(label='Profile Photo', required=False)

class LoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=100)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

class TransactionForm(forms.Form):
    amount = forms.DecimalField(label='Amount', min_value=0.01)
    transaction_type = forms.ChoiceField(label='Transaction Type', choices=[('deposit', 'Deposit'), ('withdraw', 'Withdraw')])