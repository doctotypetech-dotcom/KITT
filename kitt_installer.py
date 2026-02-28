#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
import platform

class KITTInstaller:
    def __init__(self):
        self.home = Path.home()
        self.kitt_dir = self.home / ".kitt"
        self.modelfile_url = "https://raw.githubusercontent.com/doctotypetech-dotcom/KITT/refs/heads/main/Modelfile"
        self.system = platform.system()
        
        # UI Setup
        self.root = tk.Tk()
        self.root.title("KITT Installation Manager")
        self.root.geometry("600x550")
        self.fn_setup_ui()
        
    def fn_setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="📟 KITT Installer - Verbose Mode", font=("Arial", 14, "bold")).pack(pady=10)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=20)
        
        # Log interne à l'UI
        self.status_text = tk.Text(main_frame, height=15, width=70, font=("Courier", 9), bg="black", fg="#00ff00")
        self.status_text.pack(fill=tk.BOTH, expand=True)
        
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=20)
        
        self.start_btn = ttk.Button(btn_frame, text="Lancer l'installation (voir Terminal)", command=self.fn_run_full_install_sequence)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="Quitter", command=self.root.quit).pack(side=tk.LEFT, padx=5)

    def fn_log_both(self, message):
        """Log à la fois dans l'interface et dans le terminal"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        full_msg = f"[{timestamp}] {message}"
        
        # Log Terminal (Précis)
        print(f"\n{'='*60}\n{full_msg}\n{'='*60}", flush=True)
        
        # Log UI
        self.status_text.insert(tk.END, full_msg + "\n")
        self.status_text.see(tk.END)
        self.root.update()

    def fn_run_full_install_sequence(self):
        self.start_btn.config(state=tk.DISABLED)
        try:
            # 1. Dossier
            self.fn_log_both("INIT : Création du dossier .kitt")
            self.kitt_dir.mkdir(parents=True, exist_ok=True)
            self.progress_var.set(10)

            # 2. Modelfile avec CURL (Verbose)
            self.fn_log_both("CURL : Téléchargement du Modelfile")
            subprocess.run(["curl", "-vL", self.modelfile_url, "-o", str(self.kitt_dir / "Modelfile")], check=True)
            self.progress_var.set(25)

            # 3. main.py avec CURL (Verbose)
            self.fn_log_both("CURL : Téléchargement du script main.py")
            main_url = "https://raw.githubusercontent.com/doctotypetech-dotcom/KITT/refs/heads/main/main.py"
            subprocess.run(["curl", "-vL", main_url, "-o", str(self.kitt_dir / "main.py")], check=True)
            os.chmod(self.kitt_dir / "main.py", 0o755)
            self.progress_var.set(40)

            # 4. Ollama (Installation)
            self.fn_log_both("SYSTEM : Vérification/Installation Ollama")
            if not shutil.which("ollama"):
                # On pipe le curl dans sh de manière verbeuse
                cmd = "curl -fsSL https://ollama.ai/install.sh | sh"
                subprocess.run(cmd, shell=True, check=True)
            self.progress_var.set(55)

            # 5. Modèle Llama (Logs temps réel d'Ollama)
            self.fn_log_both("OLLAMA : Pull du modèle llama3.2:3b")
            subprocess.run(["ollama", "pull", "llama3.2:3b"], check=True)
            self.progress_var.set(70)

            # 6. Création IA
            self.fn_log_both("OLLAMA : Création de l'entité kitt-ai")
            subprocess.run(["ollama", "create", "kitt-ai", "-f", str(self.kitt_dir / "Modelfile")], check=True)
            self.progress_var.set(85)

            # 7. Compilation
            self.fn_log_both("BUILD : Compilation de l'exécutable final")
            self.fn_compile_application()
            self.progress_var.set(100)

            self.fn_log_both("TERMINÉ : KITT est prêt à l'emploi.")
            messagebox.showinfo("Succès", "Installation verbeuse terminée.")

        except subprocess.CalledProcessError as e:
            self.fn_log_both(f"ERREUR FATALE (Commande échouée) : {e}")
            messagebox.showerror("Erreur Critique", f"La commande {e.cmd} a échoué. Vérifie le terminal.")
        except Exception as e:
            self.fn_log_both(f"ERREUR INCONNUE : {e}")
            messagebox.showerror("Erreur", str(e))
        finally:
            self.start_btn.config(state=tk.NORMAL)

    def fn_compile_application(self):
        os.chdir(self.kitt_dir)
        if self.system == "Darwin":
            self.fn_log_both("MAC : Préparation py2app")
            subprocess.run([sys.executable, "-m", "pip", "install", "py2app", "--break-system-packages"], check=True)
            if os.path.exists("setup.py"): os.remove("setup.py")
            subprocess.run(["py2applet", "--make-setup", "main.py"], check=True)
            subprocess.run([sys.executable, "setup.py", "py2app", "-A"], check=True)
            
            app_path = self.home / "Applications" / "KITT.app"
            if app_path.exists(): shutil.rmtree(app_path)
            shutil.move("dist/main.app", str(app_path))
            self.fn_log_both(f"MAC : Application déplacée dans {app_path}")
        else:
            self.fn_log_both("LINUX : Préparation PyInstaller")
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller", "--break-system-packages"], check=True)
            subprocess.run(["pyinstaller", "--onefile", "--noconsole", "main.py"], check=True)
            shutil.copy2("dist/main", str(self.home / "Desktop" / "KITT"))
            self.fn_log_both("LINUX : Exécutable copié sur le Bureau")

    def fn_run_ui(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = KITTInstaller()
    app.fn_run_ui()
