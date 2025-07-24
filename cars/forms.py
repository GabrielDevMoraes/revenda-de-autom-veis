# cars/forms.py

from django import forms
from .models import LeadInteraction, Vistoria, Lavagem, Car, VistoriaPattern, VistoriaItemPattern, VistoriaActualItem # Importe VistoriaActualItem

class LeadInteractionForm(forms.ModelForm):
    class Meta:
        model = LeadInteraction
        fields = ['status', 'observacoes']
        widgets = {
            'observacoes': forms.Textarea(attrs={'rows': 3}),
        }

class VistoriaForm(forms.ModelForm):
    # O campo pattern será selecionado no formulário
    # Se você quiser popular os itens do pattern dinamicamente no form web customizado,
    # isso exigirá JavaScript no template e lógica na view.
    class Meta:
        model = Vistoria
        fields = ['carro', 'pattern', 'data_vistoria', 'resultado', 'observacoes_gerais', 'vistoriador']
        widgets = {
            'data_vistoria': forms.DateInput(attrs={'type': 'date'}),
            'observacoes_gerais': forms.Textarea(attrs={'rows': 3}),
        }

class VistoriaActualItemForm(forms.ModelForm): # NOVO FORMULÁRIO
    class Meta:
        model = VistoriaActualItem
        fields = ['is_ok', 'description_result', 'photo'] # item_pattern será definido na view
        widgets = {
            'description_result': forms.Textarea(attrs={'rows': 2}),
        }

class LavagemForm(forms.ModelForm):
    class Meta:
        model = Lavagem
        fields = ['carro', 'data_lavagem', 'tipo_lavagem', 'custo', 'observacoes', 'responsavel']
        widgets = {
            'data_lavagem': forms.DateInput(attrs={'type': 'date'}),
            'observacoes': forms.Textarea(attrs={'rows': 3}),
        }

class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ['marca', 'modelo', 'ano', 'preco', 'lugares', 'transmissao', 
                  'combustivel', 'quilometragem', 'descricao', 'imagem', 
                  'disponivel', 'status_veiculo', 'vendedor']
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 3}),
        }
