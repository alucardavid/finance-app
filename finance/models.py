from django.db import models

class Balances(models.Model):
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
