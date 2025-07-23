# mycarreseller/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
import os

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('cars.urls')), # URLs do site público
    path('dashboard/', include('cars.dashboard_urls')), # URLs do painel de gestão
]

# Adiciona configuração para servir arquivos de mídia e estáticos durante o desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=os.path.join(settings.BASE_DIR, 'static'))

