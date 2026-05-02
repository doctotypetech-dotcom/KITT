#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import imaplib
import email
from email.header import decode_header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import subprocess
import time
import re
import os
import smtplib
from datetime import datetime

class MailCommandExecutor:
    def __init__(self, username, password, server="mail.mailo.com"):
        self.username = username
        self.password = password
        self.server = server
        self.mail = None
        self.last_check = 0
        self.processed_uids = set()  # Pour éviter de traiter plusieurs fois le même email
        
    def connect(self):
        """Se connecte à la boîte mail"""
        try:
            self.mail = imaplib.IMAP4_SSL(self.server, 993)
            self.mail.login(self.username, self.password)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✓ Connecté à {self.username}")
            return True
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✗ Erreur de connexion : {e}")
            return False
    
    def disconnect(self):
        """Se déconnecte proprement"""
        if self.mail:
            try:
                self.mail.close()
                self.mail.logout()
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ✓ Déconnecté")
            except:
                pass
    
    def send_startup_message(self):
        """Envoie un message de démarrage avec objet CMDSTART et contenu OK"""
        try:
            # Créer le message
            msg = MIMEMultipart()
            msg["From"] = self.username
            msg["To"] = self.username  # S'envoie à soi-même
            msg["Subject"] = "CMDSTART"
            
            # Contenu du message
            body = f"""OK

Service démarré le: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Email surveillé: {self.username}
Intervalle de vérification: 10 secondes

Le service est maintenant actif et attend les commandes avec l'objet 'cmd'.
"""
            
            # Ajouter le contenu
            msg.attach(MIMEText(body, "plain", "utf-8"))
            
            # Configuration SMTP
            smtp_server = "smtp.mailo.com"
            smtp_port = 465  # SSL
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 📤 Envoi du message de démarrage...")
            
            # Envoyer l'email
            with smtplib.SMTP_SSL(smtp_server, smtp_port) as smtp:
                smtp.login(self.username, self.password)
                smtp.send_message(msg)
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✓ Message de démarrage envoyé à {self.username}")
            return True
            
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✗ Erreur lors de l'envoi du message de démarrage: {e}")
            return False
    
    def decode_subject(self, subject):
        """Décode l'objet du message"""
        decoded_parts = []
        for part, encoding in decode_header(subject):
            if isinstance(part, bytes):
                try:
                    if encoding:
                        decoded_parts.append(part.decode(encoding))
                    else:
                        decoded_parts.append(part.decode('utf-8', errors='ignore'))
                except:
                    decoded_parts.append(part.decode('utf-8', errors='ignore'))
            else:
                decoded_parts.append(part)
        return ''.join(decoded_parts)
    
    def get_message_content(self, msg):
        """Extrait le contenu textuel du message"""
        content = ""
        
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                
                if "attachment" not in content_disposition:
                    if content_type == "text/plain":
                        try:
                            payload = part.get_payload(decode=True)
                            charset = part.get_content_charset() or 'utf-8'
                            content = payload.decode(charset, errors='ignore')
                            break
                        except:
                            pass
                    elif content_type == "text/html" and not content:
                        try:
                            payload = part.get_payload(decode=True)
                            charset = part.get_content_charset() or 'utf-8'
                            html_content = payload.decode(charset, errors='ignore')
                            content = re.sub(r'<[^>]+>', '', html_content)
                        except:
                            pass
        else:
            content_type = msg.get_content_type()
            if content_type == "text/plain":
                try:
                    payload = msg.get_payload(decode=True)
                    charset = msg.get_content_charset() or 'utf-8'
                    content = payload.decode(charset, errors='ignore')
                except:
                    content = str(msg.get_payload())
            elif content_type == "text/html":
                try:
                    payload = msg.get_payload(decode=True)
                    charset = msg.get_content_charset() or 'utf-8'
                    html_content = payload.decode(charset, errors='ignore')
                    content = re.sub(r'<[^>]+>', '', html_content)
                except:
                    content = str(msg.get_payload())
        
        return content.strip()
    
    def execute_command(self, command):
        """Exécute une commande shell et retourne la sortie"""
        try:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 🚀 Exécution: {command[:100]}...")
            
            # Exécuter la commande
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30  # Timeout de 30 secondes
            )
            
            # Construire la réponse
            output = ""
            if result.stdout:
                output += f"{result.stdout}\n"
            if result.stderr:
                output += f"STDERR:\n{result.stderr}\n"
            
            if result.returncode != 0:
                output += f"\nCode de retour: {result.returncode}"
            
            if not output:
                output = "✓ Commande exécutée avec succès (aucune sortie)"
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✓ Commande terminée (code: {result.returncode})")
            return output.strip()
            
        except subprocess.TimeoutExpired:
            error_msg = "✗ Erreur: La commande a dépassé le temps limite (30 secondes)"
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {error_msg}")
            return error_msg
        except Exception as e:
            error_msg = f"✗ Erreur lors de l'exécution: {str(e)}"
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {error_msg}")
            return error_msg
    
    def send_reply(self, original_msg, response_content):
        """Envoie une réponse avec l'objet 'Re: cmd'"""
        try:
            # Récupérer l'adresse de l'expéditeur original
            from_addr = original_msg.get("From")
            original_subject = original_msg.get("Subject", "")
            
            # Créer le message de réponse
            reply_msg = MIMEMultipart()
            reply_msg["From"] = self.username
            reply_msg["To"] = from_addr
            reply_msg["Subject"] = f"Re: {original_subject}"
            
            # Ajouter le contenu textuel
            text_part = MIMEText(response_content, "plain", "utf-8")
            reply_msg.attach(text_part)
            
            # Ajouter des informations sur l'exécution
            footer = f"\n\n---\nExécuté le: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            footer_part = MIMEText(footer, "plain", "utf-8")
            reply_msg.attach(footer_part)
            
            # Envoyer l'email
            smtp_server = "smtp.mailo.com"
            smtp_port = 465  # SSL
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 📤 Envoi de la réponse à {from_addr}...")
            
            with smtplib.SMTP_SSL(smtp_server, smtp_port) as smtp:
                smtp.login(self.username, self.password)
                smtp.send_message(reply_msg)
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✓ Réponse envoyée")
            return True
            
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✗ Erreur lors de l'envoi de la réponse: {e}")
            return False
    
    def check_and_process_emails(self):
        """Vérifie les nouveaux emails avec l'objet 'cmd' et les traite"""
        try:
            # Sélectionner la boîte de réception
            self.mail.select("INBOX")
            
            # Rechercher les emails NON LUS avec objet "cmd"
            status, messages = self.mail.search(None, '(UNSEEN SUBJECT "cmd")')
            
            if status != "OK":
                return
            
            message_ids = messages[0].split()
            
            if not message_ids:
                return
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 📬 {len(message_ids)} nouveau(x) message(s) avec objet 'cmd'")
            
            # Traiter chaque message
            for msg_id in message_ids:
                # Vérifier si déjà traité (par UID)
                status, uid_data = self.mail.fetch(msg_id, "(UID)")
                if status == "OK":
                    uid = uid_data[0].decode().split()[2].strip("()")
                    if uid in self.processed_uids:
                        continue
                
                # Récupérer le message
                status, msg_data = self.mail.fetch(msg_id, "(RFC822)")
                
                if status != "OK":
                    continue
                
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        # Parser l'email
                        msg = email.message_from_bytes(response_part[1])
                        
                        # Vérifier l'objet (par sécurité)
                        subject = self.decode_subject(msg.get("Subject", ""))
                        
                        if subject.lower().strip() == "cmd":
                            # Extraire la commande
                            command = self.get_message_content(msg)
                            
                            if command:
                                print(f"[{datetime.now().strftime('%H:%M:%S')}] 📝 Commande reçue: {command[:200]}")
                                
                                # Exécuter la commande
                                output = self.execute_command(command)
                                
                                # Envoyer la réponse
                                self.send_reply(msg, output)
                                
                                # Marquer comme lu
                                self.mail.store(msg_id, '+FLAGS', '\\Seen')
                                
                                # Ajouter à la liste des traités
                                if status == "OK":
                                    self.processed_uids.add(uid)
                                
                                print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Message {msg_id} traité")
                            else:
                                print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Message vide - commande ignorée")
                                # Envoyer une notification d'erreur
                                self.send_reply(msg, "Erreur: Le message ne contient aucune commande à exécuter.")
        
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✗ Erreur lors du traitement: {e}")
    
    def run(self, check_interval=10):
        """Boucle principale qui vérifie périodiquement les emails"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🚀 Démarrage du service de surveillance")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 📧 Surveillance de: {self.username}")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ⏱️  Intervalle de vérification: {check_interval} secondes")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🛑 Appuyez sur Ctrl+C pour arrêter")
        print("-" * 70)
        
        # Envoyer le message de démarrage
        self.send_startup_message()
        
        try:
            while True:
                # Vérifier la connexion et se reconnecter si nécessaire
                if not self.mail:
                    if not self.connect():
                        time.sleep(5)
                        continue
                
                try:
                    # Vérifier et traiter les emails
                    self.check_and_process_emails()
                    
                except imaplib.IMAP4.abort:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Connexion perdue, reconnexion...")
                    self.disconnect()
                    self.mail = None
                except Exception as e:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Erreur: {e}")
                
                # Attendre avant la prochaine vérification
                time.sleep(check_interval)
                
        except KeyboardInterrupt:
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🛑 Arrêt demandé par l'utilisateur")
        finally:
            self.disconnect()
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 👋 Service arrêté")

if __name__ == "__main__":
    # Configuration - À MODIFIER avec vos identifiants
    USERNAME = "aurcocy@mailo.com"  # Remplacez par votre email
    PASSWORD = "1&Aa1&Aa"              # Remplacez par votre mot de passe
    SERVER = "mail.mailo.com"
    CHECK_INTERVAL = 1  # Vérifier toutes les 10 secondes
    
    # Créer et exécuter le service
    executor = MailCommandExecutor(USERNAME, PASSWORD, SERVER)
    executor.run(check_interval=CHECK_INTERVAL)
