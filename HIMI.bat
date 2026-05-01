@echo off
TITLE Application HIMI

:: 1. On se place dans le dossier
cd /d "%~dp0"

:: 2. On active l'environnement virtuel
call env\Scripts\activate

:: 3. On rentre dans le sous-dossier
cd HIMI_project

:: 4. On lance l'application en mode VRAIE APP (pythonw)
start pythonw desktop_run.py

:: 5. On ferme la fenêtre de lancement
exit