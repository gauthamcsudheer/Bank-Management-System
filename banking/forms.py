# banking/forms.py

from django import forms

class SignupForm(forms.Form):
    name = forms.CharField(label='Full Name', max_length=100)
    email = forms.EmailField(label='Email')

class TransactionForm(forms.Form):
    amount = forms.DecimalField(label='Amount', min_value=0.01)
    transaction_type = forms.ChoiceField(label='Transaction Type', choices=[('deposit', 'Deposit'), ('withdraw', 'Withdraw')])