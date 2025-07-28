# cars/views.py

from django.shortcuts import render, get_object_or_404, redirect

from .models import Car, Vistoria, Lavagem, LeadInteraction, Customer, Sale
from .forms import LeadInteractionForm, VistoriaForm, LavagemForm, CarForm
from .models import Car, Vistoria, Lavagem, LeadInteraction, Customer, Sale, VistoriaPattern, VistoriaItemPattern, VistoriaActualItem
from django.views.generic import ListView, DetailView, TemplateView, View
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib import messages
from django.db.models import Q, Sum, Avg, Count
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.decorators import method_decorator
from .models import LeadInteraction # Certifique-se de que LeadInteraction está importado
from django.views.decorators.csrf import csrf_exempt # Importe csrf_exempt
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
import random
from datetime import datetime, timedelta
import urllib.parse
import json
import csv
from django.http import JsonResponse # Adicionar este import
from django.http import HttpResponse
from .models import Car # Certifique-se de que Car está importado
from django.utils import timezone # Importe timezone
from django.db.models.functions import TruncMonth


def admin_dashboard_view(request):
    end_date = timezone.now().date()
    start_date_sales = end_date - timedelta(days=365) # Últimos 12 meses para vendas
    start_date_conversion = end_date - timedelta(days=180) # Últimos 6 meses para conversão, se preferir

    # --- Dados para Tendência de Vendas (salesTrendChart) ---
    # Agora usando o modelo 'Sale' e 'preco_final' para o valor da venda
    sales_data_query = Sale.objects.filter(
        data_venda__range=[start_date_sales, end_date] # Use o campo de data de venda do seu modelo Sale
    ).annotate(
        month=TruncMonth('data_venda')
    ).values('month').annotate(
        total_revenue=Sum('preco_final') # Use o campo de valor final do seu modelo Sale
    ).order_by('month')

    sales_trend_labels = []
    sales_trend_data = []

    current_month = start_date_sales.replace(day=1)
    while current_month <= end_date:
        month_label = current_month.strftime('%b/%Y') # Formato: Jan/2024
        sales_trend_labels.append(month_label)
        
        # O `next` precisa buscar os dados gerados por `sales_data_query`
        found_month_data = next((item for item in sales_data_query if item['month'].month == current_month.month and item['month'].year == current_month.year), None)
        sales_trend_data.append(float(found_month_data['total_revenue']) if found_month_data else 0)
        
        if current_month.month == 12:
            current_month = current_month.replace(year=current_month.year + 1, month=1)
        else:
            current_month = current_month.replace(month=current_month.month + 1)

    # --- Dados para Taxa de Conversão (conversionRateChart) ---
    # A lógica para LeadInteraction está correta aqui, LeadInteraction já está importado.
    conversion_data_raw = LeadInteraction.objects.filter(
        data_interacao__range=[start_date_conversion, end_date]
    ).annotate(
        month=TruncMonth('data_interacao')
    ).values('month').order_by('month')

    conversion_trend_labels = []
    conversion_trend_data = []

    current_month_conv = start_date_conversion.replace(day=1)
    while current_month_conv <= end_date:
        month_label_conv = current_month_conv.strftime('%b/%Y')
        conversion_trend_labels.append(month_label_conv)

        total_leads_month = LeadInteraction.objects.filter(
            data_interacao__year=current_month_conv.year,
            data_interacao__month=current_month_conv.month
        ).count()
        
        converted_leads_month = LeadInteraction.objects.filter(
            data_interacao__year=current_month_conv.year,
            data_interacao__month=current_month_conv.month,
            status='Fechado - Ganho' # Use o status exato que indica uma venda/conversão
        ).count()
        
        conversion_rate = (converted_leads_month / total_leads_month * 100) if total_leads_month > 0 else 0
        conversion_trend_data.append(round(conversion_rate, 1))

        if current_month_conv.month == 12:
            current_month_conv = current_month_conv.replace(year=current_month_conv.year + 1, month=1)
        else:
            current_month_conv = current_month_conv.replace(month=current_month_conv.month + 1)


    # --- Outros dados para os cards de Visão Geral ---
    # Agora usando o modelo 'Sale' e 'preco_final' para o valor da venda
    monthly_revenue = Sale.objects.filter( # Usando o modelo Sale
        data_venda__year=end_date.year,
        data_venda__month=end_date.month
    ).aggregate(Sum('preco_final'))['preco_final__sum'] or 0 # Campo de agregação ajustado

    total_orders_this_month = Sale.objects.filter( # Usando o modelo Sale
        data_venda__year=end_date.year,
        data_venda__month=end_date.month
    ).count()

    # Adapte esta parte se 'Customer' não tiver uma relação direta com 'Sale' pela 'data_venda'
    # Você pode precisar de uma query JOIN ou buscar clientes de `LeadInteraction` com status 'Fechado - Ganho'
    active_customers_this_month = Customer.objects.filter(
        # Exemplo: Assumindo que Customer tem uma relação reversa 'sale_set' com Sale
        sale__data_venda__year=end_date.year,
        sale__data_venda__month=end_date.month
    ).distinct().count()

    # Taxa de Conversão do mês atual (LeadInteraction já está correto aqui)
    total_leads_month_current = LeadInteraction.objects.filter(
        data_interacao__year=end_date.year,
        data_interacao__month=end_date.month
    ).count()
    converted_leads_month_current = LeadInteraction.objects.filter(
        data_interacao__year=end_date.year,
        data_interacao__month=end_date.month,
        status='Fechado - Ganho' # Status que indica conversão
    ).count()
    conversion_rate_this_month = (converted_leads_month_current / total_leads_month_current * 100) if total_leads_month_current > 0 else 0

    context = {
        'monthly_revenue': monthly_revenue,
        'total_orders_this_month': total_orders_this_month,
        'active_customers_this_month': active_customers_this_month,
        'conversion_rate_this_month': round(conversion_rate_this_month, 1), # Arredonda para 1 casa decimal no contexto
        'sales_trend_labels': sales_trend_labels,
        'sales_trend_data': sales_trend_data,
        'conversion_trend_labels': conversion_trend_labels,
        'conversion_trend_data': conversion_trend_data,
    }
    return render(request, 'dashboard/admin_overview.html', context)

