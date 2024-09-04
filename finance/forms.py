from django.forms import TextInput, ModelForm, ChoiceField, Select
from .models import Balance

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
        