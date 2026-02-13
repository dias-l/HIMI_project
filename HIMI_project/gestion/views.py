from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import NoteForm, CoursForm

def accueil(request):
    news = Actualite.objects.all().order_by('-date_publication')
    return render(request, 'gestion/accueil.html', {'actualites': news})

@login_required
def espace_notes(request):
    user = request.user
    context = {}
    
    if hasattr(user, 'profil_professeur'):
        prof = user.profil_professeur
        if request.method == 'POST':
            form = NoteForm(request.POST, professeur=prof)
            if form.is_valid():
                note = form.save(commit=False)
                note.professeur = prof
                note.save()
                return redirect('espace_notes')
        else:
            form = NoteForm(professeur=prof)
        context = {'role': 'prof', 'form': form, 'notes': Note.objects.filter(professeur=prof).order_by('-date')}
    
    elif hasattr(user, 'profil_etudiant'):
        return redirect('mon_bulletin')

    return render(request, 'gestion/notes.html', context)

@login_required
def mon_bulletin(request):
    user = request.user
    if not hasattr(user, 'profil_etudiant'): return redirect('accueil')
    
    etudiant = user.profil_etudiant
    matieres = Matiere.objects.filter(professeur__classes=etudiant.classe).distinct()
    bulletin = []
    
    for matiere in matieres:
        note = Note.objects.filter(etudiant=etudiant, matiere=matiere).first()
        bulletin.append({
            'matiere': matiere.nom,
            'note': note.valeur if note else None,
            'appreciation': note.appreciation if note else "En attente",
            'coefficient': note.coefficient if note else 1,
        })
        
    moyenne = Moyenne.objects.filter(etudiant=etudiant, est_publie=True).first()
    return render(request, 'gestion/bulletin.html', {'etudiant': etudiant, 'bulletin': bulletin, 'moyenne_generale': moyenne})

@login_required
def emploi_du_temps(request):
    planning = []
    if hasattr(request.user, 'profil_etudiant'):
        planning = CoursEmploiDuTemps.objects.filter(classe=request.user.profil_etudiant.classe)
    elif hasattr(request.user, 'profil_professeur'):
        planning = CoursEmploiDuTemps.objects.filter(professeur=request.user.profil_professeur)
    return render(request, 'gestion/emploi_du_temps.html', {'planning': planning})

@login_required
def liste_cours_pdf(request):
    cours = []
    if hasattr(request.user, 'profil_etudiant'):
        cours = SupportCours.objects.filter(classe=request.user.profil_etudiant.classe)
    elif hasattr(request.user, 'profil_professeur'):
        cours = SupportCours.objects.filter(professeur=request.user.profil_professeur)
    return render(request, 'gestion/cours_pdf.html', {'cours': cours})

@login_required
def ajouter_cours(request):
    if not hasattr(request.user, 'profil_professeur'): return redirect('accueil')
    prof = request.user.profil_professeur
    
    if request.method == 'POST':
        form = CoursForm(request.POST, request.FILES, professeur=prof)
        if form.is_valid():
            c = form.save(commit=False)
            c.professeur = prof
            c.save()
            return redirect('liste_cours_pdf')
    else:
        form = CoursForm(professeur=prof)
    return render(request, 'gestion/ajouter_cours.html', {'form': form})