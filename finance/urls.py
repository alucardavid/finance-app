"""Defines URL patterns for Finance App"""

from django.urls import path

from . import views 

app_name = 'finance'

urlpatterns = [
    path("", views.index, name="index"),
    path("balances/", views.balances, name="balances"),
    path("balances/<int:balance_id>/", views.balance, name="balance"),
    path("new-balance/", views.new_balance, name="new_balance"),
    path("variable-expenses/", views.variable_expenses, name="variable_expenses"),
    path("new-variable-expense/", views.new_variable_expense, name="new_variable_expense"),
]