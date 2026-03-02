from .models import Note, Moyenne
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import NoteForm, CoursForm
from django.db.models import Q
from .models import Message
from .forms import MessageForm

@login_required
def accueil(request):
    user = request.user
    notifications = []
    
    # 1. ACTUALITÉS (Pour tout le monde)
    annonces = Actualite.objects.order_by('-date_publication')[:5]
    
    if hasattr(user, 'profil_etudiant'):
        etudiant = user.profil_etudiant
        classe = etudiant.classe
        
        # --- NOTIFICATIONS : PRIORITÉ 1 (MESSAGES NON LUS) ---
        messages_non_lus = Message.objects.filter(destinataire=user, lu=False).order_by('-date_envoi')[:3]
        for msg in messages_non_lus:
            notifications.append({
                'priorite': 1,
                'icone': '💬',
                'titre': f"Nouveau message de {msg.expediteur.first_name}",
                'texte': msg.contenu[:30] + '...',
                'date': msg.date_envoi,
                'lien': 'messagerie'
            })

        # --- NOTIFICATIONS : PRIORITÉ 2 (PLANNING MODIFIÉ) ---
        # On prend les 2 dernières modifications de la classe
        plannings = CoursEmploiDuTemps.objects.filter(classe=classe).order_by('-date_modification')[:2]
        for plan in plannings:
            notifications.append({
                'priorite': 2,
                'icone': '📅',
                'titre': f"Planning modifié : {plan.matiere.nom}",
                'texte': f"{plan.jour} ({plan.heure_debut.strftime('%H:%M')})",
                'date': plan.date_modification,
                'lien': 'emploi_du_temps'
            })

        # --- NOTIFICATIONS : PRIORITÉ 3 (NOUVEAUX COURS) ---
        cours = SupportCours.objects.filter(classe=classe).order_by('-date_ajout')[:3]
        for c in cours:
            notifications.append({
                'priorite': 3,
                'icone': '📚',
                'titre': f"Nouveau cours : {c.matiere.nom}",
                'texte': c.titre,
                'date': c.date_ajout,
                'lien': 'liste_cours_pdf'
            })

        # --- NOTIFICATIONS : PRIORITÉ 4 (NOUVELLES NOTES) ---
        notes = Note.objects.filter(etudiant=etudiant).order_by('-date')[:3]
        for n in notes:
            moyenne_str = f"{n.moyenne}/20" if n.moyenne is not None else "Saisie"
            notifications.append({
                'priorite': 4,
                'icone': '🎓',
                'titre': f"Nouvelle note : {n.matiere.nom}",
                'texte': moyenne_str,
                'date': n.date,
                'lien': 'mon_bulletin'
            })

        # --- TRI MAGIQUE ---
        # On trie d'abord par priorité (1, puis 2, puis 3...), et ensuite par date (du plus récent au plus ancien)
        notifications.sort(key=lambda x: (x['priorite'], -x['date'].timestamp()))
        
        # On ne garde que les 6 premières notifications pour ne pas surcharger l'écran
        notifications = notifications[:6]
        
        context = {
            'role': 'etudiant',
            'profil': etudiant,
            'notifications': notifications,
            'annonces': annonces
        }
        return render(request, 'gestion/accueil.html', context)
        
    elif hasattr(user, 'profil_professeur'):
        # Logique professeur (on garde la tienne)
        professeur = user.profil_professeur
        context = {
            'role': 'professeur',
            'profil': professeur,
            'annonces': annonces
        }
        return render(request, 'gestion/accueil.html', context)

@login_required
def espace_notes(request):
    user = request.user
    context = {}
    
    if hasattr(user, 'profil_professeur'):
        prof = user.profil_professeur
        
        if request.method == 'POST':
            form = NoteForm(request.POST)
            
            if form.is_valid():
                # On récupère l'étudiant et la matière PROPREMENT via Django
                etud = form.cleaned_data.get('etudiant')
                mat = form.cleaned_data.get('matiere')
                
                # On cherche si cette ligne existe déjà
                note_existante = Note.objects.filter(etudiant=etud, matiere=mat).first()
                
                if note_existante:
                    # ♻️ MISE À JOUR : On remplace les anciennes valeurs
                    note_existante.note_test = form.cleaned_data.get('note_test')
                    note_existante.note_examen = form.cleaned_data.get('note_examen')
                    note_existante.note_rattrapage = form.cleaned_data.get('note_rattrapage')
                    note_existante.appreciation = form.cleaned_data.get('appreciation')
                    note_existante.professeur = prof
                    note_existante.save()
                else:
                    # 🆕 CRÉATION : C'est une toute nouvelle note
                    note = form.save(commit=False)
                    note.professeur = prof
                    note.save()
                    
                # On recharge la page pour vider le formulaire
                return redirect('espace_notes')
        else:
            form = NoteForm()
            
        context['form'] = form
        context['notes'] = Note.objects.filter(professeur=prof).order_by('-date')
        return render(request, 'gestion/espace_notes.html', context)
        
    return redirect('accueil')

