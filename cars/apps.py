# cars/apps.py

from django.apps import AppConfig


class CarsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cars' # O nome do seu aplicativo, deve ser 'cars' para corresponder à pasta
    verbose_name = 'Revenda de Carros' # Um nome mais amigável para o painel de administração
