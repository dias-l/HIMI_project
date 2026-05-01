from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('gestion.urls')),  # On inclut les URLs de ton app 'gestion'
    path('accounts/', include('django.contrib.auth.urls')), # Pour le Login
]

# Ceci permet d'afficher les fichiers (images/PDF) en mode développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)