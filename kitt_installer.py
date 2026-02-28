#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KITT Setup Interface - Installation automatisée pour macOS et Linux
Gère l'installation d'Ollama, téléchargement du modèle et création de l'IA KITT
"""

import os
import sys
import subprocess
import urllib.request
import shutil
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import platform


class KITTInstaller:
    """Classe principale pour gérer l'installation de KITT"""
    
    def __init__(self):
        self.home = Path.home()
        self.kitt_dir = self.home / ".kitt"
        self.modelfile_url = "https://raw.githubusercontent.com/doctotypetech-dotcom/KITT/refs/heads/main/Modelfile"
        self.modelfile_path = self.kitt_dir / "Modelfile"
        self.system = platform.system()
        
        # Interface graphique
        self.root = tk.Tk()
        self.root.title("KITT Installation Manager")
        self.root.geometry("600x500")
        self.setup_ui()
        
    def setup_ui(self):
        """Configure l'interface utilisateur"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title = ttk.Label(main_frame, text="KITT Installation Manager", 
                         font=("Arial", 14, "bold"))
        title.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Info text
        info = ttk.Label(main_frame, text="Système détecté: " + self.system,
                        font=("Arial", 10))
        info.grid(row=1, column=0, columnspan=2, pady=5)
        
        # Progress frame
        progress_frame = ttk.LabelFrame(main_frame, text="Progression", padding="10")
        progress_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        self.progress_var = tk.IntVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                           maximum=100, length=400)
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Status text
        self.status_text = tk.Text(main_frame, height=15, width=70, 
                                   font=("Courier", 9))
        self.status_text.grid(row=3, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, 
                                 command=self.status_text.yview)
        scrollbar.grid(row=3, column=2, sticky=(tk.N, tk.S))
        self.status_text.config(yscroll=scrollbar.set)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        self.start_btn = ttk.Button(button_frame, text="Démarrer Installation", 
                                    command=self.start_installation)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.quit_btn = ttk.Button(button_frame, text="Quitter", 
                                   command=self.root.quit)
        self.quit_btn.pack(side=tk.LEFT, padx=5)
        
    def log(self, message):
        """Affiche un message dans le log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        self.status_text.insert(tk.END, log_message)
        self.status_text.see(tk.END)
        self.root.update()
        print(log_message, end='')
        
    def update_progress(self, value):
        """Met à jour la barre de progression"""
        self.progress_var.set(value)
        self.root.update()
        
    def start_installation(self):
        """Lance l'installation dans un thread séparé"""
        self.start_btn.config(state=tk.DISABLED)
        self.quit_btn.config(state=tk.DISABLED)
        
        thread = threading.Thread(target=self.run_installation)
        thread.daemon = True
        thread.start()
        
    def run_installation(self):
        """Exécute tous les étapes d'installation"""
        try:
            # Étape 1: Créer le dossier ~/.kitt
            self.log("█ Étape 1/9: Création du dossier ~/.kitt")
            self.create_kitt_directory()
            self.update_progress(11)
            
            # Étape 2: Télécharger le Modelfile
            self.log("█ Étape 2/9: Téléchargement du Modelfile")
            self.download_modelfile()
            self.update_progress(22)
            
            # Étape 3: Télécharger le main.py
            self.log("█ Étape 3/9: Téléchargement du main.py")
            self.download_main_py()
            self.update_progress(33)
            
            # Étape 4: Installer Ollama
            self.log("█ Étape 4/9: Installation d'Ollama (si nécessaire)")
            self.install_ollama()
            self.update_progress(44)
            
            # Étape 5: Télécharger le modèle llama3.2:3b
            self.log("█ Étape 5/9: Téléchargement du modèle llama3.2:3b")
            self.download_model()
            self.update_progress(55)
            
            # Étape 6: Créer l'IA KITT
            self.log("█ Étape 6/9: Création de l'IA KITT")
            self.create_kitt_ai()
            self.update_progress(66)
            
            # Étape 7: Installer PyInstaller
            self.log("█ Étape 7/9: Installation de PyInstaller")
            self.install_pyinstaller()
            self.update_progress(77)
            
            # Étape 8: Compiler avec PyInstaller
            self.log("█ Étape 8/9: Compilation avec PyInstaller")
            self.compile_with_pyinstaller()
            self.update_progress(88)
            
            # Étape 9: Copier les fichiers
            self.log("█ Étape 9/9: Mise en place des fichiers")
            self.copy_executable()
            self.update_progress(100)
            
            self.log("\n✅ Installation terminée avec succès!")
            messagebox.showinfo("Succès", "Installation de KITT terminée avec succès!")
            
        except Exception as e:
            self.log(f"\n❌ Erreur: {str(e)}")
            messagebox.showerror("Erreur", f"Installation échouée:\n{str(e)}")
        finally:
            self.start_btn.config(state=tk.NORMAL)
            self.quit_btn.config(state=tk.NORMAL)
            
    def create_kitt_directory(self):
        """Crée le dossier ~/.kitt s'il n'existe pas"""
        if self.kitt_dir.exists():
            self.log(f"  ✓ Le dossier {self.kitt_dir} existe déjà")
        else:
            self.kitt_dir.mkdir(parents=True, exist_ok=True)
            self.log(f"  ✓ Dossier créé: {self.kitt_dir}")
            
    def download_modelfile(self):
        """Télécharge le Modelfile depuis GitHub"""
        try:
            if self.modelfile_path.exists():
                self.log(f"  ✓ Modelfile existe déjà: {self.modelfile_path}")
            else:
                self.log(f"  ⬇ Téléchargement depuis: {self.modelfile_url}")
                urllib.request.urlretrieve(self.modelfile_url, self.modelfile_path)
                self.log(f"  ✓ Modelfile téléchargé: {self.modelfile_path}")
        except Exception as e:
            raise Exception(f"Erreur lors du téléchargement du Modelfile: {e}")
    
    def download_main_py(self):
        """Télécharge le main.py depuis GitHub"""
        try:
            main_py_url = "https://raw.githubusercontent.com/doctotypetech-dotcom/KITT/refs/heads/main/main.py"
            main_py_path = self.kitt_dir / "main.py"
            
            if main_py_path.exists():
                self.log(f"  ✓ main.py existe déjà: {main_py_path}")
            else:
                self.log(f"  ⬇ Téléchargement depuis: {main_py_url}")
                urllib.request.urlretrieve(main_py_url, main_py_path)
                # Rendre le fichier exécutable
                main_py_path.chmod(0o755)
                self.log(f"  ✓ main.py téléchargé: {main_py_path}")
        except Exception as e:
            raise Exception(f"Erreur lors du téléchargement du main.py: {e}")
            
    def install_ollama(self):
        """Installe Ollama via subprocess si nécessaire"""
        try:
            # Vérifier si ollama est déjà installé
            result = subprocess.run(["which", "ollama"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                self.log("  ✓ Ollama est déjà installé")
                return
                
            self.log("  ⬇ Installation d'Ollama...")
            
            if self.system == "Darwin":  # macOS
                # Télécharger et installer Ollama sur macOS
                self.log("  → Détecté: macOS")
                subprocess.run(["curl", "-fsSL", 
                              "https://ollama.ai/install.sh"],
                             check=True)
                
            elif self.system == "Linux":
                # Installation sur Linux
                self.log("  → Détecté: Linux")
                subprocess.run(["curl", "-fsSL", 
                              "https://ollama.ai/install.sh"],
                             check=True)
            else:
                raise Exception(f"Système non supporté: {self.system}")
                
            self.log("  ✓ Ollama installé avec succès")
            
        except Exception as e:
            raise Exception(f"Erreur lors de l'installation d'Ollama: {e}")
            
    def download_model(self):
        """Télécharge le modèle llama3.2:3b"""
        try:
            # Vérifier si le modèle est déjà téléchargé
            result = subprocess.run(["ollama", "list"], 
                                  capture_output=True, text=True)
            if "llama3.2:3b" in result.stdout:
                self.log("  ✓ Le modèle llama3.2:3b est déjà téléchargé")
                return
                
            self.log("  ⬇ Téléchargement de llama3.2:3b (cela peut prendre du temps)...")
            
            # Lancer le processus avec affichage en temps réel
            process = subprocess.Popen(
                ["ollama", "pull", "llama3.2:3b"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            # Afficher chaque ligne en temps réel
            while True:
                line = process.stdout.readline()
                if not line:
                    break
                self.log(f"    {line.rstrip()}")
            
            # Attendre la fin
            process.wait()
            
            if process.returncode != 0:
                raise Exception("Erreur lors du téléchargement du modèle")
                
            self.log("  ✓ Modèle llama3.2:3b téléchargé avec succès")
            
        except Exception as e:
            raise Exception(f"Erreur lors du téléchargement du modèle: {e}")
            
    def create_kitt_ai(self):
        """Crée l'IA KITT avec le Modelfile"""
        try:
            self.log("  🤖 Création de l'IA KITT...")
            
            # Lancer le processus avec affichage en temps réel
            process = subprocess.Popen(
                ["ollama", "create", "kitt-ai", "-f", str(self.modelfile_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            # Afficher les logs en temps réel depuis stdout
            while True:
                line = process.stdout.readline()
                if not line:
                    break
                self.log(f"    {line.rstrip()}")
            
            # Attendre la fin du processus
            process.wait()
            
            # Vérifier les erreurs
            if process.returncode != 0:
                stderr_lines = process.stderr.readlines()
                for line in stderr_lines:
                    self.log(f"    ❌ {line.rstrip()}")
                raise Exception(f"Ollama create a échoué avec le code {process.returncode}")
                
            self.log("  ✓ IA KITT créée avec succès")
            
        except Exception as e:
            raise Exception(f"Erreur lors de la création de KITT: {e}")
            
    def install_pyinstaller(self):
        """Installe PyInstaller via pip"""
        try:
            self.log("  ⬇ Installation de PyInstaller...")
            
            result = subprocess.run([sys.executable, "-m", "pip", "install", 
                                   "pyinstaller", "--break-system-packages"],
                                  capture_output=True, text=True)
            
            if result.returncode != 0:
                self.log(f"  ⚠ Tentative sans --break-system-packages")
                result = subprocess.run([sys.executable, "-m", "pip", "install", 
                                       "pyinstaller"],
                                      capture_output=True, text=True)
                
            self.log("  ✓ PyInstaller installé")
            
        except Exception as e:
            raise Exception(f"Erreur lors de l'installation de PyInstaller: {e}")
            
    def compile_with_pyinstaller(self):
        """Compile main.py avec PyInstaller"""
        try:
            main_py = self.kitt_dir / "main.py"
            
            if not main_py.exists():
                raise Exception("main.py non trouvé dans ~/.kitt - Le téléchargement a échoué")
                
            self.log("  🔨 Compilation avec PyInstaller...")
            
            result = subprocess.run(["pyinstaller", "--noconsole", "--onefile", 
                                   str(main_py)],
                                  cwd=str(self.kitt_dir),
                                  capture_output=True, text=True)
            
            if result.returncode != 0:
                self.log(f"  ⚠ Erreur: {result.stderr}")
                raise Exception(f"PyInstaller a échoué: {result.stderr}")
                
            self.log("  ✓ Compilation réussie")
            
        except Exception as e:
            raise Exception(f"Erreur lors de la compilation: {e}")

    def copy_executable(self):
        """Copie l'exécutable sur le bureau et ajoute à ~/.bashrc"""
        try:
            dist_dir = self.kitt_dir / "dist"
            
            if not dist_dir.exists():
                raise Exception(f"Dossier dist non trouvé: {dist_dir}")
                
            # Trouver le fichier exécutable
            executables = list(dist_dir.glob("main*"))
            if not executables:
                raise Exception("Aucun exécutable trouvé dans dist/")
                
            executable = executables[0]
            self.log(f"  📦 Exécutable trouvé: {executable}")
            
            # Copier sur le bureau
            desktop = self.home / "Desktop" / executable.name
            desktop.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(executable, desktop)
            os.chmod(desktop, 0o755)
            self.log(f"  ✓ Copié sur le desktop: {desktop}")
            
            # Ajouter au ~/.bashrc
            bashrc = self.home / ".bashrc"
            bashrc_content = ""
            
            if bashrc.exists():
                with open(bashrc, 'r') as f:
                    bashrc_content = f.read()
                    
            # Ajouter l'alias si pas déjà présent
            alias_line = f"alias kitt='{desktop}'"
            if "alias kitt=" not in bashrc_content:
                bashrc_content += f"\n\n# KITT shortcut\n{alias_line}\n"
                with open(bashrc, 'w') as f:
                    f.write(bashrc_content)
                self.log(f"  ✓ Alias 'kitt' ajouté au ~/.bashrc")
            else:
                self.log(f"  ✓ Alias 'kitt' déjà présent dans ~/.bashrc")
                
        except Exception as e:
            raise Exception(f"Erreur lors de la copie des fichiers: {e}")
            
    def run(self):
        """Lance l'interface graphique"""
        self.root.mainloop()


if __name__ == "__main__":
    installer = KITTInstaller()
    installer.run()
