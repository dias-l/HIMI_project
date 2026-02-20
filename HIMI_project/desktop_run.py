import os
import sys
import threading
import time
import webview
from django.core.management import execute_from_command_line

# 1. Fonction pour démarrer le moteur Django en arrière-plan
def run_django():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HIMI_project.settings')
    sys.argv = ['manage.py', 'runserver', '127.0.0.1:8000', '--noreload']
    execute_from_command_line(sys.argv)

# 2. Fonction pour démarrer la fenêtre d'application (sans navigateur)
def start_webview():
    time.sleep(3) # On attend 3 secondes que Django chauffe
    # Crée la fenêtre de l'application
    webview.create_window('Gestion École', 'http://127.0.0.1:8000', width=1200, height=800)
    webview.start()

if __name__ == '__main__':
    # Lance le serveur local
    t = threading.Thread(target=run_django)
    t.daemon = True
    t.start()

    # Ouvre l'interface graphique native
    start_webview()