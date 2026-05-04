from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from gestion.admin_site import himi_admin_site

# Importer admin.py pour déclencher l'enregistrement des modèles
import gestion.admin  # noqa

urlpatterns = [
    path('admin/', himi_admin_site.urls),
    path('', include('gestion.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)