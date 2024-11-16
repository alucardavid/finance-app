"""Defines URL patterns for Finance App"""

from django.urls import path

from . import views 

app_name = 'finance'

urlpatterns = [
    path("", views.index, name="index"),
    path("balances/", views.balances, name="balances"),
    path("edit-balance/<int:balance_id>/", views.edit_balance, name="edit_balance"),
    path("new-balance/", views.new_balance, name="new_balance"),
    path("variable-expenses/", views.variable_expenses, name="variable_expenses"),
    path("new-variable-expense/", views.new_variable_expense, name="new_variable_expense"),
    path("edit-variable-expense/<int:variable_expense_id>/", views.edit_variable_expense, name="edit_variable_expense"),
    path("monthly-expenses/", views.monthly_expenses, name="monthly_expenses"),
    path("new-monthly-expense/", views.new_monthly_expense, name="new_monthly_expense"),
    path("edit-monthly-balance/<int:monthly_expense_id>/", views.edit_monthly_expense, name="edit_monthly_expense"),
    path("import-monthly-expenses/", views.import_monthly_expenses, name="import_monthly_expenses"),
    path("incomings/", views.incomings, name="incomings"),
    path("new-incoming/", views.new_incoming, name="new_incoming"),
    path("edit-incoming/<int:incoming_id>/", views.edit_incoming, name="edit_incoming"),
    path("expense-categorys/", views.expense_categorys, name="expense_categorys"),
    path("new-expense-category/", views.new_expense_category, name="new_expense_category"),
    path("edit-expense-category/<int:category_id>/", views.edit_expense_category, name="edit_expense_category"),
]