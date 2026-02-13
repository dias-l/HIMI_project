from django.contrib import admin
from .models import *

class MoyenneAdmin(admin.ModelAdmin):
    list_display = ('etudiant', 'valeur', 'decision', 'est_publie')
    list_editable = ('est_publie', 'decision')
    list_filter = ('est_publie', 'etudiant__classe')

class ProfesseurAdmin(admin.ModelAdmin):
    filter_horizontal = ('matieres', 'classes')

admin.site.register(Classe)
admin.site.register(Matiere)
admin.site.register(Etudiant)
admin.site.register(Professeur, ProfesseurAdmin)
admin.site.register(Note)
admin.site.register(CoursEmploiDuTemps)
admin.site.register(SupportCours)
admin.site.register(Actualite)
admin.site.register(Moyenne, MoyenneAdmin)
