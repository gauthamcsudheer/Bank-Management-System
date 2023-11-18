# banking/views.py

from django.shortcuts import render, redirect, get_object_or_404
from .forms import SignupForm, TransactionForm
from .models import Customer, Account, Transaction

def customer_list(request):
    customers = Customer.objects.all()
    return render(request, 'customer_list.html', {'customers': customers})

def account_details(request, customer_id):
    customer = get_object_or_404(Customer, pk=customer_id)
    account = get_object_or_404(Account, customer=customer)
    transactions = Transaction.objects.filter(account=account)

    if request.method == 'POST':
        transaction_form = TransactionForm(request.POST)
        if transaction_form.is_valid():
            amount = transaction_form.cleaned_data['amount']
            transaction_type = transaction_form.cleaned_data['transaction_type']

            if transaction_type == 'deposit':
                account.balance += amount
            elif transaction_type == 'withdraw':
                if amount <= account.balance:
                    account.balance -= amount
                else:
                    # Handle insufficient funds error
                    return render(request, 'account_details.html', {'customer': customer, 'account': account, 'transactions': transactions, 'error': 'Insufficient funds'})

            # Save the transaction
            Transaction.objects.create(account=account, amount=amount, transaction_type=transaction_type)
            
            # Update the account balance
            account.save()

            # Redirect to the account details page
            return redirect('account_details', customer_id=customer.id)
    else:
        transaction_form = TransactionForm()

    return render(request, 'account_details.html', {'customer': customer, 'account': account, 'transactions': transactions, 'transaction_form': transaction_form})

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            # Create a new customer and account
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']

            # Create a new customer
            customer = Customer.objects.create(name=name, email=email)

            # Create a corresponding account for the customer
            Account.objects.create(customer=customer, balance=0.0)

            # Redirect to the customer list or any other page
            return redirect('customer_list')
    else:
        form = SignupForm()

    return render(request, 'signup.html', {'form': form})