# cars/models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone 

class Car(models.Model):
    STATUS_INTERACTION_CHOICES = [
        ('Novo Contato', 'Novo Contato'),
        ('Em Andamento', 'Em Andamento (Tirando Dúvidas)'),
        ('Negociação', 'Negociação'),
        ('Aguardando Resposta', 'Aguardando Resposta do Cliente'),
        ('Fechado - Ganho', 'Fechado - Venda Concluída'),
        ('Fechado - Perdido', 'Fechado - Venda Perdida'),
        ('Follow-up', 'Follow-up Necessário'),
        ('Em Andamento (WhatsApp)', 'Em Andamento (WhatsApp)'),
    ]
    
    MARCA_CHOICES = [
        ('Mercedes Benz', 'Mercedes Benz'),
        ('Toyota', 'Toyota'),
        ('Tesla', 'Tesla'),
        ('Hyundai', 'Hyundai'),
        ('Volkswagen', 'Volkswagen'),
        ('Audi', 'Audi'),
        ('BMW', 'BMW'),
    ]
    TRANSMISSAO_CHOICES = [
        ('AT', 'Automática'),
        ('MT', 'Manual'),
        ('AUTO', 'Automática'),
    ]
    COMBUSTIVEL_CHOICES = [
        ('Petrol', 'Gasolina'),
        ('Electric', 'Elétrico'),
        ('Diesel', 'Diesel'),
    ]
    STATUS_VEICULO_CHOICES = [
        ('Disponível', 'Disponível para Venda'),
        ('Em Vistoria', 'Em Vistoria'),
        ('Em Lavagem', 'Em Lavagem'),
        ('Reservado', 'Reservado'),
        ('Vendido', 'Vendido'),
        ('Manutenção', 'Em Manutenção'),
    ]

    modelo = models.CharField(max_length=100, verbose_name="Modelo")
    marca = models.CharField(max_length=50, choices=MARCA_CHOICES, verbose_name="Marca")
    ano = models.IntegerField(verbose_name="Ano")
    preco = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço de Venda")
    lugares = models.IntegerField(verbose_name="Número de Lugares")
    transmissao = models.CharField(max_length=10, choices=TRANSMISSAO_CHOICES, verbose_name="Transmissão")
    combustivel = models.CharField(max_length=20, choices=COMBUSTIVEL_CHOICES, verbose_name="Combustível")
    quilometragem = models.IntegerField(verbose_name="Quilometragem (KM)")
    descricao = models.TextField(blank=True, verbose_name="Descrição")
    imagem = models.ImageField(upload_to='cars/', blank=True, null=True, verbose_name="Imagem do Carro")
    disponivel = models.BooleanField(default=True, verbose_name="Disponível para Venda")
    status_veiculo = models.CharField(
        max_length=20,
        choices=STATUS_VEICULO_CHOICES,
        default='Disponível',
        verbose_name="Status do Veículo"
    )
    vendedor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='carros_vendidos', verbose_name="Vendedor Responsável")
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")

    def __str__(self):
        return f"{self.marca} {self.modelo} ({self.ano})"

    class Meta:
        verbose_name = "Carro"
        verbose_name_plural = "Carros"
        ordering = ['-data_cadastro']