def export_cars_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="carros.csv"'

    writer = csv.writer(response)
    writer.writerow(['Marca', 'Modelo', 'Ano', 'Preço', 'Status', 'Quilometragem']) # Cabeçalho do CSV

    cars = Car.objects.all().order_by('marca' , 'modelo')
    for car in cars:
        writer.writerow([
            car.marca,
            car.modelo,
            car.ano,
            str(car.preco), # Converte Decimal para string para o CSV
            car.get_status_veiculo_display(), # Pega o valor legível do ChoiceField
            car.quilometragem
        ])

    return response

def quick_analysis_data(request):
    # Contagem de carros por status
    cars_by_status = Car.objects.values('status_veiculo').annotate(count=Count('status_veiculo'))
    car_labels = [entry['status_veiculo'] for entry in cars_by_status]
    car_data = [entry['count'] for entry in cars_by_status]

    # Mapear chaves para valores legíveis se necessário
    status_map_car = dict(Car.STATUS_VEICULO_CHOICES)
    car_labels_display = [status_map_car.get(label, label) for label in car_labels]

    # Contagem de leads por status
    leads_by_status = LeadInteraction.objects.values('status').annotate(count=Count('status')) # ESTAS LINHAS DEVEM VIR ANTES
    lead_labels = [entry['status'] for entry in leads_by_status] # ESTAS LINHAS DEVEM VIR ANTES
    lead_data = [entry['count'] for entry in leads_by_status] # ESTAS LINHAS DEVEM VIR ANTES
    
    # Mapear chaves para valores legíveis se necessário
    status_map_lead = dict(LeadInteraction._meta.get_field('status').choices)
    lead_labels_display = [status_map_lead.get(label, label) for label in lead_labels]

    data = {
        'carsByStatusLabels': car_labels_display,
        'carsByStatusData': car_data,
        'leadsByStatusLabels': lead_labels_display,
        'leadsByStatusData': lead_data,
    }
    return JsonResponse(data)

# Função auxiliar para adicionar a quilometragem em "K" aos objetos Carro
def add_kilometragem_k(cars_queryset):
    for car in cars_queryset:
        car.quilometragem_k = car.quilometragem / 1000
    return cars_queryset

    #Função auxiliar para coletar dados do dashboard de administrador/gerente#