@login_required
def mon_bulletin(request):
    user = request.user
    context = {}
    
    if hasattr(user, 'profil_etudiant'):
        etudiant = user.profil_etudiant
        notes = Note.objects.filter(etudiant=etudiant).order_by('matiere__nom')
        
        # On va chercher la moyenne officielle saisie par l'admin.
        # .first() permet de prendre la dernière ou la seule moyenne publiée pour cet étudiant.
        moyenne_officielle = Moyenne.objects.filter(etudiant=etudiant, est_publie=True).order_by('-id').first()
        
        context = {
            'role': 'etudiant',
            'etudiant': etudiant,
            'notes': notes,
            'moyenne_semestre': moyenne_officielle # On envoie l'objet entier au template
        }
        return render(request, 'gestion/bulletin.html', context)
        
    return redirect('accueil')

@login_required
def emploi_du_temps(request):
    planning = []
    role = None # On crée une variable pour stocker le rôle
    
    # Si c'est un étudiant
    if hasattr(request.user, 'profil_etudiant'):
        etudiant = request.user.profil_etudiant
        planning = CoursEmploiDuTemps.objects.filter(classe=etudiant.classe)
        role = 'etudiant'
        
    # Si c'est un professeur
    elif hasattr(request.user, 'profil_professeur'):
        prof = request.user.profil_professeur
        planning = CoursEmploiDuTemps.objects.filter(professeur=prof)
        role = 'professeur'
        
    return render(request, 'gestion/emploi_du_temps.html', {
        'planning': planning,
        'role': role  # On envoie le rôle au fichier HTML
    })

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

# --- VUES MESSAGERIE ---

@login_required
def messagerie(request):
    # Récupérer tous les messages où l'utilisateur est impliqué
    messages = Message.objects.filter(
        Q(expediteur=request.user) | Q(destinataire=request.user)
    ).order_by('-date_envoi')
    
    # Extraire les contacts uniques
    contacts = []
    vus = set()
    for msg in messages:
        contact = msg.destinataire if msg.expediteur == request.user else msg.expediteur
        if contact.id not in vus:
            vus.add(contact.id)
            contacts.append(contact)
            
    return render(request, 'gestion/messagerie.html', {'contacts': contacts})

@login_required
def nouveau_message(request):
    if request.method == 'POST':
        form = MessageForm(request.POST, user=request.user)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.expediteur = request.user
            msg.save()
            return redirect('discussion', user_id=msg.destinataire.id)
    else:
        form = MessageForm(user=request.user)
    return render(request, 'gestion/nouveau_message.html', {'form': form})

@login_required
def discussion(request, user_id):
    contact = User.objects.get(id=user_id)
    
    # Marquer les messages reçus comme "lus"
    Message.objects.filter(expediteur=contact, destinataire=request.user, lu=False).update(lu=True)
    
    if request.method == 'POST':
        contenu = request.POST.get('contenu')
        if contenu:
            Message.objects.create(expediteur=request.user, destinataire=contact, contenu=contenu)
            return redirect('discussion', user_id=user_id)

    # Récupérer l'historique du chat
    historique = Message.objects.filter(
        Q(expediteur=request.user, destinataire=contact) |
        Q(expediteur=contact, destinataire=request.user)
    ).order_by('date_envoi')
    
    # --- NOUVEAU : On récupère aussi la liste des contacts pour la barre de gauche ---
    messages_all = Message.objects.filter(
        Q(expediteur=request.user) | Q(destinataire=request.user)
    ).order_by('-date_envoi')
    
    contacts = []
    vus = set()
    for msg in messages_all:
        c = msg.destinataire if msg.expediteur == request.user else msg.expediteur
        if c.id not in vus:
            vus.add(c.id)
            contacts.append(c)
            
    # On envoie 'contacts' en plus à la page !
    return render(request, 'gestion/discussion.html', {
        'contact': contact, 
        'messages': historique,
        'contacts': contacts 
    })

@login_required
def infos_etablissement(request):
    return render(request, 'gestion/infos_himi.html')