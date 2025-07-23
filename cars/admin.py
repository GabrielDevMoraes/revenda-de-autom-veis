# cars/admin.py

from django.contrib import admin
from .models import Car, Customer, Sale, Vistoria, Lavagem, LeadInteraction

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('marca', 'modelo', 'ano', 'preco', 'status_veiculo', 'vendedor', 'disponivel', 'data_cadastro')
    list_filter = ('marca', 'disponivel', 'transmissao', 'combustivel', 'status_veiculo', 'vendedor', 'ano')
    search_fields = ('marca', 'modelo', 'descricao')
    ordering = ('-data_cadastro',)

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('nome_completo', 'email', 'telefone', 'whatsapp_number') # Adicionado 'whatsapp_number'
    search_fields = ('nome_completo', 'email', 'telefone', 'whatsapp_number') # Adicionado 'whatsapp_number'

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('carro', 'cliente', 'preco_final', 'data_venda')
    list_filter = ('carro', 'cliente', 'data_venda')
    search_fields = ('carro__modelo', 'cliente__nome_completo')
    date_hierarchy = 'data_venda'

@admin.register(Vistoria)
class VistoriaAdmin(admin.ModelAdmin):
    list_display = ('carro', 'data_vistoria', 'resultado', 'vistoriador', 'data_registro')
    list_filter = ('resultado', 'data_vistoria', 'vistoriador')
    search_fields = ('carro__modelo', 'observacoes')
    date_hierarchy = 'data_vistoria'

@admin.register(Lavagem)
class LavagemAdmin(admin.ModelAdmin):
    list_display = ('carro', 'data_lavagem', 'tipo_lavagem', 'custo', 'responsavel', 'data_registro')
    list_filter = ('tipo_lavagem', 'data_lavagem', 'responsavel')
    search_fields = ('carro__modelo', 'observacoes')
    date_hierarchy = 'data_lavagem'

@admin.register(LeadInteraction)
class LeadInteractionAdmin(admin.ModelAdmin):
    list_display = ('carro', 'cliente', 'vendedor', 'status', 'ultima_atualizacao', 'data_interacao')
    list_filter = ('status', 'vendedor', 'data_interacao', 'ultima_atualizacao')
    search_fields = ('carro__modelo', 'cliente__nome_completo', 'vendedor__username', 'observacoes')
    date_hierarchy = 'data_interacao'
    raw_id_fields = ('carro', 'cliente', 'vendedor')

