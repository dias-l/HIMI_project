from django.db import models
from django.contrib.auth.models import User

# --- 1. Structure ---
class Classe(models.Model):
    nom = models.CharField(max_length=50)
    def __str__(self): return self.nom

class Matiere(models.Model):
    nom = models.CharField(max_length=100)
    def __str__(self): return self.nom

# --- 2. Utilisateurs ---
class Etudiant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profil_etudiant')
    classe = models.ForeignKey(Classe, on_delete=models.PROTECT)
    date_naissance = models.DateField(null=True, blank=True)
    def __str__(self): return f"{self.user.last_name} {self.user.first_name}"

class Professeur(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profil_professeur')
    telephone = models.CharField(max_length=15)
    matieres = models.ManyToManyField(Matiere)
    classes = models.ManyToManyField(Classe) 
    def __str__(self): return f"Pr. {self.user.last_name}"

# --- 3. Notes & Moyennes ---
class Note(models.Model):
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE)
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE)
    professeur = models.ForeignKey(Professeur, on_delete=models.CASCADE)
    
    # Le nouveau système HIMI
    note_test = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, verbose_name="Test /12")
    note_examen = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, verbose_name="Examen /8")
    note_rattrapage = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, verbose_name="Rattrapage /20")
    
    appreciation = models.TextField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    # Cette fonction calcule la moyenne automatiquement !
    @property
    def moyenne(self):
        if self.note_rattrapage is not None:
            return self.note_rattrapage  # Le rattrapage écrase la note
            
        test = self.note_test if self.note_test else 0
        examen = self.note_examen if self.note_examen else 0
        
        # S'il y a au moins une note saisie, on fait l'addition
        if self.note_test is not None or self.note_examen is not None:
            return test + examen
        return None

    def __str__(self):
        return f"{self.etudiant} - {self.matiere}"

class Moyenne(models.Model):
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE)
    periode = models.CharField(max_length=50, default="Trimestre 1")
    valeur = models.DecimalField(max_digits=4, decimal_places=2)
    decision = models.CharField(max_length=50, blank=True)
    est_publie = models.BooleanField(default=False)

# --- 4. Outils ---
class CoursEmploiDuTemps(models.Model):
    JOURS = [('Lundi','Lundi'), ('Mardi','Mardi'), ('Mercredi','Mercredi'), ('Jeudi','Jeudi'), ('Vendredi','Vendredi')]
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE)
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE)
    professeur = models.ForeignKey(Professeur, on_delete=models.CASCADE)
    jour = models.CharField(max_length=10, choices=JOURS)
    heure_debut = models.TimeField()
    heure_fin = models.TimeField()
    salle = models.CharField(max_length=20, blank=True)
    date_modification = models.DateTimeField(auto_now=True)

class SupportCours(models.Model):
    titre = models.CharField(max_length=200)
    fichier = models.FileField(upload_to='cours/')
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE)
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE)
    professeur = models.ForeignKey(Professeur, on_delete=models.CASCADE)
    date_ajout = models.DateTimeField(auto_now_add=True)

class Actualite(models.Model):
    titre = models.CharField(max_length=200)
    contenu = models.TextField()
    date_publication = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='news/', blank=True, null=True)

# À rajouter à la fin de models.py

class Message(models.Model):
    expediteur = models.ForeignKey(User, related_name='messages_envoyes', on_delete=models.CASCADE)
    destinataire = models.ForeignKey(User, related_name='messages_recus', on_delete=models.CASCADE)
    contenu = models.TextField()
    date_envoi = models.DateTimeField(auto_now_add=True)
    lu = models.BooleanField(default=False)

    def __str__(self):
        return f"De {self.expediteur} à {self.destinataire} le {self.date_envoi.strftime('%d/%m/%Y')}"