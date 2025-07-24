# cars/forms.py

from django import forms
from .models import LeadInteraction, Vistoria, Lavagem, Car # Importe Car

class LeadInteractionForm(forms.ModelForm):
    class Meta:
        model = LeadInteraction
        fields = ['status', 'observacoes']
        widgets = {
            'observacoes': forms.Textarea(attrs={'rows': 3}),
        }

class VistoriaForm(forms.ModelForm):
    class Meta:
        model = Vistoria
        fields = ['carro', 'data_vistoria', 'resultado', 'observacoes', 'vistoriador']
        widgets = {
            'data_vistoria': forms.DateInput(attrs={'type': 'date'}),
            'observacoes': forms.Textarea(attrs={'rows': 3}),
        }

class LavagemForm(forms.ModelForm):
    class Meta:
        model = Lavagem
        fields = ['carro', 'data_lavagem', 'tipo_lavagem', 'custo', 'observacoes', 'responsavel']
        widgets = {
            'data_lavagem': forms.DateInput(attrs={'type': 'date'}),
            'observacoes': forms.Textarea(attrs={'rows': 3}),
        }

class CarForm(forms.ModelForm): # NOVO FORMULÁRIO PARA CARROS
    class Meta:
        model = Car
        fields = ['marca', 'modelo', 'ano', 'preco', 'lugares', 'transmissao', 
                  'combustivel', 'quilometragem', 'descricao', 'imagem', 
                  'disponivel', 'status_veiculo', 'vendedor']
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 3}),
        }
