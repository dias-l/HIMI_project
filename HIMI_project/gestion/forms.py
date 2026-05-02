from django.db.models import Q
from django.contrib.auth.models import User
from .models import Message
from django import forms
from django.core.exceptions import ValidationError
from .models import Note, SupportCours, Etudiant

class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['etudiant', 'matiere', 'note_test', 'note_examen', 'note_rattrapage', 'appreciation']
        widgets = {
            'etudiant': forms.Select(attrs={'class': 'form-select'}),
            'matiere': forms.Select(attrs={'class': 'form-select'}),
            'note_test': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.25', 'min': '0', 'max': '12'}),
            'note_examen': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.25', 'min': '0', 'max': '8'}),
            'note_rattrapage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.25', 'min': '0', 'max': '20'}),
            'appreciation': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        professeur = kwargs.pop('professeur', None)
        super(NoteForm, self).__init__(*args, **kwargs)
        if professeur:
            self.fields['etudiant'].queryset = Etudiant.objects.filter(classe__in=professeur.classes.all())
            self.fields['matiere'].queryset = professeur.matieres.all()

    # Bug 7 corrigé — Validation des plages de notes
    def clean_note_test(self):
        val = self.cleaned_data.get('note_test')
        if val is not None and not (0 <= val <= 12):
            raise ValidationError("La note de test doit être comprise entre 0 et 12.")
        return val

    def clean_note_examen(self):
        val = self.cleaned_data.get('note_examen')
        if val is not None and not (0 <= val <= 8):
            raise ValidationError("La note d'examen doit être comprise entre 0 et 8.")
        return val

    def clean_note_rattrapage(self):
        val = self.cleaned_data.get('note_rattrapage')
        if val is not None and not (0 <= val <= 20):
            raise ValidationError("La note de rattrapage doit être comprise entre 0 et 20.")
        return val

class CoursForm(forms.ModelForm):
    class Meta:
        model = SupportCours
        fields = ['titre', 'fichier', 'matiere', 'classe']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control'}),
            'fichier': forms.FileInput(attrs={'class': 'form-control'}),
            'matiere': forms.Select(attrs={'class': 'form-select'}),
            'classe': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        professeur = kwargs.pop('professeur', None)
        super(CoursForm, self).__init__(*args, **kwargs)
        if professeur:
            self.fields['matiere'].queryset = professeur.matieres.all()
            self.fields['classe'].queryset = professeur.classes.all()

# Ajoute ce formulaire à la fin :
class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['destinataire', 'contenu']
        widgets = {
            'destinataire': forms.Select(attrs={'class': 'form-select'}),
            'contenu': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Écrivez votre message ici...'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(MessageForm, self).__init__(*args, **kwargs)

        if user:
            # 1. Si c'est un ÉTUDIANT : Il voit sa classe + ses profs
            if hasattr(user, 'profil_etudiant'):
                ma_classe = user.profil_etudiant.classe
                contacts_autorises = User.objects.filter(
                    Q(profil_etudiant__classe=ma_classe) | 
                    Q(profil_professeur__classes=ma_classe)
                ).exclude(id=user.id).distinct()
                self.fields['destinataire'].queryset = contacts_autorises

            # 2. Si c'est un PROFESSEUR : Il voit ses élèves
            elif hasattr(user, 'profil_professeur'):
                mes_classes = user.profil_professeur.classes.all()
                contacts_autorises = User.objects.filter(
                    profil_etudiant__classe__in=mes_classes
                ).exclude(id=user.id).distinct()
                self.fields['destinataire'].queryset = contacts_autorises