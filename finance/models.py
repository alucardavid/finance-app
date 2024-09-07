from django.db import models

class Balance(models.Model):
    id = models.BigAutoField(primary_key=True)
    description = models.CharField(max_length=50)
    value = models.DecimalField(max_digits=15, decimal_places=2)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)
    user_id = models.IntegerField()
    show = models.CharField(max_length=1)

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


    