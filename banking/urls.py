# banking/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('customers/', views.customer_list, name='customer_list'),
    path('account/<int:customer_id>/', views.account_details, name='account_details'),

    path('signup/', views.signup, name='signup'),
]
