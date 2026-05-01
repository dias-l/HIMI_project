import os
import sys
import threading
import time
import webview
import ctypes
from django.core.management import execute_from_command_line

# --- LA MAGIE POUR WINDOWS ---
try:
    myappid = 'himi.business.school.app.1'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except Exception:
    pass

def run_django():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HIMI_project.settings')
    sys.argv = ['manage.py', 'runserver', '127.0.0.1:8000', '--noreload']
    execute_from_command_line(sys.argv)

def start_webview():
    time.sleep(3) # On attend que Django démarre
    
    # Chemin ABSOLU blindé vers ton icône
    base_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(base_dir, 'static', 'images', 'logo.ico')
    
    webview.create_window(
        title='HIMI Business School - Espace Numérique', 
        url='http://127.0.0.1:8000', 
        width=1280, 
        height=850,
        min_size=(1024, 768),
        confirm_close=True
    )
    
    webview.start(icon=icon_path)

if __name__ == '__main__':
    # Lance Django en tâche de fond (il se coupera tout seul en fermant la fenêtre)
    t = threading.Thread(target=run_django)
    t.daemon = True
    t.start()

    # Ouvre la belle fenêtre
    start_webview()