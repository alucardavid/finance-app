"""Defines URL patterns for Finance App"""

from django.urls import path

from . import views 

app_name = 'finance'

urlpatterns = [
    path("", views.index, name="index"),
    path("balances/", views.balances, name="balances"),
    path("balances/<int:balance_id>/", views.balance, name="balance"),
    path("new_balance/", views.new_balance, name="new_balance"),
]