# cars/views.py

from django.shortcuts import render, get_object_or_404, redirect
from .models import Car, Vistoria, Lavagem, LeadInteraction, Customer, Sale
from .forms import LeadInteractionForm
from django.views.generic import ListView, DetailView, TemplateView, View
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.db.models import Q, Sum, Avg, Count
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
import random
from datetime import datetime, timedelta
import urllib.parse # Para codificar o texto do WhatsApp

# Função auxiliar para adicionar a quilometragem em "K" aos objetos Carro
def add_kilometragem_k(cars_queryset):
    """
    Adiciona um atributo 'quilometragem_k' a cada objeto Carro
    no queryset, representando a quilometragem em milhares.
    """
    for car in cars_queryset:
        car.quilometragem_k = car.quilometragem / 1000
    return cars_queryset

# Função auxiliar para coletar dados do dashboard de administrador/gerente
def get_admin_dashboard_data():
    """
    Coleta dados de visão geral da empresa para administradores/gerentes.
    """
    total_cars = Car.objects.count()
    available_cars = Car.objects.filter(disponivel=True).count()
    total_sales = Sale.objects.count()
    total_revenue = Sale.objects.aggregate(total=Sum('preco_final'))['total'] or 0
    total_leads = LeadInteraction.objects.count()
    new_leads_today = LeadInteraction.objects.filter(data_interacao__date=datetime.now().date()).count()

    return {
        'total_cars': total_cars,
        'available_cars': available_cars,
        'total_sales': total_sales,
        'total_revenue': total_revenue,
        'total_leads': total_leads,
        'new_leads_today': new_leads_today,
    }

# View para a página inicial (index.html)
class HomePageView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        latest_cars = Car.objects.filter(disponivel=True).order_by('-data_cadastro')[:4]
        context['latest_cars'] = add_kilometragem_k(latest_cars)
        return context


# View para a página de listagem de carros (cars.html)
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

# View para a página de detalhes do carro
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

# View para a página "Sobre Nós" (about.html)
class AboutPageView(TemplateView):
    template_name = 'about.html'

# View para a página de serviços (service.html)
class ServicePageView(TemplateView):
    template_name = 'service.html'

# View para a página de blog (blog.html)
class BlogPageView(TemplateView):
    template_name = 'blog.html'

# View para a página de recursos (feature.html)
class FeaturePageView(TemplateView):
    template_name = 'feature.html'

# View para a página de equipe (team.html)
class TeamPageView(TemplateView):
    template_name = 'team.html'

# View para a página de depoimentos (testimonial.html)
class TestimonialPageView(TemplateView):
    template_name = 'testimonial.html'

# View para a página 404 (404.html)
class Custom404View(TemplateView):
    template_name = '404.html'

# View para a página de sucesso do contato
class ContactSuccessView(TemplateView):
    template_name = 'contact_success.html'

# View para a página de contato (contact.html) - Mantida para contatos gerais
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
                ['your_email@example.com'], # E-mail para onde a mensagem será enviada (substitua pelo seu e-mail)
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

# View para criar Lead a partir do formulário de interesse do cliente (AGORA SEM VENDEDOR INICIAL)
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
def create_lead_interaction_manual(request): # Renomeada para clareza (manual)
    """
    View para criar uma nova interação de lead manualmente por um vendedor logado.
    """
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
                customer.nome_tempo = customer_name # Erro de digitação aqui: customer_tempo -> nome_completo
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
    """
    Permite que um vendedor logado reivindique um lead não atribuído.
    """
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
    """
    Redireciona para o WhatsApp com mensagem pré-preenchida e atualiza o status do lead.
    """
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

    # Constrói a mensagem pré-preenchida
    whatsapp_message = f"Olá {lead_interaction.cliente.nome_completo}! Meu nome é {user.get_full_name() or user.username} da Cental. Vi seu interesse no carro {lead_interaction.carro.marca} {lead_interaction.carro.modelo} ({lead_interaction.carro.ano}) disponível por R${lead_interaction.carro.preco:.2f}. Posso ajudar com alguma dúvida?" # Corrigido a formatação do preço
    encoded_message = urllib.parse.quote(whatsapp_message)

    whatsapp_url = f"https://wa.me/{lead_interaction.cliente.whatsapp_number}?text={encoded_message}"
    
    return redirect(whatsapp_url)


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
class InspectionListView(LoginRequiredMixin, ListView):
    model = Vistoria
    template_name = 'dashboard/inspection_list.html'
    context_object_name = 'inspections'
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.groups.filter(name__in=['Administradores', 'Gerentes', 'Vendedores']).exists():
            return Vistoria.objects.all().order_by('-data_vistoria')
        elif user.groups.filter(name='Vistoriadores').exists():
            return Vistoria.objects.filter(vistoriador=user).order_by('-data_vistoria')
        return Vistoria.objects.none()

@method_decorator(login_required, name='dispatch')
class CarWashListView(LoginRequiredMixin, ListView):
    model = Lavagem
    template_name = 'dashboard/car_wash_list.html'
    context_object_name = 'car_washes'
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.groups.filter(name__in=['Administradores', 'Gerentes', 'Vendedores']).exists():
            return Lavagem.objects.all().order_by('-data_lavagem')
        elif user.groups.filter(name__in=['Vistoriadores', 'Lavadores']).exists():
            return Lavagem.objects.filter(responsavel=user).order_by('-data_lavagem')
        return Lavagem.objects.none()

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

        if is_admin_or_manager:
            context.update(get_admin_dashboard_data())

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
