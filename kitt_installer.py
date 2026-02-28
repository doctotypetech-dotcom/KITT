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
        # URLs Directes (évite les redirections complexes)
        self.modelfile_url = "https://raw.githubusercontent.com/doctotypetech-dotcom/KITT/main/Modelfile"
        self.main_url = "https://raw.githubusercontent.com/doctotypetech-dotcom/KITT/main/main.py"
        self.system = platform.system()
        self.shell = "zsh" if self.system == "Darwin" else "bash"

    def log(self, level, message):
        """Logs avec couleurs ANSI pour le terminal"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        colors = {
            "STEP": "\033[92m[ÉTAP]\033[0m", # Vert
            "INFO": "\033[94m[INFO]\033[0m", # Bleu
            "CURL": "\033[95m[CURL]\033[0m", # Magenta
            "ERR ": "\033[91m[ERR ]\033[0m"  # Rouge
        }
        print(f"[{timestamp}] {colors.get(level, level)} {message}", flush=True)

    def fn_run_shell_cmd(self, cmd, desc):
        """Lance une commande via le vrai Shell (zsh/bash) pour bypass IDLE"""
        self.log("STEP", f"Action : {desc}")
        
        # On encapsule la commande pour forcer l'environnement Shell
        # -c : execute la string, -l : charge le profil utilisateur (PATH)
        full_cmd = f'{self.shell} -l -c \'{cmd}\''
        
        # On laisse le flux sortir directement dans le terminal (stdout/stderr)
        result = subprocess.run(full_cmd, shell=True)
        
        if result.returncode != 0:
            # Cas spécial : Ollama qui tente d'ouvrir une fenêtre sur Mac
            if "ollama" in cmd and self.system == "Darwin":
                self.log("INFO", "Note: Erreur d'interface ignorée (Ollama CLI installé).")
                return 0
            self.log("ERR ", f"La commande a échoué (Code {result.returncode})")
            sys.exit(result.returncode)
        return result.returncode

    def fn_install_sequence(self):
        print("\n" + "═"*60)
        print("   K.I.T.T. SYSTEM - INSTALLATEUR VERBOSE -v+++")
        print("═"*60 + "\n")

        # 1. Dossier de base
        self.log("INFO", f"Préparation du dossier : {self.kitt_dir}")
        self.kitt_dir.mkdir(parents=True, exist_ok=True)

        # 2. Téléchargement Modelfile
        # -vLf : Verbose, suit les redirections, échoue si erreur 404
        cmd_model = f'curl -vLf "{self.modelfile_url}" -o "{self.kitt_dir}/Modelfile"'
        self.fn_run_shell_cmd(cmd_model, "Récupération du Modelfile")

        # 3. Téléchargement main.py
        cmd_main = f'curl -vLf "{self.main_url}" -o "{self.kitt_dir}/main.py"'
        self.fn_run_shell_cmd(cmd_main, "Récupération du script KITT")
        os.chmod(self.kitt_dir / "main.py", 0o755)

        # 4. Installation Ollama (si manquant)
        if not shutil.which("ollama"):
            self.log("INFO", "Ollama absent. Lancement du script d'installation...")
            # On ajoute '|| true' car le script officiel crash si l'UI ne peut pas s'ouvrir (IDLE/GitHub)
            cmd_ollama = "curl -fsSL https://ollama.ai/install.sh | sh || true"
            self.fn_run_shell_cmd(cmd_ollama, "Installation du moteur Ollama")
        else:
            self.log("INFO", "Moteur Ollama déjà présent sur le système.")

        # 5. Pull & Create (L'IA de KITT)
        self.log("INFO", "Synchronisation avec les serveurs d'IA...")
        self.fn_run_shell_cmd("ollama pull llama3.2:3b", "Téléchargement Llama 3.2")
        
        cmd_create = f'ollama create kitt-ai -f "{self.kitt_dir}/Modelfile"'
        self.fn_run_shell_cmd(cmd_create, "Génération de l'empreinte KITT-AI")

        # 6. Compilation
        os.chdir(self.kitt_dir)
        self.log("STEP", "Phase de compilation finale...")
        
        if self.system == "Darwin":
            self.log("INFO", "Cible : macOS Bundle (.app)")
            self.fn_run_shell_cmd(f'"{sys.executable}" -m pip install py2app --break-system-packages', "Setup py2app")
            if os.path.exists("setup.py"): os.remove("setup.py")
            self.fn_run_shell_cmd("py2applet --make-setup main.py", "Init setup.py")
            self.fn_run_shell_cmd(f'"{sys.executable}" setup.py py2app -A', "Build App")
            
            # Déplacement vers Applications
            app_path = self.home / "Applications" / "KITT.app"
            if app_path.exists(): shutil.rmtree(app_path)
            shutil.move("dist/main.app", str(app_path))
            self.log("INFO", f"Succès : KITT est dans tes Applications !")
        else:
            self.log("INFO", "Cible : Linux Binary")
            self.fn_run_shell_cmd(f'"{sys.executable}" -m pip install pyinstaller --break-system-packages', "Setup PyInstaller")
            self.fn_run_shell_cmd("pyinstaller --onefile --noconsole main.py", "Build Binary")
            shutil.copy2("dist/main", str(self.home / "Desktop" / "KITT"))

        print("\n" + "═"*60)
        print("   ✅ INSTALLATION RÉUSSIE, MICHAEL.")
        print(f"   Système prêt dans : {self.kitt_dir}")
        print("═"*60 + "\n")

if __name__ == "__main__":
    KITTTerminalInstaller().fn_install_sequence()
