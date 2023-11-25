from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('customers/', views.customer_list, name='customer_list'),
    path('account/<int:customer_id>/', views.account_details, name='account_details'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('transaction-history/<int:customer_id>/', views.transaction_history, name='transaction_history'),
    path('make-deposit/<int:customer_id>/', views.make_deposit, name='make_deposit'),
    path('make-withdrawal/<int:customer_id>/', views.make_withdrawal, name='make_withdrawal'),
    path('make-transfer/<int:customer_id>/', views.make_transfer, name='make_transfer'),
]
