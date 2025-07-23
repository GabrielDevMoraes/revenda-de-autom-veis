# cars/forms.py

from django import forms
from .models import LeadInteraction

class LeadInteractionForm(forms.ModelForm):
    class Meta:
        model = LeadInteraction
        fields = ['status', 'observacoes'] # Campos que o vendedor poderá editar
        widgets = {
            'observacoes': forms.Textarea(attrs={'rows': 3}),
        }

