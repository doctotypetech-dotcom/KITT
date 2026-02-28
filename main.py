#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KITT - Assistant IA Interactif
Interface graphique pour communiquer avec KITT via Ollama
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import subprocess
import threading
from pathlib import Path
from datetime import datetime
import sys


class KITTApplication:
    """Application principale pour KITT"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("KITT - Assistant IA")
        self.root.geometry("900x700")
        self.root.minsize(600, 500)
        
        # Configuration du style
        style = ttk.Style()
        style.theme_use('clam')
        
        self.setup_ui()
        self.check_ollama_status()
        
    def setup_ui(self):
        """Configure l'interface utilisateur"""
        # Frame principal avec padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # === SECTION TITRE ===
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        title = ttk.Label(header_frame, text="🤖 KITT - Assistant IA Intelligent", 
                         font=("Arial", 16, "bold"))
        title.pack(side=tk.LEFT)
        
        self.status_label = ttk.Label(header_frame, text="⏳ Vérification...", 
                                     foreground="orange", font=("Arial", 10))
        self.status_label.pack(side=tk.RIGHT)
        
        # Séparateur
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # === SECTION CONVERSATION ===
        chat_frame = ttk.LabelFrame(main_frame, text="Conversation", padding="10")
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Text widget pour les messages
        self.chat_display = scrolledtext.ScrolledText(chat_frame, 
                                                      height=20, 
                                                      width=80,
                                                      font=("Courier", 10),
                                                      wrap=tk.WORD,
                                                      state=tk.DISABLED)
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        
        # Configuration des tags pour le formatage
        self.chat_display.tag_config("user", foreground="#0066cc", font=("Courier", 10, "bold"))
        self.chat_display.tag_config("kitt", foreground="#009900", font=("Courier", 10))
        self.chat_display.tag_config("system", foreground="#999999", font=("Courier", 9, "italic"))
        self.chat_display.tag_config("error", foreground="#cc0000", font=("Courier", 10, "bold"))
        
        # === SECTION INPUT ===
        input_frame = ttk.LabelFrame(main_frame, text="Votre Message", padding="10")
        input_frame.pack(fill=tk.BOTH, expand=False, pady=(0, 10))
        
        self.input_text = tk.Text(input_frame, height=4, width=80, 
                                  font=("Courier", 10), wrap=tk.WORD)
        self.input_text.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        scrollbar = ttk.Scrollbar(input_frame, orient=tk.VERTICAL, 
                                 command=self.input_text.yview)
        scrollbar.pack(fill=tk.Y, side=tk.RIGHT)
        self.input_text.config(yscroll=scrollbar.set)
        
        # Bind Ctrl+Entrée pour envoyer
        self.input_text.bind("<Control-Return>", lambda e: self.send_message())
        
        # === SECTION BOUTONS ===
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        self.send_btn = ttk.Button(button_frame, text="Envoyer (Ctrl+Entrée)", 
                                   command=self.send_message)
        self.send_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.clear_btn = ttk.Button(button_frame, text="Effacer la conversation", 
                                    command=self.clear_chat)
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        self.quit_btn = ttk.Button(button_frame, text="Quitter", 
                                   command=self.root.quit)
        self.quit_btn.pack(side=tk.RIGHT, padx=5)
        
        self.display_message("Bienvenue dans KITT!", "system")
        
    def display_message(self, message, sender="system"):
        """Affiche un message dans le chat"""
        self.chat_display.config(state=tk.NORMAL)
        
        if sender == "user":
            self.chat_display.insert(tk.END, "Vous: ", "user")
            self.chat_display.insert(tk.END, f"{message}\n\n")
        elif sender == "kitt":
            self.chat_display.insert(tk.END, "KITT: ", "kitt")
            self.chat_display.insert(tk.END, f"{message}\n\n")
        else:
            self.chat_display.insert(tk.END, f"[SYSTÈME] {message}\n", "system")
            
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
        
    def check_ollama_status(self):
        """Vérifie le statut d'Ollama"""
        def check():
            try:
                result = subprocess.run(["ollama", "list"], 
                                      capture_output=True, text=True, timeout=5)
                
                if result.returncode == 0:
                    if "kitt-ai" in result.stdout:
                        self.status_label.config(text="✅ KITT prêt", foreground="green")
                        self.display_message("KITT est prêt à discuter!", "system")
                    else:
                        self.status_label.config(text="⚠️  KITT non créé", foreground="orange")
                        self.display_message("KITT n'est pas installé. Veuillez exécuter l'installateur.", "system")
                else:
                    self.status_label.config(text="❌ Ollama non accessible", foreground="red")
                    self.display_message("Ollama n'est pas accessible. Assurez-vous qu'il est lancé.", "system")
                    
            except FileNotFoundError:
                self.status_label.config(text="❌ Ollama non installé", foreground="red")
                self.display_message("Ollama n'est pas installé. Veuillez l'installer d'abord.", "system")
            except Exception as e:
                self.status_label.config(text="❌ Erreur de vérification", foreground="red")
                self.display_message(f"Erreur: {str(e)}", "error")
                
        thread = threading.Thread(target=check, daemon=True)
        thread.start()
        
    def send_message(self):
        """Envoie un message à KITT"""
        message = self.input_text.get("1.0", tk.END).strip()
        
        if not message:
            messagebox.showwarning("Attention", "Veuillez entrer un message!")
            return
            
        # Afficher le message de l'utilisateur
        self.display_message(message, "user")
        self.input_text.delete("1.0", tk.END)
        
        # Désactiver les boutons pendant le traitement
        self.send_btn.config(state=tk.DISABLED)
        self.input_text.config(state=tk.DISABLED)
        
        # Lancer la requête dans un thread
        thread = threading.Thread(target=self.query_kitt, args=(message,), daemon=True)
        thread.start()
        
    def query_kitt(self, user_message):
        """Communique avec KITT avec affichage en temps réel"""
        try:
            # Afficher le début de la réponse de KITT
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.insert(tk.END, "🤖 KITT: ", "kitt")
            self.chat_display.see(tk.END)
            self.chat_display.config(state=tk.DISABLED)
            self.root.update()
            
            # Lancer le processus Ollama
            process = subprocess.Popen(
                ["ollama", "run", "kitt-ai", user_message],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            # Afficher en temps réel
            full_response = ""
            while True:
                try:
                    # Lire avec timeout pour éviter le blocage
                    char = process.stdout.read(1)
                    if not char:
                        break
                    
                    full_response += char
                    
                    # Afficher le caractère en temps réel
                    self.chat_display.config(state=tk.NORMAL)
                    self.chat_display.insert(tk.END, char, "kitt")
                    self.chat_display.see(tk.END)
                    self.chat_display.config(state=tk.DISABLED)
                    self.root.update()
                    
                except Exception as e:
                    break
            
            # Attendre la fin du processus
            process.wait(timeout=300)
            
            # Ajouter une nouvelle ligne à la fin
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.insert(tk.END, "\n\n")
            self.chat_display.config(state=tk.DISABLED)
            
            if process.returncode != 0 and not full_response:
                error_msg = process.stderr if process.stderr else "Erreur inconnue"
                self.display_message(f"Erreur: {error_msg}", "error")
                
        except subprocess.TimeoutExpired:
            process.kill()
            self.display_message("\n⏱️ Timeout: KITT prend trop de temps à répondre", "error")
        except Exception as e:
            self.display_message(f"\n❌ Erreur: {str(e)}", "error")
        finally:
            self.send_btn.config(state=tk.NORMAL)
            self.input_text.config(state=tk.NORMAL)
            self.input_text.focus()
            
    def clear_chat(self):
        """Efface la conversation"""
        if messagebox.askyesno("Confirmation", "Effacer toute la conversation?"):
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.delete("1.0", tk.END)
            self.chat_display.config(state=tk.DISABLED)
            self.display_message("Conversation effacée", "system")


def main():
    """Fonction principale"""
    root = tk.Tk()
    app = KITTApplication(root)
    root.mainloop()


if __name__ == "__main__":
    main()
