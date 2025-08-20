from django.db import models

class Balance(models.Model):
    id = models.BigAutoField(primary_key=True)
    description = models.CharField(max_length=50)
    value = models.DecimalField(max_digits=15, decimal_places=2)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)
    user_id = models.IntegerField()
    show = models.CharField(max_length=1)
    status_open_finance = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'balances'


class FormOfPayment(models.Model):
    id = models.BigAutoField(primary_key=True)
    description = models.CharField(max_length=100)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)
    balance = models.ForeignKey(Balance, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'form_of_payments'
        ordering = ['description']

    def __str__(self):
        return self.description

class VariableExpense(models.Model):
    id = models.BigAutoField(primary_key=True)
    date = models.DateTimeField()
    description = models.CharField(max_length=200)
    type = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)
    form_of_payment = models.ForeignKey(FormOfPayment, models.DO_NOTHING)
    user_id = models.IntegerField(blank=True, null=True)
    place = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'variable_expenses'

class ExpenseCategory(models.Model):
    description = models.CharField(max_length=50)
    show = models.CharField(max_length=1)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'expense_categorys'

class MonthlyExpense(models.Model):

    id = models.BigAutoField(primary_key=True)
    place = models.CharField(max_length=50, blank=True, null=True)
    description = models.CharField(max_length=50, blank=True, null=True)
    date = models.DateTimeField()
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    total_plots = models.IntegerField(blank=True, null=True)
    current_plot = models.IntegerField(blank=True, null=True)
    due_date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)
    expense_category = models.ForeignKey(ExpenseCategory, models.DO_NOTHING, blank=True, null=True)
    form_of_payment = models.ForeignKey(FormOfPayment, models.DO_NOTHING, blank=True, null=True)
    user_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'monthly_expenses'

class Incoming(models.Model):
    description = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    source = models.CharField(max_length=50)
    date = models.DateTimeField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'incomings'
    
