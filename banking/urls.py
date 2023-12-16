from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

from django.contrib.auth import views as auth_views

urlpatterns = [
    path('account/<int:customer_id>/', views.account_details, name='account_details'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('transaction-history/<int:customer_id>/', views.transaction_history, name='transaction_history'),
    path('make-deposit/<int:customer_id>/', views.make_deposit, name='make_deposit'),
    path('make-withdrawal/<int:customer_id>/', views.make_withdrawal, name='make_withdrawal'),
    path('make-transfer/<int:customer_id>/', views.make_transfer, name='make_transfer'),

    path('manager-login/', views.manager_login, name='manager_login'),
    path('manager-signup/', views.manager_signup, name='manager_signup'),
     path('manager_logout/', auth_views.LogoutView.as_view(next_page='manager_login'), name='manager_logout'),
    path('manager-dashboard/', views.manager_dashboard, name='manager_dashboard'),
    path('customer-details/<int:customer_id>/', views.customer_details, name='customer_details'),
]