def get_admin_dashboard_data():
    """
    Coleta dados de visão geral da empresa para administradores/gerentes.
    Inclui métricas e dados mock para gráficos.
    """
    today = datetime.now().date()
    start_of_month = today.replace(day=1)
    
    total_cars = Car.objects.count()
    available_cars = Car.objects.filter(disponivel=True).count()
    total_sales = Sale.objects.count()
    total_revenue = Sale.objects.aggregate(total=Sum('preco_final'))['total'] or 0
    total_leads = LeadInteraction.objects.count()
    
    # Métricas do mês atual
    monthly_sales = Sale.objects.filter(data_venda__date__gte=start_of_month, data_venda__date__lte=today)
    monthly_revenue = monthly_sales.aggregate(total=Sum('preco_final'))['total'] or 0
    monthly_leads = LeadInteraction.objects.filter(data_interacao__date__gte=start_of_month, data_interacao__date__lte=today)
    
    # Clientes Ativos (exemplo: leads que não são 'Novo Contato' ou 'Fechado - Perdido' no mês)
    active_customers_this_month = monthly_leads.exclude(status__in=['Novo Contato', 'Fechado - Perdido']).values('cliente').distinct().count()

    # Taxa de Conversão (simplificada: Vendas Concluídas / Total de Leads)
    conversion_rate = (monthly_sales.count() / monthly_leads.count() * 100) if monthly_leads.count() > 0 else 0

    # Dados Mock para Gráficos (últimos 6 meses)
    sales_trend_data = []
    conversion_trend_data = []
    months_labels = []
    
    for i in range(6, 0, -1): # Últimos 6 meses
        month_start = (today - timedelta(days=30*i)).replace(day=1) # Aproximado
        month_end = (month_start + timedelta(days=30)).replace(day=1) - timedelta(days=1) # Fim do mês
        
        # Dados de vendas mock
        mock_sales = random.randint(5000, 20000) if i != 1 else float(monthly_revenue) # Mês atual usa o valor real
        sales_trend_data.append(round(mock_sales, 2))

        # Dados de conversão mock
        mock_conversion = random.uniform(2.0, 8.0) if i != 1 else round(conversion_rate, 2) # Mês atual usa o valor real
        conversion_trend_data.append(round(mock_conversion, 2))
        
        months_labels.append(month_start.strftime('%b').lower()) # Ex: 'jan', 'fev'
    
    return {
        'total_cars': total_cars,
        'available_cars': available_cars,
        'total_sales': total_sales,
        'total_revenue': total_revenue,
        'total_leads': total_leads,
        'new_leads_today': LeadInteraction.objects.filter(data_interacao__date=today).count(),
        
        'monthly_revenue': monthly_revenue,
        'total_orders_this_month': monthly_sales.count(),
        'active_customers_this_month': active_customers_this_month,
        'conversion_rate_this_month': round(conversion_rate, 2),

        'sales_trend_labels': months_labels,
        'sales_trend_data': sales_trend_data,
        'conversion_trend_labels': months_labels,
        'conversion_trend_data': conversion_trend_data,
    }

@method_decorator(login_required, name='dispatch')
class InspectionListView(LoginRequiredMixin, ListView):
    model = Vistoria
    template_name = 'dashboard/inspection_list.html'
    context_object_name = 'inspections'
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        # Admins/Gerentes/Vendedores veem todas as vistorias, Vistoriadores veem as que são responsáveis
        if user.is_superuser or user.groups.filter(name__in=['Administradores', 'Gerentes', 'Vendedores']).exists():
            return Vistoria.objects.all().order_by('-data_vistoria')
        elif user.groups.filter(name='Vistoriadores').exists():
            return Vistoria.objects.filter(vistoriador=user).order_by('-data_vistoria')
        return Vistoria.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        # Passa as permissões para o template para controlar a visibilidade dos botões
        context['can_add_inspection'] = user.has_perm('cars.add_vistoria')
        context['can_change_inspection'] = user.has_perm('cars.change_vistoria')
        return context

@login_required
@permission_required('cars.add_vistoria', raise_exception=True)
def add_inspection_view(request):
    """
    View para adicionar um novo registro de vistoria.
    Exige que o usuário esteja logado e tenha a permissão 'cars.add_vistoria'.
    """
    if request.method == 'POST':
        form = VistoriaForm(request.POST)
        if form.is_valid():
            vistoria = form.save(commit=False)
            vistoria.vistoriador = request.user # Atribui o vistoriador logado
            vistoria.save()
            messages.success(request, 'Vistoria adicionada com sucesso!')
            return redirect('inspection_list') # Redireciona para a lista de vistorias
    else:
        # Preenche o campo vistoriador com o usuário logado por padrão
        form = VistoriaForm(initial={'vistoriador': request.user}) 
    
    context = {
        'form': form,
        'action_type': 'Adicionar',
        'model_name': 'Vistoria' # Nome do modelo para o template genérico
    }
    return render(request, 'dashboard/inspection_form.html', context)

@login_required
@permission_required('cars.change_vistoria', raise_exception=True)
def edit_inspection_view(request, pk):
    """
    View para editar um registro de vistoria existente.
    Exige que o usuário esteja logado e tenha a permissão 'cars.change_vistoria'.
    """
    vistoria = get_object_or_404(Vistoria, pk=pk) # Obtém a vistoria pelo ID

    if request.method == 'POST':
        form = VistoriaForm(request.POST, instance=vistoria) # Preenche o formulário com dados POST e a instância existente
        if form.is_valid():
            form.save() # Salva as alterações na vistoria
            messages.success(request, 'Vistoria atualizada com sucesso!')
            return redirect('inspection_list') # Redireciona para a lista de vistorias
    else:
        form = VistoriaForm(instance=vistoria) # Preenche o formulário com os dados da vistoria existente
    
    context = {
        'form': form,
        'action_type': 'Editar',
        'model_name': 'Vistoria',
        'vistoria': vistoria # Passa a instância da vistoria para o template
    }
    return render(request, 'dashboard/inspection_form.html', context)

