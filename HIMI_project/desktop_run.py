import os
import sys
import threading
import time
import webview
from django.core.management import execute_from_command_line

# Fonction pour démarrer Django
def run_django():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HIMI_project.settings')
    # On force le port 8000
    sys.argv = ['manage.py', 'runserver', '127.0.0.1:8000', '--noreload']
    execute_from_command_line(sys.argv)

# Fonction pour démarrer la fenêtre Desktop
def start_webview():
    # On attend 3 secondes que Django soit prêt
    time.sleep(3)
    # On lance la fenêtre "Native"
    webview.create_window('Gestion École', 'http://127.0.0.1:8000', width=1200, height=800, resizable=True)
    webview.start()

if __name__ == '__main__':
    # 1. On lance Django en arrière-plan (Thread)
    t = threading.Thread(target=run_django)
    t.daemon = True
    t.start()

    # 2. On lance l'interface graphique
    start_webview()