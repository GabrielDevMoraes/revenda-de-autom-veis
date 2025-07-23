# cars/dashboard_urls.py

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Painel de Gestão Central
    path('', views.DashboardHomeView.as_view(), name='dashboard_home'),

    # Painel Específico do Vendedor (Meus Carros)
    path('my-cars/', views.SellerDashboardView.as_view(), name='seller_dashboard'),

    # Painel de Leads do Vendedor (CRM)
    path('leads/', views.LeadInteractionListView.as_view(), name='lead_interaction_list'),
    path('leads/<int:pk>/', views.lead_interaction_detail_and_update, name='lead_interaction_detail'),
    # URL para criar lead manualmente por vendedor (dashboard)
    path('leads/create-manual/', views.create_lead_interaction_manual, name='create_lead_interaction_manual'), 
    path('leads/claim/<int:pk>/', views.claim_lead, name='claim_lead'), # URL para reivindicar lead
    path('leads/whatsapp/<int:pk>/', views.initiate_whatsapp_conversation, name='initiate_whatsapp_conversation'), # NOVA URL para WhatsApp

    # Futuras URLs para Vistoriadores, Gerentes, Admins
    path('inspections/', views.InspectionListView.as_view(), name='inspection_list'),
    path('car-washes/', views.CarWashListView.as_view(), name='car_wash_list'),
    path('admin-overview/', views.AdminOverviewView.as_view(), name='admin_overview'),
]