@method_decorator(login_required, name='dispatch')
class CarWashListView(LoginRequiredMixin, ListView):
    model = Lavagem
    template_name = 'dashboard/car_wash_list.html'
    context_object_name = 'car_washes'
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        # Admins/Gerentes/Vendedores veem todas as lavagens, outros veem as que são responsáveis
        if user.is_superuser or user.groups.filter(name__in=['Administradores', 'Gerentes', 'Vendedores']).exists():
            return Lavagem.objects.all().order_by('-data_lavagem')
        elif user.groups.filter(name__in=['Vistoriadores', 'Lavadores']).exists(): # Se houver um grupo 'Lavadores'
            return Lavagem.objects.filter(responsavel=user).order_by('-data_lavagem')
        return Lavagem.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        # Passa as permissões para o template para controlar a visibilidade dos botões
        context['can_add_car_wash'] = user.has_perm('cars.add_lavagem')
        context['can_change_car_wash'] = user.has_perm('cars.change_lavagem')
        return context

class HomePageView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        latest_cars = Car.objects.filter(disponivel=True).order_by('-data_cadastro')[:4]
        context['latest_cars'] = add_kilometragem_k(latest_cars)
        return context

class CarListView(ListView):
    model = Car
    template_name = 'cars/car_list.html'
    context_object_name = 'cars'
    paginate_by = 8

    def get_queryset(self):
        queryset = super().get_queryset().filter(disponivel=True)
        brand = self.request.GET.get('brand')
        model = self.request.GET.get('model')
        max_price = self.request.GET.get('max_price')
        if brand and brand != 'Selecione a Marca':
            queryset = queryset.filter(marca=brand)
        if model:
            queryset = queryset.filter(Q(modelo__icontains=model))
        if max_price:
            try:
                max_price = float(max_price)
                queryset = queryset.filter(preco__lte=max_price)
            except ValueError:
                pass
        return add_kilometragem_k(queryset)

class CarDetailView(DetailView):
    model = Car
    template_name = 'cars/car_detail.html'
    context_object_name = 'car'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        car = self.get_object()
        car.quilometragem_k = car.quilometragem / 1000
        context['car'] = car
        latest_cars = Car.objects.exclude(pk=self.object.pk).filter(disponivel=True).order_by('-data_cadastro')[:3]
        context['latest_cars'] = add_kilometragem_k(latest_cars)
        return context

class AboutPageView(TemplateView):
    template_name = 'about.html'

class ServicePageView(TemplateView):
    template_name = 'service.html'

class BlogPageView(TemplateView):
    template_name = 'blog.html'

class FeaturePageView(TemplateView):
    template_name = 'feature.html'

class TeamPageView(TemplateView):
    template_name = 'team.html'

class TestimonialPageView(TemplateView):
    template_name = 'testimonial.html'

class Custom404View(TemplateView):
    template_name = '404.html'

class ContactSuccessView(TemplateView):
    template_name = 'contact_success.html'

def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        project = request.POST.get('project')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        full_message = f"Nome: {name}\nEmail: {email}\nTelefone: {phone or 'N/A'}\nProjeto/Tipo: {project or 'N/A'}\n\nAssunto: {subject or 'N/A'}\nMensagem:\n{message}"

        try:
            send_mail(
                subject,
                full_message,
                settings.DEFAULT_FROM_EMAIL,
                ['your_email@example.com'],
                fail_silently=False,
            )
            messages.success(request, 'Sua mensagem foi enviada com sucesso! Entraremos em contato em breve.')
            return HttpResponseRedirect(reverse('contact_success'))
        except Exception as e:
            messages.error(request, f'Houve um erro ao enviar sua mensagem: {e}. Por favor, tente novamente mais tarde.')
            print(f"Erro ao enviar e-mail: {e}")
            return render(request, 'contact.html', {
                'name': name, 'email': email, 'phone': phone, 'project': project, 'subject': subject, 'message': message
            })
    return render(request, 'contact.html')

def create_customer_lead(request):
    if request.method == 'POST':
        car_id = request.POST.get('car_id')
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        whatsapp_number = request.POST.get('whatsapp_number') 

        car = get_object_or_404(Car, pk=car_id)
        
        customer, created = Customer.objects.get_or_create(
            email=email, 
            defaults={
                'nome_completo': name,
                'whatsapp_number': whatsapp_number,
                'telefone': request.POST.get('phone', ''),
            }
        )
        if not created:
            if customer.nome_completo != name:
                customer.nome_completo = name
            if customer.whatsapp_number != whatsapp_number:
                customer.whatsapp_number = whatsapp_number
            if customer.telefone != request.POST.get('phone', ''):
                customer.telefone = request.POST.get('phone', '')
            customer.save()

        lead_interaction = LeadInteraction.objects.create(
            carro=car,
            cliente=customer,
            vendedor=None,
            status='Novo Contato',
            observacoes=f"Mensagem do cliente: {message}"
        )

        messages.success(request, 'Sua consulta sobre o veículo foi enviada! Um de nossos vendedores entrará em contato em breve.')
        
        return redirect('contact_success')

    messages.error(request, 'Método de requisição inválido.')
    return redirect('home')


