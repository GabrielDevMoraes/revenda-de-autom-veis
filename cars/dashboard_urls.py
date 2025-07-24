# cars/dashboard_urls.py

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Painel de Gestão Central
    path('', views.DashboardHomeView.as_view(), name='dashboard_home'),

    # Painel Específico do Vendedor (Meus Carros)
    path('my-cars/', views.SellerDashboardView.as_view(), name='seller_dashboard'),
    path('all-cars/', views.AllCarsManagementView.as_view(), name='all_cars_management'),

    # Painel de Leads do Vendedor (CRM)
    path('leads/', views.LeadInteractionListView.as_view(), name='lead_interaction_list'),
    path('leads/<int:pk>/', views.lead_interaction_detail_and_update, name='lead_interaction_detail'),
    path('leads/create-manual/', views.create_lead_interaction_manual, name='create_lead_interaction_manual'), 
    path('leads/claim/<int:pk>/', views.claim_lead, name='claim_lead'),
    path('leads/whatsapp/<int:pk>/', views.initiate_whatsapp_conversation, name='initiate_whatsapp_conversation'),
    path('leads/update-status-kanban/', views.update_lead_status_kanban, name='update_lead_status_kanban'), # URL para API Kanban

    # URLs para CRUD de Carros (ADICIONADAS/CONFIRMADAS)
    path('cars/add/', views.add_car_view, name='add_car'), 
    path('cars/edit/<int:pk>/', views.edit_car_view, name='edit_car'),
    path('cars/delete/<int:pk>/', views.delete_car_view, name='delete_car'),

    # URLs para Vistorias
    path('inspections/', views.InspectionListView.as_view(), name='inspection_list'),
    path('inspections/add/', views.add_inspection_view, name='add_inspection'),
    path('inspections/edit/<int:pk>/', views.edit_inspection_view, name='edit_inspection'),

    # URLs para Lavagens
    path('car-washes/', views.CarWashListView.as_view(), name='car_wash_list'),
    path('car-washes/add/', views.add_car_wash_view, name='add_car_wash'),
    path('car-washes/edit/<int:pk>/', views.edit_car_wash_view, name='edit_car_wash'),

    # URL para Admin/Gerente
    path('admin-overview/', views.AdminOverviewView.as_view(), name='admin_overview'),
]

