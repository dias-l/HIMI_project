from django.contrib.admin import AdminSite
from django.contrib.auth.models import User


class HimiAdminSite(AdminSite):
    """
    Admin site personnalisé HIMI.
    Injecte les 4 querysets (Etudiants, Profs, Classes, Matières)
    directement dans le contexte de la page index pour afficher
    les 4 sections sur une seule page.
    """
    site_header = "HIMI Business School"
    site_title  = "HIMI Admin"
    index_title = "Administration"

    def index(self, request, extra_context=None):
        from gestion.models import Etudiant, Professeur, Classe, Matiere

        extra_context = extra_context or {}
        extra_context.update({
            'etudiants'   : Etudiant.objects.select_related('user', 'classe').order_by('user__last_name'),
            'professeurs' : Professeur.objects.select_related('user').prefetch_related('matieres', 'classes').order_by('user__last_name'),
            'classes'     : Classe.objects.all().order_by('nom'),
            'matieres'    : Matiere.objects.all().order_by('nom'),
        })
        return super().index(request, extra_context)


himi_admin_site = HimiAdminSite(name='admin')