@method_decorator(login_required, name='dispatch')
class SellerDashboardView(LoginRequiredMixin, ListView):
    model = Car
    template_name = 'cars/seller_dashboard.html'
    context_object_name = 'my_cars'
    paginate_by = 10

    def get_queryset(self):
        return Car.objects.filter(vendedor=self.request.user).order_by('-data_cadastro')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['my_cars'] = add_kilometragem_k(context['my_cars'])
        return context

@method_decorator(login_required, name='dispatch')
class LeadInteractionListView(LoginRequiredMixin, ListView):
    model = LeadInteraction
    template_name = 'cars/lead_interaction_list.html'
    context_object_name = 'lead_interactions'
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Vendedores').exists():
            return LeadInteraction.objects.filter(Q(vendedor=user) | Q(vendedor__isnull=True)).order_by('-ultima_atualizacao')
        elif user.is_superuser or user.groups.filter(name__in=['Administradores', 'Gerentes']).exists():
            return LeadInteraction.objects.all().order_by('-ultima_atualizacao')
        return LeadInteraction.objects.none()

@csrf_exempt # <--- IMPORTANTE: Desabilita a verificação CSRF para esta view (para requisições AJAX)
@login_required
def update_lead_status_kanban(request):
    """
    Atualiza o status do lead via requisição AJAX (Kanban drag-and-drop).
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            lead_id = data.get('lead_id')
            new_status = data.get('new_status')

            lead = get_object_or_404(LeadInteraction, pk=lead_id)
            
            user = request.user
            # Permissão: Vendedor responsável, ou Admin/Gerente pode mudar
            # Se o lead não tem vendedor atribuído, qualquer vendedor pode movê-lo inicialmente.
            if lead.vendedor != user and not (user.is_superuser or user.groups.filter(name__in=['Administradores', 'Gerentes']).exists()):
                # Se o lead não tem vendedor e o usuário é vendedor, ele pode reivindicar ao mover
                if lead.vendedor is None and user.groups.filter(name='Vendedores').exists():
                    lead.vendedor = user
                else:
                    return JsonResponse({'status': 'error', 'message': 'Você não tem permissão para atualizar este lead.'}, status=403)

            # Valida se o novo status é um dos STATUS_INTERACTION_CHOICES
            valid_statuses = [choice[0] for choice in LeadInteraction.STATUS_INTERACTION_CHOICES]
            if new_status not in valid_statuses:
                return JsonResponse({'status': 'error', 'message': 'Status inválido.'}, status=400)

            lead.status = new_status
            lead.save()
            return JsonResponse({'status': 'success', 'message': 'Status do lead atualizado com sucesso!'})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Requisição JSON inválida.'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Método não permitido.'}, status=405)


@login_required
def lead_interaction_detail_and_update(request, pk):
    lead_interaction = get_object_or_404(LeadInteraction, pk=pk)

    user = request.user
    if lead_interaction.vendedor != user and not (user.is_superuser or user.groups.filter(name__in=['Administradores', 'Gerentes']).exists()):
        messages.error(request, "Você não tem permissão para acessar este lead.")
        return redirect('lead_interaction_list')

    if request.method == 'POST':
        form = LeadInteractionForm(request.POST, instance=lead_interaction)
        if form.is_valid():
            if form.cleaned_data['status'] == 'Fechado - Ganho':
                car = lead_interaction.carro
                car.disponivel = False
                car.status_veiculo = 'Vendido'
                car.save()
                messages.info(request, f"Carro '{car.modelo}' atualizado para indisponível (Vendido)!")

            form.save()
            messages.success(request, 'Status da interação atualizado com sucesso!')
            return redirect('lead_interaction_list')
    else:
        form = LeadInteractionForm(instance=lead_interaction)
    
    context = {
        'lead_interaction': lead_interaction,
        'form': form,
    }
    return render(request, 'cars/lead_interaction_detail.html', context)

@login_required
def lead_interaction_detail_and_update(request, pk):
    lead_interaction = get_object_or_404(LeadInteraction, pk=pk)

    user = request.user
    if lead_interaction.vendedor != user and not (user.is_superuser or user.groups.filter(name__in=['Administradores', 'Gerentes']).exists()):
        messages.error(request, "Você não tem permissão para acessar este lead.")
        return redirect('lead_interaction_list')

    if request.method == 'POST':
        form = LeadInteractionForm(request.POST, instance=lead_interaction)
        if form.is_valid():
            if form.cleaned_data['status'] == 'Fechado - Ganho':
                car = lead_interaction.carro
                car.disponivel = False
                car.status_veiculo = 'Vendido'
                car.save()
                messages.info(request, f"Carro '{car.modelo}' atualizado para indisponível (Vendido)!")

            form.save()
            messages.success(request, 'Status da interação atualizado com sucesso!')
            return redirect('lead_interaction_list')
    else:
        form = LeadInteractionForm(instance=lead_interaction)
    
    context = {
        'lead_interaction': lead_interaction,
        'form': form,
    }
    return render(request, 'cars/lead_interaction_detail.html', context)

@login_required
def create_lead_interaction_manual(request):
    if request.method == 'POST':
        car_id = request.POST.get('car_id')
        customer_name = request.POST.get('customer_name', 'Cliente Genérico')
        customer_email = request.POST.get('customer_email', f'generico_{random.randint(1,1000000)}@example.com') 
        initial_notes = request.POST.get('initial_notes', 'Interação criada manualmente pelo vendedor.')
        whatsapp_number = request.POST.get('whatsapp_number')

        car = get_object_or_404(Car, pk=car_id)

        customer, created = Customer.objects.get_or_create(
            email=customer_email, 
            defaults={
                'nome_completo': customer_name,
                'whatsapp_number': whatsapp_number
            }
        )
        if not created:
            if customer.nome_completo != customer_name:
                customer.nome_completo = customer_name
            if customer.whatsapp_number != whatsapp_number:
                customer.whatsapp_number = whatsapp_number
            customer.save()


        lead_interaction = LeadInteraction.objects.create(
            carro=car,
            cliente=customer,
            vendedor=request.user,
            status='Novo Contato',
            observacoes=initial_notes
        )
        messages.success(request, f'Nova interação de lead criada para {customer.nome_completo}!')
        return redirect('lead_interaction_detail', pk=lead_interaction.pk)
    
    context = {
        'all_cars': Car.objects.all().order_by('marca', 'modelo')
    }
    return render(request, 'cars/create_lead_interaction.html', context)

@login_required
def claim_lead(request, pk):
    lead_interaction = get_object_or_404(LeadInteraction, pk=pk)

    user = request.user
    if lead_interaction.vendedor is not None and lead_interaction.vendedor != user and not (user.is_superuser or user.groups.filter(name__in=['Administradores', 'Gerentes']).exists()):
        messages.error(request, "Este lead já está atribuído a outro vendedor.")
        return redirect('lead_interaction_list')
    
    lead_interaction.vendedor = user
    lead_interaction.status = 'Em Andamento' if lead_interaction.status == 'Novo Contato' else lead_interaction.status
    lead_interaction.save()
    messages.success(request, f"Você reivindicou o lead de {lead_interaction.cliente.nome_completo}!")

    if user.email:
        send_mail(
            f'Lead Reivindicado: {lead_interaction.carro.marca} {lead_interaction.carro.modelo}',
            f'Olá {user.username},\n\nVocê reivindicou o lead para o carro {lead_interaction.carro.marca} {lead_interaction.carro.modelo} de {lead_interaction.cliente.nome_completo} ({lead_interaction.cliente.email}).\n\nStatus atual: {lead_interaction.status}\n\nAcesse o painel de leads para mais detalhes: {request.build_absolute_uri(reverse("lead_interaction_detail", args=[lead_interaction.pk]))}',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=True,
        )

    return redirect('lead_interaction_detail', pk=pk)

@login_required
def initiate_whatsapp_conversation(request, pk):
    lead_interaction = get_object_or_404(LeadInteraction, pk=pk)

    user = request.user
    if lead_interaction.vendedor != user and not (user.is_superuser or user.groups.filter(name__in=['Administradores', 'Gerentes']).exists()):
        messages.error(request, "Você não tem permissão para iniciar conversa para este lead.")
        return redirect('lead_interaction_list')

    if not lead_interaction.cliente.whatsapp_number:
        messages.error(request, f"O cliente {lead_interaction.cliente.nome_completo} não possui um número de WhatsApp cadastrado.")
        return redirect('lead_interaction_detail', pk=pk)
    
    lead_interaction.status = 'Em Andamento (WhatsApp)'
    lead_interaction.save()
    messages.success(request, f"Status do lead atualizado para 'Em Andamento (WhatsApp)'!")

    whatsapp_message = f"Olá {lead_interaction.cliente.nome_completo}! Meu nome é {user.get_full_name() or user.username} da Cental. Vi seu interesse no carro {lead_interaction.carro.marca} {lead_interaction.carro.modelo} ({lead_interaction.carro.ano}) disponível por R${lead_interaction.carro.preco:.2f}. Posso ajudar com alguma dúvida?"
    encoded_message = urllib.parse.quote(whatsapp_message)

    whatsapp_url = f"https://wa.me/{lead_interaction.cliente.whatsapp_number}?text={encoded_message}"
    
    return redirect(whatsapp_url)

@login_required
@permission_required('cars.add_lavagem', raise_exception=True)
def add_car_wash_view(request):
    """
    View para adicionar um novo registro de lavagem.
    Exige que o usuário esteja logado e tenha a permissão 'cars.add_lavagem'.
    """
    if request.method == 'POST':
        form = LavagemForm(request.POST)
        if form.is_valid():
            lavagem = form.save(commit=False)
            lavagem.responsavel = request.user # Atribui o responsável logado
            lavagem.save()
            messages.success(request, 'Lavagem adicionada com sucesso!')
            return redirect('car_wash_list') # Redireciona para a lista de lavagens
    else:
        # Preenche o campo responsável com o usuário logado por padrão
        form = LavagemForm(initial={'responsavel': request.user}) 
    
    context = {
        'form': form,
        'action_type': 'Adicionar',
        'model_name': 'Lavagem' # Nome do modelo para o template genérico
    }
    return render(request, 'dashboard/car_wash_form.html', context)


@login_required
@permission_required('cars.change_lavagem', raise_exception=True)
def edit_car_wash_view(request, pk):
    """
    View para editar um registro de lavagem existente.
    Exige que o usuário esteja logado e tenha a permissão 'cars.change_lavagem'.
    """
    lavagem = get_object_or_404(Lavagem, pk=pk) # Obtém o registro de lavagem pelo ID

    if request.method == 'POST':
        form = LavagemForm(request.POST, instance=lavagem) # Preenche o formulário com dados POST e a instância existente
        if form.is_valid():
            form.save() # Salva as alterações no registro de lavagem
            messages.success(request, 'Lavagem atualizada com sucesso!')
            return redirect('car_wash_list') # Redireciona para a lista de lavagens
    else:
        form = LavagemForm(instance=lavagem) # Preenche o formulário com os dados do registro de lavagem existente
    
    context = {
        'form': form,
        'action_type': 'Editar',
        'model_name': 'Lavagem',
        'lavagem': lavagem # Passa a instância da lavagem para o template
    }
    return render(request, 'dashboard/car_wash_form.html', context)

# NOVO: Views para CRUD de Carros (Adicionar)
@login_required
@permission_required('cars.add_car', raise_exception=True)
def add_car_view(request):
    if request.method == 'POST':
        form = CarForm(request.POST, request.FILES)
        if form.is_valid():
            car = form.save()
            messages.success(request, f"Carro '{car.modelo}' adicionado com sucesso!")
            return redirect('seller_dashboard')
    else:
        form = CarForm(initial={'vendedor': request.user})
    
    context = {
        'form': form,
        'action_type': 'Adicionar',
        'model_name': 'Carro'
    }
    return render(request, 'dashboard/car_form.html', context)

# NOVO: Views para CRUD de Carros (Editar)
@login_required
@permission_required('cars.change_car', raise_exception=True)
def edit_car_view(request, pk):
    car = get_object_or_404(Car, pk=pk)
    
    if car.vendedor != request.user and not (request.user.is_superuser or request.user.groups.filter(name__in=['Administradores', 'Gerentes']).exists()):
        messages.error(request, "Você não tem permissão para editar este carro.")
        return redirect('seller_dashboard')

    if request.method == 'POST':
        form = CarForm(request.POST, request.FILES, instance=car)
        if form.is_valid():
            form.save()
            messages.success(request, f"Carro '{car.modelo}' atualizado com sucesso!")
            return redirect('seller_dashboard')
    else:
        form = CarForm(instance=car)
    
    context = {
        'form': form,
        'action_type': 'Editar',
        'model_name': 'Carro'
    }
    return render(request, 'dashboard/car_form.html', context)

# NOVO: Views para CRUD de Carros (Deletar)
@login_required
@permission_required('cars.delete_car', raise_exception=True)
def delete_car_view(request, pk):
    car = get_object_or_404(Car, pk=pk)
    
    if car.vendedor != request.user and not (request.user.is_superuser or request.user.groups.filter(name__in=['Administradores', 'Gerentes']).exists()):
        messages.error(request, "Você não tem permissão para deletar este carro.")
        return redirect('seller_dashboard')

    if request.method == 'POST':
        car.delete()
        messages.success(request, f"Carro '{car.modelo}' deletado com sucesso!")
        return redirect('seller_dashboard')
    
    context = {
        'car': car,
        'model_name': 'Carro'
    }
    return render(request, 'dashboard/confirm_delete.html', context)

@method_decorator(login_required, name='dispatch')
class AllCarsManagementView(LoginRequiredMixin, ListView): # NOVA VIEW: Gerenciar todos os carros
    model = Car
    template_name = 'dashboard/all_cars_management.html' # Novo template
    context_object_name = 'all_cars_managed'
    paginate_by = 10

    # Método dispatch para lidar com permissões e redirecionamentos ANTES de get_queryset/get_context_data
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        # Se o usuário NÃO tem permissão para gerenciar todos os carros
        if not (user.is_superuser or \
                user.groups.filter(name__in=['Administradores', 'Gerentes']).exists() or \
                user.has_perm('cars.change_car') or \
                user.has_perm('cars.delete_car')):
            
            # Se for um vendedor sem permissões gerais, redireciona para o painel de "Meus Carros"
            if user.groups.filter(name='Vendedores').exists():
                messages.warning(request, "Você não tem permissão para gerenciar todos os carros. Redirecionado para 'Meus Carros'.")
                return redirect('seller_dashboard')
            else:
                # Para outros usuários sem permissão, mostra mensagem de erro e redireciona para o dashboard principal
                messages.error(request, "Você não tem permissão para acessar esta página.")
                return redirect('dashboard_home')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # Se o usuário chegou até aqui, ele tem permissão para ver todos os carros.
        return Car.objects.all().order_by('-data_cadastro')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_cars_managed'] = add_kilometragem_k(self.object_list) # Use self.object_list que é o resultado de get_queryset()
        user = self.request.user
        context['can_add_car'] = user.has_perm('cars.add_car')
        context['can_change_car'] = user.has_perm('cars.change_car')
        context['can_delete_car'] = user.has_perm('cars.delete_car')
        return context
    
    
@method_decorator(login_required, name='dispatch')
class DashboardHomeView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/dashboard_home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        is_admin_or_manager = user.is_superuser or user.groups.filter(name__in=['Administradores', 'Gerentes']).exists()
        is_seller = user.groups.filter(name='Vendedores').exists()
        is_inspector = user.groups.filter(name='Vistoriadores').exists()

        context['is_admin_or_manager'] = is_admin_or_manager
        context['is_seller'] = is_seller
        context['is_inspector'] = is_inspector

        context['lead_statuses'] = LeadInteraction.STATUS_INTERACTION_CHOICES

        if is_seller:
            all_leads = LeadInteraction.objects.filter(Q(vendedor=user) | Q(vendedor__isnull=True)).order_by('-ultima_atualizacao')
        elif is_admin_or_manager:
            all_leads = LeadInteraction.objects.all().order_by('-ultima_atualizacao')
        else:
            all_leads = LeadInteraction.objects.none()
        

        leads_by_status = {status_key: [] for status_key, status_label in LeadInteraction.STATUS_INTERACTION_CHOICES}
        for lead in all_leads:
            lead.carro.quilometragem_k = lead.carro.quilometragem / 1000
            lead.formatted_price = f"R${lead.carro.preco:.2f}"
            leads_by_status[lead.status].append(lead)
        
        context['leads_by_status'] = leads_by_status

        if is_admin_or_manager:
            context.update(get_admin_dashboard_data())
            today = datetime.now().date()
            start_of_month = today.replace(day=1)

        if is_seller:
            today = datetime.now().date()
            start_of_month = today.replace(day=1)
            
            seller_cars = Car.objects.filter(vendedor=user)
            context['seller_total_cars'] = seller_cars.count()
            context['seller_available_cars'] = seller_cars.filter(disponivel=True).count()

            seller_leads = LeadInteraction.objects.filter(vendedor=user)
            context['seller_total_leads'] = seller_leads.count()
            context['seller_new_leads_today'] = seller_leads.filter(data_interacao__date=today).count()
            context['seller_leads_in_negotiation'] = seller_leads.filter(status='Negociação').count()

            seller_sales = Sale.objects.filter(carro__vendedor=user)
            context['seller_total_sales_count'] = seller_sales.count()
            context['seller_total_sales_revenue'] = seller_sales.aggregate(total=Sum('preco_final'))['total'] or 0

            seller_monthly_sales = seller_sales.filter(data_venda__date__gte=start_of_month, data_venda__date__lte=today)
            context['seller_monthly_sales_count'] = seller_monthly_sales.count()
            context['seller_monthly_revenue'] = seller_monthly_sales.aggregate(total=Sum('preco_final'))['total'] or 0

            best_selling_car = seller_sales.values('carro__marca', 'carro__modelo').annotate(
                total_sold=Count('carro')
            ).order_by('-total_sold').first()
            context['seller_best_selling_car'] = best_selling_car['carro__marca'] + ' ' + best_selling_car['carro__modelo'] if best_selling_car else 'N/A'
            context['seller_best_selling_car_count'] = best_selling_car['total_sold'] if best_selling_car else 0

            context['seller_avg_closing_time'] = 'N/A'
            
            attended_leads = seller_leads.exclude(status__in=['Novo Contato', 'Fechado - Perdido']).count()
            context['seller_attended_customers'] = attended_leads
            
        return context
    
    
@method_decorator(login_required, name='dispatch')
class AdminOverviewView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/admin_overview.html'
    
    def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            context.update(get_admin_dashboard_data())
            return context
