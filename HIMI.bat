@echo off
TITLE Application Gestion Ecole

:: 1. On se place dans le dossier
cd /d "%~dp0"

:: 2. On active l'environnement virtuel
call env\Scripts\activate

:: 3. On rentre dans le sous-dossier
cd HIMI_project

:: 4. On lance l'application en mode "Réduit" (invisible) grâce à "start /min"
start /min python desktop_run.py

:: 5. On ferme la première fenêtre noire automatiquement
exit