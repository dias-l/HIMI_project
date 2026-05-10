from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User, Group
from django import forms
from .admin_site import himi_admin_site
from .models import (
    Classe, Matiere, Etudiant, Professeur,
    Note, Moyenne, CoursEmploiDuTemps, SupportCours,
    Actualite, Message,
)


# ════════════════════════════════════════════════════════
#  FORMULAIRES INLINE — User + Etudiant/Professeur en 1 étape
# ════════════════════════════════════════════════════════

class EtudiantInlineForm(forms.ModelForm):
    class Meta:
        model = Etudiant
        fields = ['classe', 'date_naissance']
        widgets = {
            'date_naissance': forms.DateInput(attrs={'type': 'date'}),
        }

class ProfesseurInlineForm(forms.ModelForm):
    class Meta:
        model = Professeur
        fields = ['telephone', 'matieres', 'classes']


class EtudiantInline(admin.StackedInline):
    model = Etudiant
    form = EtudiantInlineForm
    can_delete = False
    verbose_name = "Profil Etudiant"
    verbose_name_plural = "Profil Etudiant"
    extra = 0
    filter_horizontal = ()


class ProfesseurInline(admin.StackedInline):
    model = Professeur
    form = ProfesseurInlineForm
    can_delete = False
    verbose_name = "Profil Professeur"
    verbose_name_plural = "Profil Professeur"
    extra = 0
    filter_horizontal = ('matieres', 'classes')


# ════════════════════════════════════════════════════════
#  USER ADMIN
# ════════════════════════════════════════════════════════

