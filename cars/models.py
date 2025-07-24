# cars/models.py

from django.db import models
from django.contrib.auth.models import User

class Car(models.Model):
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
    data_venda = models.DateTimeField(auto_now_add=True, verbose_name="Data da Venda")

    def __str__(self):
        return f"Venda de {self.carro.modelo} para {self.cliente.nome_completo} em {self.data_venda.strftime('%d/%m/%Y')}"

    class Meta:
        verbose_name = "Venda"
        verbose_name_plural = "Vendas"

class Vistoria(models.Model):
    """
    Modelo para registrar a vistoria de um veículo.
    """
    RESULTADO_CHOICES = [
        ('Aprovado', 'Aprovado'),
        ('Reprovado', 'Reprovado'),
        ('Pendente', 'Pendente'),
    ]

    carro = models.ForeignKey(Car, on_delete=models.CASCADE, verbose_name="Carro")
    data_vistoria = models.DateField(verbose_name="Data da Vistoria")
    resultado = models.CharField(max_length=20, choices=RESULTADO_CHOICES, default='Pendente', verbose_name="Resultado")
    observacoes = models.TextField(blank=True, verbose_name="Observações")
    vistoriador = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Vistoriador")
    data_registro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Registro")

    def __str__(self):
        return f"Vistoria de {self.carro.modelo} em {self.data_vistoria} - {self.resultado}"

    class Meta:
        verbose_name = "Vistoria"
        verbose_name_plural = "Vistorias"
        ordering = ['-data_vistoria']
        permissions = [ # PERMISSÕES CUSTOMIZADAS
            ("can_add_vistoria", "Pode adicionar vistoria"),
            ("can_change_vistoria", "Pode editar vistoria"),
        ]

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
        permissions = [ # PERMISSÕES CUSTOMIZADAS
            ("can_add_lavagem", "Pode adicionar lavagem"),
            ("can_change_lavagem", "Pode editar lavagem"),
        ]

class LeadInteraction(models.Model):
    """
    Modelo para registrar interações de leads/clientes com carros específicos.
    Funciona como um mini-CRM para o vendedor.
    """
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
