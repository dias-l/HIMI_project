from django import forms
from .models import Note, SupportCours, Etudiant

class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['etudiant', 'matiere', 'valeur', 'coefficient', 'appreciation']
        widgets = {
            'etudiant': forms.Select(attrs={'class': 'form-select'}),
            'matiere': forms.Select(attrs={'class': 'form-select'}),
            'valeur': forms.NumberInput(attrs={'class': 'form-control'}),
            'coefficient': forms.NumberInput(attrs={'class': 'form-control'}),
            'appreciation': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        professeur = kwargs.pop('professeur', None)
        super(NoteForm, self).__init__(*args, **kwargs)
        if professeur:
            self.fields['etudiant'].queryset = Etudiant.objects.filter(classe__in=professeur.classes.all())
            self.fields['matiere'].queryset = professeur.matieres.all()

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