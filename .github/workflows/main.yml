#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import shutil
import platform
from pathlib import Path
from datetime import datetime

class KITTTerminalInstaller:
    def __init__(self):
        self.home = Path.home()
        self.kitt_dir = self.home / ".kitt"
        self.modelfile_url = "https://raw.githubusercontent.com/doctotypetech-dotcom/KITT/main/Modelfile"
        self.main_url = "https://raw.githubusercontent.com/doctotypetech-dotcom/KITT/main/main.py"
        self.system = platform.system()

    def log(self, level, message):
        """Affiche des logs avec horodatage et niveau de priorité"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = {
            "INFO":  "\033[94m[INFO]\033[0m",    # Bleu
            "STEP":  "\033[92m[ÉTAP]\033[0m",    # Vert
            "WARN":  "\033[93m[WARN]\033[0m",    # Jaune
            "ERROR": "\033[91m[ERR ]\033[0m",    # Rouge
            "CURL":  "\033[95m[CURL]\033[0m"     # Magenta
        }
        print(f"[{timestamp}] {prefix.get(level, level)} {message}", flush=True)

    def fn_run_command(self, cmd, desc):
        """Exécute une commande système avec affichage direct du flux"""
        self.log("STEP", f"Lancement : {desc}")
        self.log("INFO", f"Commande : {cmd}")
        
        # On utilise subprocess.run sans capture pour que le flux (curl, ollama)
        # s'affiche directement dans le terminal de l'utilisateur.
        result = subprocess.run(cmd, shell=True)
        
        if result.returncode != 0:
            self.log("ERROR", f"La commande a échoué avec le code {result.returncode}")
            sys.exit(result.returncode)
        else:
            self.log("INFO", "Succès ✅")

    def fn_install(self):
        print("\n" + "="*60)
        print("    KITT SYSTEM INSTALLER - MODE VERBOSE -v+++")
        print("="*60 + "\n")

        # 1. Préparation Environnement
        self.log("STEP", f"Système : {self.system}")
        if not self.kitt_dir.exists():
            self.log("INFO", f"Création du répertoire {self.kitt_dir}")
            self.kitt_dir.mkdir(parents=True, exist_ok=True)
        
        # 2. Téléchargement Modelfile
        self.log("CURL", "Récupération du Modelfile (GitHub -> Local)")
        # -v : Verbose, -L : Suit les redirections, -f : Échoue si 404
        cmd_curl_model = f'curl -vLf "{self.modelfile_url}" -o "{self.kitt_dir}/Modelfile"'
        self.fn_run_command(cmd_curl_model, "Téléchargement Modelfile")

        # 3. Téléchargement main.py
        self.log("CURL", "Récupération du script principal main.py")
        cmd_curl_main = f'curl -vLf "{self.main_url}" -o "{self.kitt_dir}/main.py"'
        self.fn_run_command(cmd_curl_main, "Téléchargement main.py")
        os.chmod(self.kitt_dir / "main.py", 0o755)

        # 4. Vérification Ollama
        self.log("STEP", "Vérification de l'infrastructure Ollama")
        if not shutil.which("ollama"):
            self.log("WARN", "Ollama non détecté. Tentative d'installation automatique...")
            self.fn_run_command("curl -fsSL https://ollama.ai/install.sh | sh", "Installation Ollama")
        else:
            self.log("INFO", "Ollama est déjà installé.")

        # 5. Pull du modèle de base
        self.log("STEP", "Synchronisation avec le modèle Llama 3.2 (3B)")
        self.fn_run_command("ollama pull llama3.2:3b", "Ollama Pull")

        # 6. Création de l'IA KITT
        self.log("STEP", "Initialisation de l'IA KITT-AI")
        cmd_create = f'ollama create kitt-ai -f "{self.kitt_dir}/Modelfile"'
        self.fn_run_command(cmd_create, "Ollama Create")

        # 7. Compilation (Dépend de l'OS)
        self.log("STEP", "Phase de compilation finale")
        os.chdir(self.kitt_dir)
        
        if self.system == "Darwin":
            self.log("INFO", "Cible détectée : macOS (.app)")
            self.fn_run_command(f'"{sys.executable}" -m pip install py2app --break-system-packages', "Install py2app")
            if os.path.exists("setup.py"): os.remove("setup.py")
            self.fn_run_command("py2applet --make-setup main.py", "Génération setup.py")
            self.fn_run_command(f'"{sys.executable}" setup.py py2app -A', "Compilation py2app")
            
            app_dest = self.home / "Applications" / "KITT.app"
            self.log("INFO", f"Déplacement vers {app_dest}")
            if app_dest.exists(): shutil.rmtree(app_dest)
            shutil.move("dist/main.app", str(app_dest))
        else:
            self.log("INFO", "Cible détectée : Linux (Binaire)")
            self.fn_run_command(f'"{sys.executable}" -m pip install pyinstaller --break-system-packages', "Install PyInstaller")
            self.fn_run_command("pyinstaller --onefile --noconsole main.py", "Compilation PyInstaller")
            shutil.copy2("dist/main", str(self.home / "Desktop" / "KITT"))

        print("\n" + "="*60)
        print("✅ INSTALLATION TERMINÉE AVEC SUCCÈS")
        print(f"📁 Dossier de travail : {self.kitt_dir}")
        print("="*60 + "\n")

if __name__ == "__main__":
    installer = KITTTerminalInstaller()
    installer.fn_install()
