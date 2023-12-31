# banking/forms.py

from django import forms

from django.core.exceptions import ValidationError

class SignupForm(forms.Form):
    name = forms.CharField(label='Full Name', max_length=100)
    email = forms.EmailField(label='Email')
    phone_number = forms.CharField(label='Phone Number', max_length=15)
    username = forms.CharField(label='Username', max_length=100)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    confirm_password = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)
    photo = forms.ImageField(label='Profile Photo', required=False)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        phone_number = cleaned_data.get("phone_number")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match. Please enter matching passwords.")

        # Add any other form-level validation logic here

        # Validate the phone number
        if phone_number is not None:
            # Add phone number validation logic here
            pass

        return cleaned_data
        

class LoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=100)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

class DepositForm(forms.Form):
    amount = forms.DecimalField(label='Amount', min_value=0.01)

class WithdrawalForm(forms.Form):
    amount = forms.DecimalField(label='Amount', min_value=0.01)

    def clean_amount(self):
        amount = self.cleaned_data['amount']

        # Access the customer from the form's initial data
        customer = self.initial.get('customer')

        if customer:
            account = customer.account

            if amount > account.balance:
                raise ValidationError("Insufficient funds to make the withdrawal.")

        return amount

class TransferForm(forms.Form):
    recipient_account_number = forms.IntegerField(label='Recipient Account Number')
    amount = forms.DecimalField(label='Amount', min_value=0.01)



class ManagerSignupForm(forms.Form):
    managerid = forms.CharField(label='Manager ID', max_length=8)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    confirm_password = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match. Please enter matching passwords.")

        return cleaned_data