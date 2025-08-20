from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.utils.formats import localize
from django import forms
from django.contrib import messages
from finance.open_finance import accounts, auth, transactions
from .forms import BalanceForm, VariableExpenseForm, MonthlyExpenseForm, IncomingForm, ExpenseCategoryForm
from .models import MonthlyExpense
from . import api
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from tabula import read_pdf
from setup.settings import BASE_DIR
from .finance_api import variable_expenses as api_variable_expenses
import sys, csv, requests
import os
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger('finance')


       