class HimiUserAdmin(BaseUserAdmin):
    inlines = [EtudiantInline, ProfesseurInline]
    list_display = ('username', 'first_name', 'last_name', 'email', 'get_role', 'is_active')
    list_filter  = ('is_active', 'is_staff')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('last_name', 'first_name')

    fieldsets = (
        ("Identifiants de connexion", {
            'fields': ('username', 'password')
        }),
        ("Informations personnelles", {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ("Acces et permissions", {
            'fields': ('is_active', 'is_staff', 'is_superuser'),
            'classes': ('collapse',),
        }),
    )

    add_fieldsets = (
        ("Compte", {
            'classes': ('wide',),
            'fields': ('username', 'first_name', 'last_name', 'email', 'password1', 'password2'),
        }),
    )

    def get_role(self, obj):
        if hasattr(obj, 'profil_etudiant'):
            return 'Etudiant'
        elif hasattr(obj, 'profil_professeur'):
            return 'Professeur'
        elif obj.is_superuser:
            return 'Administrateur'
        return '—'
    get_role.short_description = 'Role'


admin.site.unregister(User)
admin.site.register(User, HimiUserAdmin)


# ════════════════════════════════════════════════════════
#  CLASSES & MATIERES
# ════════════════════════════════════════════════════════

@admin.register(Classe)
class ClasseAdmin(admin.ModelAdmin):
    list_display  = ('nom', 'nb_etudiants')
    search_fields = ('nom',)
    ordering      = ('nom',)

    def nb_etudiants(self, obj):
        return obj.etudiant_set.count()
    nb_etudiants.short_description = 'Nb etudiants'


@admin.register(Matiere)
class MatiereAdmin(admin.ModelAdmin):
    list_display  = ('nom',)
    search_fields = ('nom',)
    ordering      = ('nom',)


# ════════════════════════════════════════════════════════
#  ETUDIANTS & PROFESSEURS
# ════════════════════════════════════════════════════════

@admin.register(Etudiant)
class EtudiantAdmin(admin.ModelAdmin):
    list_display  = ('nom_complet', 'classe', 'date_naissance')
    list_filter   = ('classe',)
    search_fields = ('user__first_name', 'user__last_name', 'user__username')
    ordering      = ('user__last_name',)
    # autocomplete_fields supprimé car conflictue avec le site admin personnalisé

    def nom_complet(self, obj):
        return f"{obj.user.last_name} {obj.user.first_name}"
    nom_complet.short_description = 'Nom complet'


@admin.register(Professeur)
class ProfesseurAdmin(admin.ModelAdmin):
    list_display      = ('nom_complet', 'telephone', 'liste_matieres', 'liste_classes')
    search_fields     = ('user__first_name', 'user__last_name', 'telephone')
    filter_horizontal = ('matieres', 'classes')
    ordering          = ('user__last_name',)

    def nom_complet(self, obj):
        return str(obj)
    nom_complet.short_description = 'Professeur'

    def liste_matieres(self, obj):
        return ', '.join(m.nom for m in obj.matieres.all()) or '—'
    liste_matieres.short_description = 'Matieres'

    def liste_classes(self, obj):
        return ', '.join(c.nom for c in obj.classes.all()) or '—'
    liste_classes.short_description = 'Classes'


# ════════════════════════════════════════════════════════
#  NOTES & MOYENNES
# ════════════════════════════════════════════════════════

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display  = ('etudiant', 'matiere', 'professeur', 'note_test', 'note_examen', 'note_rattrapage', 'get_moyenne')
    list_filter   = ('matiere', 'etudiant__classe')
    search_fields = ('etudiant__user__last_name', 'matiere__nom')
    ordering      = ('-date',)
    date_hierarchy = 'date'

    def get_moyenne(self, obj):
        return obj.moyenne if obj.moyenne is not None else '—'
    get_moyenne.short_description = 'Moyenne /20'


@admin.register(Moyenne)
class MoyenneAdmin(admin.ModelAdmin):
    list_display  = ('etudiant', 'periode', 'valeur', 'decision', 'est_publie')
    list_editable = ('est_publie', 'decision')
    list_filter   = ('est_publie', 'etudiant__classe', 'periode')
    search_fields = ('etudiant__user__last_name',)
    ordering      = ('etudiant__user__last_name',)


# ════════════════════════════════════════════════════════
#  EMPLOI DU TEMPS & COURS
# ════════════════════════════════════════════════════════

@admin.register(CoursEmploiDuTemps)
class CoursEmploiDuTempsAdmin(admin.ModelAdmin):
    list_display  = ('classe', 'matiere', 'professeur', 'jour', 'heure_debut', 'heure_fin', 'salle')
    list_filter   = ('jour', 'classe', 'matiere')
    search_fields = ('classe__nom', 'matiere__nom', 'professeur__user__last_name')
    ordering      = ('classe', 'jour', 'heure_debut')


@admin.register(SupportCours)
class SupportCoursAdmin(admin.ModelAdmin):
    list_display  = ('titre', 'matiere', 'classe', 'professeur', 'date_ajout')
    list_filter   = ('matiere', 'classe')
    search_fields = ('titre', 'matiere__nom')
    ordering      = ('-date_ajout',)


# ════════════════════════════════════════════════════════
#  COMMUNICATION
# ════════════════════════════════════════════════════════

@admin.register(Actualite)
class ActualiteAdmin(admin.ModelAdmin):
    list_display  = ('titre', 'date_publication')
    search_fields = ('titre', 'contenu')
    ordering      = ('-date_publication',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display    = ('expediteur', 'destinataire', 'date_envoi', 'lu')
    list_filter     = ('lu',)
    search_fields   = ('expediteur__last_name', 'destinataire__last_name')
    ordering        = ('-date_envoi',)
    readonly_fields = ('date_envoi',)


# ════════════════════════════════════════════════════════
#  ENREGISTREMENT SUR himi_admin_site
# ════════════════════════════════════════════════════════

himi_admin_site.register(User,               HimiUserAdmin)
himi_admin_site.register(Group)
himi_admin_site.register(Classe,             ClasseAdmin)
himi_admin_site.register(Matiere,            MatiereAdmin)
himi_admin_site.register(Etudiant,           EtudiantAdmin)
himi_admin_site.register(Professeur,         ProfesseurAdmin)
himi_admin_site.register(Note,               NoteAdmin)
himi_admin_site.register(Moyenne,            MoyenneAdmin)
himi_admin_site.register(CoursEmploiDuTemps, CoursEmploiDuTempsAdmin)
himi_admin_site.register(SupportCours,       SupportCoursAdmin)
himi_admin_site.register(Actualite,          ActualiteAdmin)
himi_admin_site.register(Message,            MessageAdmin)