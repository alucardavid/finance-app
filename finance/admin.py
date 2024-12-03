from django.contrib import admin
from finance.models import Balance

class BalancesAdmin(admin.ModelAdmin):
    pass    

admin.site.register(Balance, BalancesAdmin)