class Customer(models.Model):
    """
    Modelo para representar um cliente.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Usuário")
    nome_completo = models.CharField(max_length=200, verbose_name="Nome Completo")
    email = models.EmailField(unique=True, verbose_name="Email")
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone")
    whatsapp_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="WhatsApp")
    endereco = models.CharField(max_length=255, blank=True, null=True, verbose_name="Endereço")

    def __str__(self):
        return self.nome_completo

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"

class Sale(models.Model):
    """
    Modelo para registrar uma venda de carro.
    """
    carro = models.ForeignKey(Car, on_delete=models.CASCADE, verbose_name="Carro Vendido")
    cliente = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name="Comprador")
    preco_final = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço Final da Venda")
    
    # ALTERADO AQUI:
    # Opção 1: Registra a data na criação, mas permite edição manual.
    # Se você vai criar a Sale no momento da finalização do Lead, esta é uma boa opção.
    data_venda = models.DateTimeField(default=timezone.now, verbose_name="Data da Venda")

    # Opção 2 (Alternativa): Atualiza automaticamente a cada salvamento do objeto.
    # data_venda = models.DateTimeField(auto_now=True, verbose_name="Data da Venda") 
    # Esta opção faz a data_venda sempre ser a última data que o objeto Sale foi salvo,
    # o que pode ser útil se o objeto é salvo no momento da finalização da venda.

    def __str__(self):
        return f"Venda de {self.carro.modelo} para {self.cliente.nome_completo} em {self.data_venda.strftime('%d/%m/%Y')}"

    class Meta:
        verbose_name = "Venda"
        verbose_name_plural = "Vendas"

class VistoriaPattern(models.Model): # NOVO MODELO: Padrão de Vistoria
    """
    Define um padrão de vistoria personalizável (checklist).
    """
    name = models.CharField(max_length=100, unique=True, verbose_name="Nome do Padrão")
    description = models.TextField(blank=True, verbose_name="Descrição")
    is_active = models.BooleanField(default=True, verbose_name="Ativo")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Padrão de Vistoria"
        verbose_name_plural = "Padrões de Vistoria"
        ordering = ['name']

class VistoriaItemPattern(models.Model): # NOVO MODELO: Item do Padrão de Vistoria
    """
    Define um item específico dentro de um Padrão de Vistoria.
    """
    pattern = models.ForeignKey(VistoriaPattern, on_delete=models.CASCADE, related_name='items', verbose_name="Padrão de Vistoria")
    description = models.CharField(max_length=255, verbose_name="Descrição do Item")
    is_mandatory = models.BooleanField(default=False, verbose_name="Obrigatório") # Refere-se a "Obrigatoriedade"
    requires_photo = models.BooleanField(default=False, verbose_name="Requer Foto") # Refere-se a "Foto"
    order = models.IntegerField(default=0, verbose_name="Ordem") # Para ordenar os itens

    def __str__(self):
        return f"{self.pattern.name} - {self.description}"

    class Meta:
        verbose_name = "Item do Padrão de Vistoria"
        verbose_name_plural = "Itens do Padrão de Vistoria"
        ordering = ['pattern', 'order']
        unique_together = ('pattern', 'description') # Um item não pode ter a mesma descrição no mesmo padrão

class Vistoria(models.Model):
    """
    Modelo para registrar uma vistoria de um veículo.
    """
    RESULTADO_CHOICES = [
        ('Aprovado', 'Aprovado'),
        ('Reprovado', 'Reprovado'),
        ('Pendente', 'Pendente'),
        ('Finalizada', 'Finalizada'), # Adicionado "Finalizada"
    ]

    carro = models.ForeignKey(Car, on_delete=models.CASCADE, verbose_name="Carro")
    data_vistoria = models.DateField(verbose_name="Data da Vistoria")
    resultado = models.CharField(max_length=20, choices=RESULTADO_CHOICES, default='Pendente', verbose_name="Resultado Geral")
    observacoes_gerais = models.TextField(blank=True, verbose_name="Observações Gerais") # Renomeado de observacoes
    vistoriador = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Vistoriador")
    data_registro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Registro")
    pattern = models.ForeignKey(VistoriaPattern, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Padrão de Vistoria Utilizado") # NOVO CAMPO

    def __str__(self):
        return f"Vistoria de {self.carro.modelo} em {self.data_vistoria} - {self.resultado}"

    class Meta:
        verbose_name = "Vistoria"
        verbose_name_plural = "Vistorias"
        ordering = ['-data_vistoria']
        permissions = [
            ("can_add_vistoria", "Pode adicionar vistoria"),
            ("can_change_vistoria", "Pode editar vistoria"),
            ("can_view_all_vistorias", "Pode visualizar todas as vistorias"), # Nova permissão para ver todas
        ]

class VistoriaActualItem(models.Model): # NOVO MODELO: Registro real de um item de vistoria
    """
    Registra o resultado de um item específico em uma vistoria.
    """
    vistoria = models.ForeignKey(Vistoria, on_delete=models.CASCADE, related_name='actual_items', verbose_name="Vistoria")
    item_pattern = models.ForeignKey(VistoriaItemPattern, on_delete=models.CASCADE, verbose_name="Item do Padrão")
    is_ok = models.BooleanField(default=True, verbose_name="Está OK?") # Resultado simples (pass/fail)
    description_result = models.TextField(blank=True, verbose_name="Descrição do Resultado")
    photo = models.ImageField(upload_to='vistorias/itens/', blank=True, null=True, verbose_name="Foto do Item")

    def __str__(self):
        return f"{self.vistoria.carro.modelo} - {self.item_pattern.description} ({'OK' if self.is_ok else 'PROBLEMA'})"

    class Meta:
        verbose_name = "Item da Vistoria Real"
        verbose_name_plural = "Itens da Vistoria Real"
        unique_together = ('vistoria', 'item_pattern') # Um item de padrão só pode ser avaliado uma vez por vistoria
        ordering = ['item_pattern__order'] # Ordena os itens com base na ordem do padrão


class Lavagem(models.Model):
    """
    Modelo para registrar a lavagem de um veículo.
    """
    TIPO_LAVAGEM_CHOICES = [
        ('Simples', 'Lavagem Simples'),
        ('Completa', 'Lavagem Completa'),
        ('Detalhada', 'Lavagem Detalhada'),
        ('Polimento', 'Polimento'),
    ]

    carro = models.ForeignKey(Car, on_delete=models.CASCADE, verbose_name="Carro")
    data_lavagem = models.DateField(verbose_name="Data da Lavagem")
    tipo_lavagem = models.CharField(max_length=20, choices=TIPO_LAVAGEM_CHOICES, verbose_name="Tipo de Lavagem")
    custo = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Custo")
    observacoes = models.TextField(blank=True, verbose_name="Observações")
    responsavel = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Responsável")
    data_registro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Registro")

    def __str__(self):
        return f"Lavagem de {self.carro.modelo} em {self.data_lavagem} ({self.tipo_lavagem})"

    class Meta:
        verbose_name = "Lavagem"
        verbose_name_plural = "Lavagens"
        ordering = ['-data_lavagem']
        permissions = [
            ("can_add_lavagem", "Pode adicionar lavagem"),
            ("can_change_lavagem", "Pode editar lavagem"),
        ]

class LeadInteraction(models.Model):

    # NOVO CAMPO para registrar a data exata da conversão
    data_conversao = models.DateTimeField(null=True, blank=True, verbose_name="Data da Conversão") # Adicionado

    def save(self, *args, **kwargs):
        # Quando o status muda para 'Fechado - Ganho' e a data_conversao ainda não foi definida
        if self.status == 'Fechado - Ganho' and not self.data_conversao:
            self.data_conversao = timezone.now() # Registra a data da conversão
        elif self.status != 'Fechado - Ganho' and self.data_conversao:
            # Se o status voltar a não ser 'Fechado - Ganho', limpa a data de conversão (opcional, mas boa prática)
            self.data_conversao = None 
        super().save(*args, **kwargs)

    STATUS_INTERACTION_CHOICES = [
        ('Novo Contato', 'Novo Contato'),
        ('Em Andamento', 'Em Andamento (Tirando Dúvidas)'),
        ('Negociação', 'Negociação'),
        ('Aguardando Resposta', 'Aguardando Resposta do Cliente'),
        ('Fechado - Ganho', 'Fechado - Venda Concluída'),
        ('Fechado - Perdido', 'Fechado - Venda Perdida'),
        ('Follow-up', 'Follow-up Necessário'),
        ('Em Andamento (WhatsApp)', 'Em Andamento (WhatsApp)'),
    ]

    status = models.CharField(max_length=50, choices=STATUS_INTERACTION_CHOICES, default='Novo Contato', verbose_name="Status da Interação")
    data_interacao = models.DateTimeField(auto_now_add=True, verbose_name="Data da Interação") # Data de criação do lead
    ultima_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização") # Data da última modificação
    carro = models.ForeignKey(Car, on_delete=models.CASCADE, verbose_name="Carro de Interesse")
    cliente = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name="Cliente/Lead")
    vendedor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Vendedor Responsável")
    status = models.CharField(max_length=50, choices=STATUS_INTERACTION_CHOICES, default='Novo Contato', verbose_name="Status da Interação")
    data_interacao = models.DateTimeField(auto_now_add=True, verbose_name="Data da Interação")
    ultima_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    observacoes = models.TextField(blank=True, verbose_name="Notas da Interação")

    def __str__(self):
        return f"Interação: {self.cliente.nome_completo} - {self.carro.modelo} ({self.status})"

    class Meta:
        verbose_name = "Interação de Lead"
        verbose_name_plural = "Interações de Leads"
        ordering = ['-ultima_atualizacao']
