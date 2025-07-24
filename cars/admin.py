# cars/admin.py

from django.contrib import admin
from .models import Car, Customer, Sale, Vistoria, Lavagem, LeadInteraction, VistoriaPattern, VistoriaItemPattern, VistoriaActualItem # Importe os novos modelos

# Inlines para VistoriaPattern (itens dentro do padrão)
class VistoriaItemPatternInline(admin.TabularInline): # Ou admin.StackedInline
    model = VistoriaItemPattern
    extra = 1 # Quantos formulários em branco para adicionar itens
    fields = ['description', 'is_mandatory', 'requires_photo', 'order']

@admin.register(VistoriaPattern) # NOVO REGISTRO
class VistoriaPatternAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    inlines = [VistoriaItemPatternInline] # Permite gerenciar itens diretamente aqui

# Inline para Vistoria (itens reais de vistoria)
class VistoriaActualItemInline(admin.TabularInline):
    model = VistoriaActualItem
    extra = 0 # Não adiciona formulários em branco por padrão
    fields = ['item_pattern', 'is_ok', 'description_result', 'photo']
    readonly_fields = ['item_pattern'] # item_pattern não deve ser alterado aqui
    can_delete = False # Geralmente não se deleta itens de vistoria real individualmente
    # Se você quiser que o campo 'item_pattern' apareça como um dropdown completo para seleção,
    # você precisaria usar admin.StackedInline com fieldsets ou um ModelForm customizado
    # para a vistoria, mas TabularInline é mais compacto.
    
    # Customização para exibir itens do padrão selecionado
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Filtra para não mostrar todos os itens de vistoria, mas apenas os do padrão selecionado
        # Isso é mais complexo em um Inline padrão, geralmente exige customização do formset
        return qs 

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('marca', 'modelo', 'ano', 'preco', 'status_veiculo', 'vendedor', 'disponivel', 'data_cadastro')
    list_filter = ('marca', 'disponivel', 'transmissao', 'combustivel', 'status_veiculo', 'vendedor', 'ano')
    search_fields = ('marca', 'modelo', 'descricao')
    ordering = ('-data_cadastro',)

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('nome_completo', 'email', 'telefone', 'whatsapp_number')
    search_fields = ('nome_completo', 'email', 'telefone', 'whatsapp_number')

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('carro', 'cliente', 'preco_final', 'data_venda')
    list_filter = ('carro', 'cliente', 'data_venda')
    search_fields = ('carro__modelo', 'cliente__nome_completo')
    date_hierarchy = 'data_venda'

@admin.register(Vistoria) # ATUALIZADO: para usar o Inline
class VistoriaAdmin(admin.ModelAdmin):
    list_display = ('carro', 'pattern', 'data_vistoria', 'resultado', 'vistoriador', 'data_registro') # Adicionado 'pattern'
    list_filter = ('resultado', 'data_vistoria', 'vistoriador', 'pattern') # Adicionado 'pattern'
    search_fields = ('carro__modelo', 'observacoes_gerais')
    date_hierarchy = 'data_vistoria'
    inlines = [VistoriaActualItemInline] # Permite gerenciar itens reais da vistoria
    fieldsets = ( # Personaliza a ordem dos campos no formulário de Vistoria
        (None, {
            'fields': ('carro', 'pattern', 'data_vistoria', 'resultado', 'observacoes_gerais', 'vistoriador')
        }),
    )

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

