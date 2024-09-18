from django.forms import TextInput, ModelForm, ChoiceField, Select, ModelChoiceField, DateInput, NumberInput
from .models import Balance, VariableExpense, MonthlyExpense
from . import api   

class BalanceForm(ModelForm):
    class Meta:
        model = Balance
        fields = ['description', 'value', 'show']
        labels = {
            'value': 'Valor'
        }
        widgets = {
            'description': TextInput(attrs={'class': 'form-control'}),
            'value': TextInput(attrs={'class': 'form-control', 'onkeydown': 'checkNumberKey(event, this)'}),
            'show': Select(attrs={'class': 'form-control'}, choices=(("S", "Sim"), ("N", "No"))),
        }
    
class VariableExpenseForm(ModelForm):
    class Meta:
        model = VariableExpense
        fields = ['place', 'description', 'date', 'amount', 'type', 'form_of_payment']
        widgets = {
            'place': TextInput(attrs={'class': 'form-control'}),
            'description': TextInput(attrs={'class': 'form-control'}),
            'form_of_payment': Select(attrs={'class': 'form-control'}),
            'type': Select(attrs={'class': 'form-control'}, choices=(("", "Selecione"),("Despesa", "Despesa"), ("Receita", "Receita"))),
            'amount': TextInput(attrs={'class': 'form-control', 'onkeydown': 'checkNumberKey(event, this)', 'onload': 'console.log("onload")'}),
            'date': DateInput(attrs={'class': 'form-control', 'type': 'date'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['form_of_payment'].choices =[["", "Selecione"]] + api.get_all_form_of_payments(order_by="form_of_payments.description asc")["form_of_payments"]

class MonthlyExpenseForm(ModelForm):
    class Meta:
        model = MonthlyExpense
        fields = ['date', 'place', 'description', 'form_of_payment', 'amount', 'total_plots', 'current_plot', 'due_date']
        widgets = {
            'place': TextInput(attrs={'class': 'form-control'}),
            'description': TextInput(attrs={'class': 'form-control'}),
            'form_of_payment': Select(attrs={'class': 'form-control'}),
            'amount': TextInput(attrs={'class': 'form-control', 'onkeydown': 'checkNumberKey(event, this)', 'onload': 'console.log("onload")'}),
            'date': DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'total_plots': NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }