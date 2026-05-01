from django.urls import path
from . import views

urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('notes/', views.espace_notes, name='espace_notes'),
    path('bulletin/', views.mon_bulletin, name='mon_bulletin'),
    path('planning/', views.emploi_du_temps, name='emploi_du_temps'),
    path('cours/', views.liste_cours_pdf, name='liste_cours_pdf'),
    path('cours/ajouter/', views.ajouter_cours, name='ajouter_cours'),
    path('messagerie/', views.messagerie, name='messagerie'),
    path('messagerie/nouveau/', views.nouveau_message, name='nouveau_message'),
    path('messagerie/chat/<int:user_id>/', views.discussion, name='discussion'),
    path('infos-himi/', views.infos_etablissement, name='infos_himi'),
]