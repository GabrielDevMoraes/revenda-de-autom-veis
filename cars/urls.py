# cars/urls.py

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
    path('about/', views.AboutPageView.as_view(), name='about'),
    path('service/', views.ServicePageView.as_view(), name='service'),
    path('blog/', views.BlogPageView.as_view(), name='blog'),
    path('feature/', views.FeaturePageView.as_view(), name='feature'),
    path('team/', views.TeamPageView.as_view(), name='team'),
    path('testimonial/', views.TestimonialPageView.as_view(), name='testimonial'),
    path('cars/', views.CarListView.as_view(), name='car_list'),
    path('cars/<int:pk>/', views.CarDetailView.as_view(), name='car_detail'),
    path('contact/', views.contact_view, name='contact'),
    path('contact/success/', views.ContactSuccessView.as_view(), name='contact_success'), # Certifique-se de que esta URL está aqui para o redirecionamento
    path('404/', views.Custom404View.as_view(), name='404'),

    # URL para criar Lead a partir do formulário de interesse do cliente
    path('create-customer-lead/', views.create_customer_lead, name='create_customer_lead'), # <--- NOVA URL ADICIONADA

    # URLs de autenticação (login, logout) - Django padrão
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
]

