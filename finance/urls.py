from django.urls import path

from .views import variable_expenses, default, balances, monthly_expenses, incomings, expense_categorys

app_name = 'finance'

urlpatterns = [
    path("", default.index, name="index"),
    path("balances/", balances.index, name="balances"),
    path("edit-balance/<int:balance_id>/", balances.edit_balance, name="edit_balance"),
    path("new-balance/", balances.new_balance, name="new_balance"),
    path("sync-balances/", balances.sync_balances, name="sync_balances"),
    path("variable-expenses/", variable_expenses.index, name="variable_expenses"),
    path("new-variable-expense/", variable_expenses.new_variable_expense, name="new_variable_expense"),
    path("edit-variable-expense/<int:variable_expense_id>/", variable_expenses.edit_variable_expense, name="edit_variable_expense"),
    path("sync-variable-expenses/", variable_expenses.sync_variable_expenses, name="sync_variable_expenses"),
    path("import-variable-expenses-nubank/", variable_expenses.import_variable_expenses_nubank, name="import_variable_expenses_nubank"),
    path("monthly-expenses/", monthly_expenses.index, name="monthly_expenses"),
    path("new-monthly-expense/", monthly_expenses.new_monthly_expense, name="new_monthly_expense"),
    path("edit-monthly-balance/<int:monthly_expense_id>/", monthly_expenses.edit_monthly_expense, name="edit_monthly_expense"),
    path("import-monthly-expenses/", monthly_expenses.import_monthly_expenses, name="import_monthly_expenses"),
    path("incomings/", incomings.index, name="incomings"),
    path("new-incoming/", incomings.new_incoming, name="new_incoming"),
    path("edit-incoming/<int:incoming_id>/", incomings.edit_incoming, name="edit_incoming"),
    path("expense-categorys/", expense_categorys.index, name="expense_categorys"),
    path("new-expense-category/", expense_categorys.new_expense_category, name="new_expense_category"),
    path("edit-expense-category/<int:category_id>/", expense_categorys.edit_expense_category, name="edit_expense_category"),
    path("import-fatura-santander/", default.import_fatura_santander, name="import_fatura_santander"),
]