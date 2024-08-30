import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog as fd
from flask import Flask, request, send_from_directory, jsonify
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import threading

app = Flask(__name__)
auth = HTTPBasicAuth()

# Configuration des utilisateurs
users = {
    "admin": generate_password_hash("password")
}

# Base de données pour sauvegarder les adresses IP
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS connections (ip TEXT)''')
    conn.commit()
    conn.close()

init_db()

@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username

@app.route('/files/<path:filename>', methods=['GET'])
@auth.login_required
def serve_file(filename):
    ip = request.remote_addr
    save_ip(ip)
    return send_from_directory(directory='files', path=filename)

@app.route('/save_ip', methods=['POST'])
def save_ip(ip):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("INSERT INTO connections (ip) VALUES (?)", (ip,))
    conn.commit()
    conn.close()

@app.route('/ips', methods=['GET'])
@auth.login_required
def get_ips():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM connections")
    ips = c.fetchall()
    conn.close()
    return jsonify(ips)

def run_server():
    if not os.path.exists('files'):
        os.makedirs('files')
    app.run(host='0.0.0.0', port=8000)

def start_server():
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
    messagebox.showinfo("Serveur", "Le serveur a démarré.")

def stop_server():
    # Cette fonction est un placeholder car Flask ne peut pas être arrêté proprement via un script
    messagebox.showinfo("Serveur", "Le serveur doit être arrêté manuellement.")

def save_settings():
    # Sauvegarder les paramètres ici
    messagebox.showinfo("Paramètres", "Les paramètres ont été sauvegardés.")

def select_file():
    file_path = fd.askopenfilename()
    if file_path:
        selected_file_label.config(text=file_path)
        # Ici, tu peux ajouter le code pour afficher le fichier sur le serveur

# Interface graphique avec Tkinter
root = tk.Tk()
root.title("Serveur Web")

tab_control = ttk.Notebook(root)

tab1 = tk.Frame(tab_control)
tab2 = tk.Frame(tab_control)

tab_control.add(tab1, text='Paramètres')
tab_control.add(tab2, text='Serveur')

# Onglet Paramètres
tk.Label(tab1, text="Nom d'utilisateur:").grid(row=0, column=0, padx=10, pady=10)
username_entry = tk.Entry(tab1)
username_entry.grid(row=0, column=1, padx=10, pady=10)

tk.Label(tab1, text="Mot de passe:").grid(row=1, column=0, padx=10, pady=10)
password_entry = tk.Entry(tab1, show='*')
password_entry.grid(row=1, column=1, padx=10, pady=10)

save_ip_var = tk.BooleanVar()
tk.Checkbutton(tab1, text="Sauvegarder les adresses IP", variable=save_ip_var).grid(row=2, columnspan=2, padx=10, pady=10)

tk.Button(tab1, text="Sauvegarder les paramètres", command=save_settings).grid(row=3, columnspan=2, padx=10, pady=10)

# Ajouter un bouton pour sélectionner un fichier
tk.Button(tab1, text="Sélectionner un fichier", command=select_file).grid(row=4, columnspan=2, padx=10, pady=10)
selected_file_label = tk.Label(tab1, text="")
selected_file_label.grid(row=5, columnspan=2, padx=10, pady=10)

# Onglet Serveur
tk.Button(tab2, text="Démarrer le serveur", command=start_server).grid(row=0, column=0, padx=10, pady=10)
tk.Button(tab2, text="Arrêter le serveur", command=stop_server).grid(row=0, column=1, padx=10, pady=10)

tab_control.pack(expand=1, fill='both')

root.mainloop()
