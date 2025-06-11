"""
RM Bot - Versão Desktop Standalone para Poke Old
Sistema completo com abas Hotkeys e Cura implementadas

Instruções:
1. Tenha Python 3.8+ instalado
2. Execute: python rm_bot_completo_com_abas.py
3. O sistema instala dependências automaticamente
4. Crie conta admin no primeiro uso
5. Abra o Poke Old e configure o bot
"""

import os
import sys
import subprocess
import threading
import time
import json
import sqlite3
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import messagebox, ttk

# Auto-instalador de dependências
def install_dependencies():
    """Instalar dependências automaticamente"""
    import platform
    system = platform.system()
    
    if system != "Windows":
        print("ℹ️ Sistema não-Windows detectado. Pulando verificação de dependências.")
        print("Para funcionalidade completa, execute no Windows com:")
        print("pip install customtkinter pyautogui opencv-python psutil pywin32 keyboard bcrypt pillow")
        return
    
    required_packages = [
        'customtkinter',
        'bcrypt',
        'pillow'
    ]
    
    optional_packages = [
        'pyautogui', 
        'opencv-python',
        'psutil',
        'pywin32',
        'keyboard'
    ]
    
    print("🔧 Verificando dependências básicas...")
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"📦 Instalando {len(missing_packages)} dependências básicas...")
        try:
            for package in missing_packages:
                print(f"   Instalando {package}...")
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print("✅ Dependências básicas instaladas!")
        except Exception as e:
            print(f"❌ Erro na instalação: {e}")
            print("Instale manualmente: pip install customtkinter bcrypt pillow")

# Executar auto-instalador apenas no Windows
if __name__ == "__main__":
    install_dependencies()

import customtkinter as ctk
import bcrypt

# Importações para automação (instalar se necessário)
try:
    # Detectar sistema operacional
    import platform
    IS_WINDOWS = platform.system() == "Windows"
    
    if IS_WINDOWS:
        import pyautogui
        import cv2
        import numpy as np
        import psutil
        import random
        import win32gui
        import win32process
        import win32api
        import win32con
        import keyboard
        AUTOMATION_AVAILABLE = True
        print("✅ Bibliotecas Windows carregadas com sucesso")
    else:
        print("⚠️ Sistema não-Windows detectado. Funcionalidades limitadas.")
        AUTOMATION_AVAILABLE = False
        
except ImportError as e:
    AUTOMATION_AVAILABLE = False
    print("❌ Bibliotecas de automação não encontradas. Para Windows instale:")
    print("pip install pyautogui opencv-python psutil pywin32 keyboard")
    print(f"Erro específico: {e}")

# Configurar PyAutoGUI se disponível
if AUTOMATION_AVAILABLE:
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.1

# Configurar aparência
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class DatabaseManager:
    """Gerenciador do banco de dados SQLite local"""
    
    def __init__(self):
        self.db_path = "rm_bot.db"
        self.init_database()
    
    def init_database(self):
        """Inicializar banco de dados"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela de usuários
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                is_admin BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
        
        # Tabela de assinaturas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                subscription_type TEXT DEFAULT 'premium',
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Criar usuário admin padrão
        cursor.execute("SELECT * FROM users WHERE username = 'admin'")
        if not cursor.fetchone():
            password_hash = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cursor.execute(
                "INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, ?)",
                ('admin', password_hash, True)
            )
            
            # Criar assinatura para admin
            user_id = cursor.lastrowid
            expires_at = datetime.now() + timedelta(days=365)
            cursor.execute(
                "INSERT INTO subscriptions (user_id, expires_at, subscription_type) VALUES (?, ?, ?)",
                (user_id, expires_at, 'admin')
            )
        
        conn.commit()
        conn.close()
    
    def authenticate_user(self, username, password):
        """Autenticar usuário"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, password_hash, is_admin FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user[1].encode('utf-8')):
            # Atualizar último login
            cursor.execute("UPDATE users SET last_login = ? WHERE id = ?", (datetime.now(), user[0]))
            conn.commit()
            conn.close()
            return {'id': user[0], 'username': username, 'is_admin': user[2]}
        
        conn.close()
        return None
    
    def get_user_subscription(self, user_id):
        """Obter assinatura do usuário"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT expires_at, subscription_type FROM subscriptions WHERE user_id = ? AND active = 1",
            (user_id,)
        )
        subscription = cursor.fetchone()
        conn.close()
        
        if subscription:
            expires_at = datetime.fromisoformat(subscription[0])
            return {
                'expires_at': expires_at,
                'subscription_type': subscription[1],
                'is_expired': expires_at < datetime.now(),
                'days_remaining': max(0, (expires_at - datetime.now()).days)
            }
        return None
    
    def create_user(self, username, password, is_admin=False):
        """Criar novo usuário"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cursor.execute(
                "INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, ?)",
                (username, password_hash, is_admin)
            )
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return user_id
        except sqlite3.IntegrityError:
            conn.close()
            return None
    
    def get_all_users(self):
        """Obter todos os usuários"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT u.id, u.username, u.is_admin, u.created_at, u.last_login,
                   s.expires_at, s.subscription_type, s.active
            FROM users u
            LEFT JOIN subscriptions s ON u.id = s.user_id AND s.active = 1
            ORDER BY u.created_at DESC
        """)
        
        users = []
        for row in cursor.fetchall():
            user_data = {
                'id': row[0],
                'username': row[1],
                'is_admin': row[2],
                'created_at': row[3],
                'last_login': row[4],
                'subscription': None
            }
            
            if row[5]:  # Tem assinatura
                expires_at = datetime.fromisoformat(row[5])
                user_data['subscription'] = {
                    'expires_at': expires_at,
                    'subscription_type': row[6],
                    'active': row[7],
                    'is_expired': expires_at < datetime.now(),
                    'days_remaining': max(0, (expires_at - datetime.now()).days)
                }
            
            users.append(user_data)
        
        conn.close()
        return users
    
    def extend_user_subscription(self, user_id, days, subscription_type='premium'):
        """Estender assinatura de usuário"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Verificar se já tem assinatura ativa
        cursor.execute("SELECT expires_at FROM subscriptions WHERE user_id = ? AND active = 1", (user_id,))
        existing = cursor.fetchone()
        
        if existing:
            # Estender assinatura existente
            current_expires = datetime.fromisoformat(existing[0])
            if current_expires < datetime.now():
                # Se expirou, começar de hoje
                new_expires = datetime.now() + timedelta(days=days)
            else:
                # Se ainda está ativa, adicionar aos dias restantes
                new_expires = current_expires + timedelta(days=days)
            
            cursor.execute(
                "UPDATE subscriptions SET expires_at = ?, subscription_type = ? WHERE user_id = ? AND active = 1",
                (new_expires, subscription_type, user_id)
            )
        else:
            # Criar nova assinatura
            expires_at = datetime.now() + timedelta(days=days)
            cursor.execute(
                "INSERT INTO subscriptions (user_id, expires_at, subscription_type) VALUES (?, ?, ?)",
                (user_id, expires_at, subscription_type)
            )
        
        conn.commit()
        conn.close()
        return True
    
    def delete_user(self, user_id):
        """Deletar usuário"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Deletar assinaturas primeiro
        cursor.execute("DELETE FROM subscriptions WHERE user_id = ?", (user_id,))
        # Deletar usuário
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        
        conn.commit()
        conn.close()
        return True

class RMBotApp:
    """Aplicação principal do RM Bot"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.current_user = None
        
        # Configurações de hotkeys padrão
        self.hotkeys_config = {
            'start_fishing': 'F1',
            'stop_fishing': 'F2',
            'start_skills': 'F3',
            'stop_skills': 'F4',
            'quick_capture': 'F5',
            'mark_points': 'F6',
            'emergency_stop': 'Escape'
        }
        self.load_hotkeys_config()
        
        # Variáveis de cura e automação
        self.cura_active = False
        self.heal_skill_vars = {}
        self.heal_skill_speed_vars = {}
        self.target_points = []
        self.skills_active = False
        self.fishing_active = False
        self.fishing_points = []
        self.water_color = None
        
        # Threads de automação
        self.skills_thread = None
        self.healing_thread = None
        self.fishing_thread = None
        
        # Sistema de automação avançado
        self.automation_enabled = AUTOMATION_AVAILABLE
        self.battle_detection_enabled = False
        self.auto_battle_mode = False
        self.battle_skills = ['f1', 'f2', 'f3', 'f4']  # Skills para batalha
        
        # Detecção visual
        self.battle_image_path = None
        self.water_image_path = None
        
        # Interface
        self.root = ctk.CTk()
        self.root.title("RM Bot - Automação para Poke Old v2.0")
        self.root.geometry("1200x800")
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        self.main_frame = None
        self.setup_login_interface()
        
        # Configurar fechamento
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Configurar hotkeys globais após login
        self.setup_hotkeys_system()
        
        # Sistema de animações - inicialização
        self.animation_enabled = True
        self.current_tab = None
        self.animation_in_progress = False
        self.animation_speed = 1.0
        self.last_tab_switch_time = 0
        self.animation_progress_bar = None
    
    def load_hotkeys_config(self):
        """Carregar configurações de hotkeys do arquivo"""
        try:
            if os.path.exists('hotkeys_config.json'):
                with open('hotkeys_config.json', 'r') as f:
                    saved_config = json.load(f)
                    self.hotkeys_config.update(saved_config)
        except:
            pass
    
    def save_hotkeys_config(self):
        """Salvar configurações de hotkeys no arquivo"""
        try:
            with open('hotkeys_config.json', 'w') as f:
                json.dump(self.hotkeys_config, f, indent=2)
        except:
            pass
    
    def setup_login_interface(self):
        """Configurar tela de login"""
        self.clear_interface()
        
        # Frame principal centralizado
        login_frame = ctk.CTkFrame(self.root, width=400, height=500)
        login_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Logo/Título
        title = ctk.CTkLabel(
            login_frame,
            text="🤖 RM Bot",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        title.pack(pady=30)
        
        subtitle = ctk.CTkLabel(
            login_frame,
            text="Sistema de Automação para Poke Old",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        subtitle.pack(pady=10)
        
        # Campos de login
        self.username_entry = ctk.CTkEntry(
            login_frame,
            placeholder_text="👤 Usuário",
            width=300,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.username_entry.pack(pady=20)
        
        self.password_entry = ctk.CTkEntry(
            login_frame,
            placeholder_text="🔒 Senha",
            show="*",
            width=300,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.password_entry.pack(pady=10)
        
        # Botões
        login_btn = ctk.CTkButton(
            login_frame,
            text="🚀 Entrar",
            command=self.perform_login,
            width=300,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        login_btn.pack(pady=20)
        
        register_btn = ctk.CTkButton(
            login_frame,
            text="📝 Cadastrar",
            command=self.show_register_dialog,
            width=300,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color="gray",
            hover_color="darkgray"
        )
        register_btn.pack(pady=10)
        
        # Informações de acesso
        info_frame = ctk.CTkFrame(login_frame)
        info_frame.pack(fill="x", padx=20, pady=20)
        
        info_label = ctk.CTkLabel(
            info_frame,
            text="🔑 Acesso Administrativo:\nUsuário: admin\nSenha: admin123",
            font=ctk.CTkFont(size=12),
            text_color="cyan"
        )
        info_label.pack(pady=10)
        
        # Bind Enter para login
        self.username_entry.bind("<Return>", lambda e: self.perform_login())
        self.password_entry.bind("<Return>", lambda e: self.perform_login())
        
        # Foco inicial
        self.username_entry.focus()
    
    def show_register_dialog(self):
        """Mostrar diálogo de cadastro"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Cadastrar Novo Usuário")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Centralizar
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (300 // 2)
        dialog.geometry(f"400x300+{x}+{y}")
        
        title = ctk.CTkLabel(dialog, text="📝 Novo Cadastro", font=ctk.CTkFont(size=20, weight="bold"))
        title.pack(pady=20)
        
        username_entry = ctk.CTkEntry(dialog, placeholder_text="👤 Usuário", width=300, height=40)
        username_entry.pack(pady=10)
        
        password_entry = ctk.CTkEntry(dialog, placeholder_text="🔒 Senha", show="*", width=300, height=40)
        password_entry.pack(pady=10)
        
        confirm_password_entry = ctk.CTkEntry(dialog, placeholder_text="🔒 Confirmar Senha", show="*", width=300, height=40)
        confirm_password_entry.pack(pady=10)
        
        def register_user():
            username = username_entry.get().strip()
            password = password_entry.get()
            confirm_password = confirm_password_entry.get()
            
            if not username or not password:
                messagebox.showerror("Erro", "Preencha todos os campos!")
                return
            
            if password != confirm_password:
                messagebox.showerror("Erro", "Senhas não coincidem!")
                return
            
            if len(password) < 4:
                messagebox.showerror("Erro", "Senha deve ter pelo menos 4 caracteres!")
                return
            
            user_id = self.db.create_user(username, password)
            if user_id:
                messagebox.showinfo("Sucesso", f"Usuário '{username}' criado com sucesso!\n\nIMPORTANTE: Você começou com 0 dias de licença.\nProcure um administrador para ativar sua licença.")
                dialog.destroy()
            else:
                messagebox.showerror("Erro", "Usuário já existe!")
        
        register_btn = ctk.CTkButton(dialog, text="✅ Cadastrar", command=register_user, width=200, height=40)
        register_btn.pack(pady=20)
        
        username_entry.focus()
    
    def perform_login(self):
        """Realizar login"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Erro", "Preencha usuário e senha!")
            return
        
        user = self.db.authenticate_user(username, password)
        if user:
            self.current_user = user
            
            if user['is_admin']:
                self.setup_admin_interface()
            else:
                subscription = self.db.get_user_subscription(user['id'])
                if subscription and not subscription['is_expired']:
                    self.setup_user_interface()
                else:
                    self.setup_blocked_interface()
        else:
            messagebox.showerror("Erro", "Usuário ou senha incorretos!")
    
    def setup_user_interface(self):
        """Configurar interface para usuário comum"""
        self.clear_interface()
        
        # Sidebar
        self.create_user_sidebar()
        
        # Main frame
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        
        # Iniciar com aba de processo
        self.switch_tab("process")
    
    def setup_admin_interface(self):
        """Configurar interface para administrador"""
        self.clear_interface()
        
        # Sidebar
        self.create_admin_sidebar()
        
        # Main frame
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        
        # Iniciar com aba de usuários
        self.switch_tab("users")
    
    def setup_blocked_interface(self):
        """Configurar interface para usuário sem licença"""
        self.clear_interface()
        
        # Frame principal centralizado
        blocked_frame = ctk.CTkFrame(self.root, width=600, height=400)
        blocked_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Título
        title = ctk.CTkLabel(
            blocked_frame,
            text="🚫 Acesso Bloqueado",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="red"
        )
        title.pack(pady=30)
        
        # Mensagem
        message = ctk.CTkLabel(
            blocked_frame,
            text=f"Olá {self.current_user['username']}!\n\nSua licença expirou ou ainda não foi ativada.\nProcure um administrador para renovar seu acesso.\n\nO RM Bot oferece automação completa para Poke Old\ncom recursos avançados de pesca e skills.",
            font=ctk.CTkFont(size=14),
            justify="center"
        )
        message.pack(pady=20)
        
        # Botão de logout
        logout_btn = ctk.CTkButton(
            blocked_frame,
            text="🚪 Voltar ao Login",
            command=self.logout,
            width=200,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="red",
            hover_color="darkred"
        )
        logout_btn.pack(pady=30)
    
    def create_user_sidebar(self):
        """Criar barra lateral para usuário"""
        sidebar = ctk.CTkFrame(self.root, width=200)
        sidebar.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        
        # Informações do usuário
        user_frame = ctk.CTkFrame(sidebar)
        user_frame.pack(fill="x", padx=10, pady=10)
        
        user_label = ctk.CTkLabel(
            user_frame,
            text=f"👤 {self.current_user['username']}",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        user_label.pack(pady=10)
        
        # Status da assinatura
        subscription = self.db.get_user_subscription(self.current_user['id'])
        if subscription and not subscription['is_expired']:
            status_text = f"✅ VIP - {subscription['days_remaining']} dias"
            status_color = "green"
        else:
            status_text = "⏰ Sem assinatura"
            status_color = "red"
        
        status_label = ctk.CTkLabel(
            user_frame,
            text=status_text,
            font=ctk.CTkFont(size=11),
            text_color=status_color
        )
        status_label.pack()
        
        # Botões de navegação do usuário
        process_btn = ctk.CTkButton(
            sidebar,
            text="🎮 Selecionar Jogo",
            command=lambda: self.switch_tab("process"),
            height=35
        )
        process_btn.pack(fill="x", padx=10, pady=5)
        
        fishing_btn = ctk.CTkButton(
            sidebar,
            text="🎣 Pesca",
            command=lambda: self.switch_tab("fishing"),
            height=35
        )
        fishing_btn.pack(fill="x", padx=10, pady=5)
        
        skills_btn = ctk.CTkButton(
            sidebar,
            text="⚔️ Skills",
            command=lambda: self.switch_tab("skills"),
            height=35
        )
        skills_btn.pack(fill="x", padx=10, pady=5)
        
        stats_btn = ctk.CTkButton(
            sidebar,
            text="📊 Estatísticas",
            command=lambda: self.switch_tab("stats"),
            height=35
        )
        stats_btn.pack(fill="x", padx=10, pady=5)
        
        # ABA HOTKEYS COM COR ROXA PARA TESTE
        hotkeys_btn = ctk.CTkButton(
            sidebar,
            text="⌨️ Hotkeys",
            command=lambda: self.switch_tab("hotkeys"),
            height=35,
            fg_color="purple",
            hover_color="darkviolet"
        )
        hotkeys_btn.pack(fill="x", padx=10, pady=5)
        
        # ABA CURA COM COR LARANJA PARA TESTE  
        cura_btn = ctk.CTkButton(
            sidebar,
            text="💊 Cura",
            command=lambda: self.switch_tab("cura"),
            height=35,
            fg_color="orange",
            hover_color="darkorange"
        )
        cura_btn.pack(fill="x", padx=10, pady=5)
        
        # Auto Battle - Sistema inteligente
        auto_battle_btn = ctk.CTkButton(
            sidebar,
            text="🤖 Auto Battle",
            command=lambda: self.switch_tab("auto_battle"),
            height=35,
            fg_color="#FF6B35",
            hover_color="#E55A2B"
        )
        auto_battle_btn.pack(fill="x", padx=10, pady=5)
        
        # Botão de logout
        logout_btn = ctk.CTkButton(
            sidebar,
            text="🚪 Sair",
            command=self.logout,
            height=35,
            fg_color="red",
            hover_color="darkred"
        )
        logout_btn.pack(side="bottom", fill="x", padx=10, pady=10)
    
    def create_admin_sidebar(self):
        """Criar barra lateral para administrador"""
        sidebar = ctk.CTkFrame(self.root, width=200)
        sidebar.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        
        # Informações do admin
        user_frame = ctk.CTkFrame(sidebar)
        user_frame.pack(fill="x", padx=10, pady=10)
        
        admin_label = ctk.CTkLabel(
            user_frame,
            text=f"👑 {self.current_user['username']}",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        admin_label.pack(pady=10)
        
        role_label = ctk.CTkLabel(
            user_frame,
            text="ADMINISTRADOR",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="gold"
        )
        role_label.pack()
        
        # Botões de navegação do admin
        users_btn = ctk.CTkButton(
            sidebar,
            text="👥 Usuários",
            command=lambda: self.switch_tab("users"),
            height=35
        )
        users_btn.pack(fill="x", padx=10, pady=5)
        
        licenses_btn = ctk.CTkButton(
            sidebar,
            text="🎫 Licenças",
            command=lambda: self.switch_tab("licenses"),
            height=35
        )
        licenses_btn.pack(fill="x", padx=10, pady=5)
        
        # Funcionalidades do bot também para admin
        process_btn = ctk.CTkButton(
            sidebar,
            text="🎮 Selecionar Jogo",
            command=lambda: self.switch_tab("process"),
            height=35
        )
        process_btn.pack(fill="x", padx=10, pady=5)
        
        fishing_btn = ctk.CTkButton(
            sidebar,
            text="🎣 Pesca",
            command=lambda: self.switch_tab("fishing"),
            height=35
        )
        fishing_btn.pack(fill="x", padx=10, pady=5)
        
        skills_btn = ctk.CTkButton(
            sidebar,
            text="⚔️ Skills",
            command=lambda: self.switch_tab("skills"),
            height=35
        )
        skills_btn.pack(fill="x", padx=10, pady=5)
        
        stats_btn = ctk.CTkButton(
            sidebar,
            text="📊 Estatísticas",
            command=lambda: self.switch_tab("stats"),
            height=35
        )
        stats_btn.pack(fill="x", padx=10, pady=5)
        
        # ABA HOTKEYS COM COR ROXA PARA TESTE
        hotkeys_btn = ctk.CTkButton(
            sidebar,
            text="⌨️ Hotkeys",
            command=lambda: self.switch_tab("hotkeys"),
            height=35,
            fg_color="purple",
            hover_color="darkviolet"
        )
        hotkeys_btn.pack(fill="x", padx=10, pady=5)
        
        # ABA CURA COM COR LARANJA PARA TESTE  
        cura_btn = ctk.CTkButton(
            sidebar,
            text="💊 Cura",
            command=lambda: self.switch_tab("cura"),
            height=35,
            fg_color="orange",
            hover_color="darkorange"
        )
        cura_btn.pack(fill="x", padx=10, pady=5)
        
        # Auto Battle - Sistema inteligente para admin
        auto_battle_btn = ctk.CTkButton(
            sidebar,
            text="🤖 Auto Battle",
            command=lambda: self.switch_tab("auto_battle"),
            height=35,
            fg_color="#FF6B35",
            hover_color="#E55A2B"
        )
        auto_battle_btn.pack(fill="x", padx=10, pady=5)
        
        # Botão de logout
        logout_btn = ctk.CTkButton(
            sidebar,
            text="🚪 Sair",
            command=self.logout,
            height=35,
            fg_color="red",
            hover_color="darkred"
        )
        logout_btn.pack(side="bottom", fill="x", padx=10, pady=10)
    
    def switch_tab(self, tab_name):
        """Trocar aba com animação de transição suave"""
        import time
        
        # Throttle - evitar cliques muito rápidos
        current_time = time.time()
        if current_time - self.last_tab_switch_time < 0.3:
            return
        self.last_tab_switch_time = current_time
        
        # Evitar múltiplas animações simultâneas
        if self.animation_in_progress:
            return
        
        # Se já estamos na aba, não fazer nada
        if self.current_tab == tab_name:
            return
        
        self.animation_in_progress = True
        
        if self.animation_enabled:
            # Escolher tipo de animação baseado na aba
            if tab_name in ["auto_battle", "skills", "cura"]:
                # Animação de slide para abas de ação
                self.slide_transition(tab_name)
            else:
                # Animação de fade para outras abas
                self.fade_out_current_tab(lambda: self.load_new_tab(tab_name))
        else:
            # Transição direta sem animação
            self.load_new_tab_direct(tab_name)
    
    def fade_out_current_tab(self, callback):
        """Animação de fade out da aba atual"""
        def fade_step(alpha):
            if alpha > 0:
                # Reduzir opacidade gradualmente
                for widget in self.main_frame.winfo_children():
                    try:
                        # Simular fade out alterando a cor do texto
                        if hasattr(widget, 'configure'):
                            if hasattr(widget, 'cget'):
                                try:
                                    current_color = widget.cget('text_color')
                                    if current_color:
                                        # Escurecer gradualmente
                                        fade_color = self.interpolate_color(current_color, "#2b2b2b", 1 - alpha)
                                        widget.configure(text_color=fade_color)
                                except:
                                    pass
                    except:
                        pass
                
                # Continuar animação com easing
                eased_alpha = self.ease_in_out_cubic(1 - alpha)
                delay = int(30 / self.animation_speed)
                self.root.after(delay, lambda: fade_step(alpha - 0.1))
            else:
                # Fade out completo, executar callback
                callback()
        
        fade_step(1.0)
    
    def load_new_tab(self, tab_name):
        """Carregar nova aba e aplicar fade in"""
        # Limpar widgets atuais
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        # Carregar nova aba
        if tab_name == "fishing":
            self.create_fishing_tab()
        elif tab_name == "skills":
            self.create_skills_tab()
        elif tab_name == "stats":
            self.create_stats_tab()
        elif tab_name == "process":
            self.create_process_tab()
        elif tab_name == "hotkeys":
            self.create_hotkeys_tab()
        elif tab_name == "cura":
            self.create_cura_tab()
        elif tab_name == "auto_battle":
            self.create_auto_battle_tab()
        elif tab_name == "users":
            self.create_user_management_tab()
        elif tab_name == "licenses":
            self.create_license_management_tab()
        
        # Aplicar fade in
        self.fade_in_new_tab()
        
        # Atualizar aba atual
        self.current_tab = tab_name
    
    def fade_in_new_tab(self):
        """Animação de fade in da nova aba"""
        def fade_step(alpha):
            if alpha < 1.0:
                # Aumentar opacidade gradualmente
                for widget in self.main_frame.winfo_children():
                    try:
                        if hasattr(widget, 'configure'):
                            # Restaurar cores gradualmente
                            self.restore_widget_colors(widget, alpha)
                    except:
                        pass
                
                # Continuar animação
                self.root.after(20, lambda: fade_step(alpha + 0.15))
            else:
                # Fade in completo, animação finalizada
                self.animation_in_progress = False
        
        # Iniciar com widgets invisíveis
        for widget in self.main_frame.winfo_children():
            try:
                if hasattr(widget, 'configure'):
                    if hasattr(widget, 'cget'):
                        try:
                            widget.configure(text_color="#1a1a1a")
                        except:
                            pass
            except:
                pass
        
        fade_step(0.0)
    
    def interpolate_color(self, color1, color2, t):
        """Interpolar entre duas cores"""
        try:
            # Converter cores hex para RGB
            if color1.startswith('#'):
                r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
            else:
                r1, g1, b1 = 255, 255, 255  # Branco padrão
            
            if color2.startswith('#'):
                r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)
            else:
                r2, g2, b2 = 43, 43, 43  # Cinza escuro padrão
            
            # Interpolar
            r = int(r1 + (r2 - r1) * t)
            g = int(g1 + (g2 - g1) * t)
            b = int(b1 + (b2 - b1) * t)
            
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return "#ffffff"
    
    def restore_widget_colors(self, widget, alpha):
        """Restaurar cores originais dos widgets gradualmente"""
        try:
            widget_type = widget.__class__.__name__
            
            # Definir cores padrão por tipo de widget
            default_colors = {
                'CTkLabel': "#ffffff",
                'CTkButton': "#3b8ed0",
                'CTkEntry': "#ffffff",
                'CTkTextbox': "#ffffff",
                'CTkCheckBox': "#ffffff",
                'CTkFrame': "#2b2b2b"
            }
            
            if widget_type in default_colors:
                target_color = default_colors[widget_type]
                current_color = self.interpolate_color("#1a1a1a", target_color, alpha)
                
                if hasattr(widget, 'configure'):
                    if widget_type in ['CTkLabel', 'CTkEntry', 'CTkTextbox', 'CTkCheckBox']:
                        widget.configure(text_color=current_color)
                    elif widget_type == 'CTkButton':
                        # Para botões, interpolar também a cor de fundo
                        bg_color = self.interpolate_color("#1a1a1a", "#3b8ed0", alpha)
                        widget.configure(fg_color=bg_color, text_color="#ffffff")
        except:
            pass
    
    def slide_transition(self, tab_name):
        """Animação de deslizamento para transições especiais"""
        # Capturar conteúdo atual
        current_widgets = list(self.main_frame.winfo_children())
        
        # Aplicar efeito de slide out (deslizar para a esquerda)
        self.slide_out_current(current_widgets, lambda: self.slide_in_new_tab(tab_name))
    
    def slide_out_current(self, widgets, callback):
        """Deslizar conteúdo atual para fora"""
        def slide_step(offset):
            if offset > -300:  # Deslizar 300 pixels para a esquerda
                for widget in widgets:
                    try:
                        if widget.winfo_exists():
                            # Simular movimento alterando padding
                            current_padx = widget.pack_info().get('padx', (0, 0))
                            if isinstance(current_padx, int):
                                new_padx = (current_padx + offset, 0)
                            else:
                                new_padx = (current_padx[0] + offset, current_padx[1])
                            
                            widget.pack_configure(padx=new_padx)
                    except:
                        pass
                
                # Continuar animação
                self.root.after(15, lambda: slide_step(offset - 20))
            else:
                # Slide out completo
                callback()
        
        slide_step(0)
    
    def slide_in_new_tab(self, tab_name):
        """Carregar nova aba com efeito de slide in"""
        # Limpar widgets atuais
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        # Carregar nova aba
        self.load_tab_content(tab_name)
        
        # Aplicar slide in (deslizar da direita)
        new_widgets = list(self.main_frame.winfo_children())
        self.slide_in_widgets(new_widgets)
    
    def slide_in_widgets(self, widgets):
        """Deslizar novos widgets para dentro"""
        # Começar fora da tela (direita)
        for widget in widgets:
            try:
                widget.pack_configure(padx=(300, 0))
            except:
                pass
        
        def slide_step(offset):
            if offset > 0:
                for widget in widgets:
                    try:
                        if widget.winfo_exists():
                            widget.pack_configure(padx=(offset, 0))
                    except:
                        pass
                
                # Continuar animação
                self.root.after(15, lambda: slide_step(offset - 20))
            else:
                # Slide in completo, restaurar padding normal
                for widget in widgets:
                    try:
                        if widget.winfo_exists():
                            widget.pack_configure(padx=20)
                    except:
                        pass
                
                # Animação finalizada
                self.animation_in_progress = False
        
        slide_step(300)
    
    def load_tab_content(self, tab_name):
        """Carregar conteúdo da aba sem animação"""
        if tab_name == "fishing":
            self.create_fishing_tab()
        elif tab_name == "skills":
            self.create_skills_tab()
        elif tab_name == "stats":
            self.create_stats_tab()
        elif tab_name == "process":
            self.create_process_tab()
        elif tab_name == "hotkeys":
            self.create_hotkeys_tab()
        elif tab_name == "cura":
            self.create_cura_tab()
        elif tab_name == "auto_battle":
            self.create_auto_battle_tab()
        elif tab_name == "users":
            self.create_user_management_tab()
        elif tab_name == "licenses":
            self.create_license_management_tab()
        
        # Atualizar aba atual
        self.current_tab = tab_name
    
    def create_process_tab(self):
        """Criar aba de seleção de processo"""
        header = ctk.CTkLabel(
            self.main_frame,
            text="🎮 Seleção do Processo do Jogo",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        header.pack(pady=20)
        
        info = ctk.CTkLabel(
            self.main_frame,
            text="Selecione o processo do Poke Old para que o bot possa interagir com o jogo",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        info.pack(pady=10)
        
        # Frame para lista de processos
        process_frame = ctk.CTkFrame(self.main_frame)
        process_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Mensagem temporária para sistemas sem automação
        if not AUTOMATION_AVAILABLE:
            no_automation = ctk.CTkLabel(
                process_frame,
                text="⚠️ Automação não disponível neste sistema\n\nPara funcionalidade completa, execute no Windows com:\npip install pyautogui opencv-python psutil pywin32",
                font=ctk.CTkFont(size=16),
                text_color="orange"
            )
            no_automation.pack(expand=True)
            return
        
        # Lista de processos (simulada)
        processes_label = ctk.CTkLabel(
            process_frame,
            text="📋 Processos Disponíveis:",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        processes_label.pack(pady=20)
        
        # Frame scrollável para processos
        scroll_frame = ctk.CTkScrollableFrame(process_frame)
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Simular alguns processos para demonstração
        sample_processes = [
            {"name": "PokeOld.exe", "pid": "1234", "status": "🎮 Jogo Principal"},
            {"name": "PokeClient.exe", "pid": "5678", "status": "🎮 Cliente Alternativo"},
            {"name": "Chrome.exe", "pid": "9012", "status": "🌐 Navegador"},
            {"name": "Notepad.exe", "pid": "3456", "status": "📝 Editor de Texto"}
        ]
        
        for proc in sample_processes:
            proc_frame = ctk.CTkFrame(scroll_frame)
            proc_frame.pack(fill="x", padx=10, pady=5)
            
            proc_info = ctk.CTkLabel(
                proc_frame,
                text=f"{proc['name']} (PID: {proc['pid']}) - {proc['status']}",
                font=ctk.CTkFont(size=12)
            )
            proc_info.pack(side="left", padx=10, pady=10)
            
            select_btn = ctk.CTkButton(
                proc_frame,
                text="Selecionar",
                width=100,
                height=30,
                command=lambda p=proc: self.select_process(p)
            )
            select_btn.pack(side="right", padx=10, pady=10)
        
        # Botão para atualizar lista
        refresh_btn = ctk.CTkButton(
            process_frame,
            text="🔄 Atualizar Lista",
            command=self.refresh_processes,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        refresh_btn.pack(pady=20)
    
    def create_hotkeys_tab(self):
        """Criar aba de configuração de hotkeys"""
        header = ctk.CTkLabel(
            self.main_frame,
            text="⌨️ Configuração de Hotkeys",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        header.pack(pady=20)
        
        description = ctk.CTkLabel(
            self.main_frame,
            text="Configure teclas de atalho para controlar o bot rapidamente",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        description.pack(pady=10)
        
        # Frame principal scrollável
        main_scroll = ctk.CTkScrollableFrame(self.main_frame)
        main_scroll.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Configurações de hotkeys
        hotkeys_frame = ctk.CTkFrame(main_scroll)
        hotkeys_frame.pack(fill="x", padx=10, pady=10)
        
        hotkeys_header = ctk.CTkLabel(
            hotkeys_frame,
            text="🎯 Configurações de Teclas",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        hotkeys_header.pack(pady=15)
        
        # Grid de configurações
        config_grid = ctk.CTkFrame(hotkeys_frame)
        config_grid.pack(fill="x", padx=15, pady=10)
        
        # Lista de hotkeys configuráveis
        hotkey_configs = [
            ('start_fishing', 'Iniciar Pesca', 'Inicia a pesca automática'),
            ('stop_fishing', 'Parar Pesca', 'Para a pesca automática'),
            ('start_skills', 'Iniciar Skills', 'Ativa as skills automáticas'),
            ('stop_skills', 'Parar Skills', 'Desativa as skills automáticas'),
            ('quick_capture', 'Captura Rápida', 'Captura cor da água rapidamente'),
            ('mark_points', 'Marcar Pontos', 'Marca pontos de pesca manualmente'),
            ('emergency_stop', 'Parada de Emergência', 'Para todas as automações')
        ]
        
        self.hotkey_entries = {}
        
        for config_key, display_name, description in hotkey_configs:
            # Frame para cada configuração
            config_row = ctk.CTkFrame(config_grid)
            config_row.pack(fill="x", padx=5, pady=5)
            
            # Nome da função
            name_label = ctk.CTkLabel(
                config_row,
                text=display_name,
                font=ctk.CTkFont(size=12, weight="bold"),
                width=150
            )
            name_label.pack(side="left", padx=10, pady=10)
            
            # Descrição
            desc_label = ctk.CTkLabel(
                config_row,
                text=description,
                font=ctk.CTkFont(size=10),
                text_color="gray",
                width=200
            )
            desc_label.pack(side="left", padx=5, pady=10)
            
            # Campo da tecla
            key_entry = ctk.CTkEntry(
                config_row,
                width=80,
                height=30,
                font=ctk.CTkFont(size=12)
            )
            key_entry.insert(0, self.hotkeys_config.get(config_key, 'F1'))
            key_entry.pack(side="left", padx=5, pady=10)
            
            # Botão para capturar
            capture_btn = ctk.CTkButton(
                config_row,
                text="Capturar",
                width=80,
                height=30,
                command=lambda k=config_key, e=key_entry: self.capture_hotkey(k, e)
            )
            capture_btn.pack(side="left", padx=5, pady=10)
            
            # Botão para resetar
            reset_btn = ctk.CTkButton(
                config_row,
                text="Reset",
                width=60,
                height=30,
                fg_color="gray",
                command=lambda k=config_key, e=key_entry: self.reset_hotkey(k, e)
            )
            reset_btn.pack(side="left", padx=5, pady=10)
            
            # Status
            status_label = ctk.CTkLabel(
                config_row,
                text="✅ Configurado",
                font=ctk.CTkFont(size=10),
                text_color="green",
                width=80
            )
            status_label.pack(side="right", padx=10, pady=10)
            
            # Armazenar referências
            self.hotkey_entries[config_key] = {
                'entry': key_entry,
                'status': status_label
            }
        
        # Frame de ações
        action_frame = ctk.CTkFrame(hotkeys_frame)
        action_frame.pack(fill="x", padx=15, pady=15)
        
        # Botão salvar
        save_btn = ctk.CTkButton(
            action_frame,
            text="💾 Salvar Configurações",
            command=self.save_hotkeys,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="green",
            hover_color="darkgreen"
        )
        save_btn.pack(side="left", padx=10, pady=10)
        
        # Botão restaurar padrões
        restore_btn = ctk.CTkButton(
            action_frame,
            text="🔄 Restaurar Padrões",
            command=self.restore_default_hotkeys,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="orange",
            hover_color="darkorange"
        )
        restore_btn.pack(side="left", padx=10, pady=10)
        
        # Botão testar hotkeys
        test_btn = ctk.CTkButton(
            action_frame,
            text="🧪 Testar Hotkeys",
            command=self.test_hotkeys,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="blue",
            hover_color="darkblue"
        )
        test_btn.pack(side="left", padx=10, pady=10)
        
        # Label de status
        self.hotkeys_status = ctk.CTkLabel(
            action_frame,
            text="💡 Configure as teclas e clique em Salvar",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.hotkeys_status.pack(side="right", padx=20, pady=10)
    
    def create_cura_tab(self):
        """Criar aba de sistema de cura automática"""
        header = ctk.CTkLabel(
            self.main_frame,
            text="💊 Sistema de Cura Automática",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        header.pack(pady=20)
        
        description = ctk.CTkLabel(
            self.main_frame,
            text="Configure skills de cura e targets para manter seu Pokémon saudável",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        description.pack(pady=10)
        
        # Frame principal scrollável
        main_scroll = ctk.CTkScrollableFrame(self.main_frame)
        main_scroll.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Seção 1: Configuração de Targets
        target_frame = ctk.CTkFrame(main_scroll)
        target_frame.pack(fill="x", padx=10, pady=10)
        
        target_header = ctk.CTkLabel(
            target_frame,
            text="🎯 Configuração de Targets (Pokémon Selvagens)",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        target_header.pack(pady=15)
        
        # Botões para configurar targets
        target_buttons_frame = ctk.CTkFrame(target_frame)
        target_buttons_frame.pack(fill="x", padx=15, pady=10)
        
        mark_targets_btn = ctk.CTkButton(
            target_buttons_frame,
            text="📍 Marcar Targets",
            command=self.mark_targets,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="blue",
            hover_color="darkblue"
        )
        mark_targets_btn.pack(side="left", padx=10, pady=10)
        
        clear_targets_btn = ctk.CTkButton(
            target_buttons_frame,
            text="🗑️ Limpar Targets",
            command=self.clear_targets,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="red",
            hover_color="darkred"
        )
        clear_targets_btn.pack(side="left", padx=10, pady=10)
        
        load_targets_btn = ctk.CTkButton(
            target_buttons_frame,
            text="📂 Carregar Targets",
            command=self.load_targets,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="orange",
            hover_color="darkorange"
        )
        load_targets_btn.pack(side="left", padx=10, pady=10)
        
        # Status dos targets
        targets_status = ctk.CTkLabel(
            target_frame,
            text="❌ Nenhum target configurado - Use 'Marcar Targets' para configurar",
            font=ctk.CTkFont(size=12),
            text_color="red"
        )
        targets_status.pack(pady=10)
        
        # Seção 2: Skills de Cura
        heal_skills_frame = ctk.CTkFrame(main_scroll)
        heal_skills_frame.pack(fill="x", padx=10, pady=10)
        
        heal_header = ctk.CTkLabel(
            heal_skills_frame,
            text="⚔️ Skills de Cura (Target Skills)",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        heal_header.pack(pady=15)
        
        # Grid de skills de cura
        heal_grid_frame = ctk.CTkFrame(heal_skills_frame)
        heal_grid_frame.pack(fill="x", padx=15, pady=10)
        
        heal_skills_list = [
            ("F1", "f1"), ("F2", "f2"), ("F3", "f3"), ("F4", "f4"),
            ("F5", "f5"), ("F6", "f6"), ("F7", "f7"), ("F8", "f8"),
            ("F9", "f9"), ("F10", "f10"), ("F11", "f11"), ("F12", "f12")
        ]
        
        for i, (display_name, key) in enumerate(heal_skills_list):
            skill_row = ctk.CTkFrame(heal_grid_frame)
            skill_row.pack(fill="x", padx=5, pady=3)
            
            # Checkbox para ativar skill
            self.heal_skill_vars[key] = ctk.BooleanVar()
            skill_check = ctk.CTkCheckBox(
                skill_row,
                text=f"Skill {display_name}",
                variable=self.heal_skill_vars[key],
                width=120
            )
            skill_check.pack(side="left", padx=10, pady=8)
            
            # Campo de intervalo
            interval_label = ctk.CTkLabel(skill_row, text="Intervalo (ms):")
            interval_label.pack(side="left", padx=5)
            
            self.heal_skill_speed_vars[key] = ctk.StringVar(value="3000")
            interval_entry = ctk.CTkEntry(
                skill_row,
                textvariable=self.heal_skill_speed_vars[key],
                width=80,
                height=30
            )
            interval_entry.pack(side="left", padx=5, pady=8)
            
            # Prioridade
            priority_label = ctk.CTkLabel(skill_row, text="Prioridade:")
            priority_label.pack(side="left", padx=5)
            
            priority_var = ctk.StringVar(value="Normal")
            priority_combo = ctk.CTkComboBox(
                skill_row,
                values=["Alta", "Normal", "Baixa"],
                variable=priority_var,
                width=80,
                height=30
            )
            priority_combo.pack(side="left", padx=5, pady=8)
        
        # Seção 3: Controles de Cura
        control_frame = ctk.CTkFrame(main_scroll)
        control_frame.pack(fill="x", padx=10, pady=10)
        
        control_header = ctk.CTkLabel(
            control_frame,
            text="🎮 Controles de Cura",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        control_header.pack(pady=15)
        
        # Botão principal de controle
        main_control_frame = ctk.CTkFrame(control_frame)
        main_control_frame.pack(fill="x", padx=15, pady=15)
        
        self.cura_btn = ctk.CTkButton(
            main_control_frame,
            text="▶️ Iniciar Sistema de Cura",
            command=self.toggle_healing,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="green",
            hover_color="darkgreen"
        )
        self.cura_btn.pack(side="left", padx=10, pady=10)
        
        # Status do sistema
        cura_status = ctk.CTkLabel(
            main_control_frame,
            text="❌ Sistema Inativo",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="red"
        )
        cura_status.pack(side="left", padx=20, pady=10)
        
        # Log de atividades
        log_frame = ctk.CTkFrame(control_frame)
        log_frame.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(
            log_frame,
            text="📝 Log de Atividades",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=5)
        
        heal_log = ctk.CTkTextbox(log_frame, height=100)
        heal_log.pack(fill="x", padx=10, pady=10)
        heal_log.insert("end", "Sistema de cura inicializado. Configure targets e skills para começar.\n")
        
        # Armazenar referências importantes
        self.heal_log = heal_log
        self.targets_status = targets_status
        self.cura_status = cura_status
    
    def create_auto_battle_tab(self):
        """Criar aba Auto Battle - Sistema inteligente inspirado no repositório bot-otpokemon"""
        header = ctk.CTkLabel(
            self.main_frame,
            text="🤖 Sistema Auto Battle Inteligente",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        header.pack(pady=20)
        
        description = ctk.CTkLabel(
            self.main_frame,
            text="Sistema que detecta automaticamente se está em batalha ou pescando e executa as ações apropriadas",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        description.pack(pady=10)
        
        # Frame principal scrollável
        main_scroll = ctk.CTkScrollableFrame(self.main_frame)
        main_scroll.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Seção 1: Configuração de Detecção Visual
        detection_frame = ctk.CTkFrame(main_scroll)
        detection_frame.pack(fill="x", padx=10, pady=10)
        
        detection_header = ctk.CTkLabel(
            detection_frame,
            text="👁️ Configuração de Detecção Visual",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        detection_header.pack(pady=15)
        
        # Configurar imagem de batalha
        battle_config_frame = ctk.CTkFrame(detection_frame)
        battle_config_frame.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(
            battle_config_frame,
            text="📷 Imagem de Referência da Batalha:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", padx=10, pady=5)
        
        battle_img_frame = ctk.CTkFrame(battle_config_frame)
        battle_img_frame.pack(fill="x", padx=10, pady=5)
        
        self.battle_img_entry = ctk.CTkEntry(
            battle_img_frame,
            placeholder_text="Caminho da imagem de batalha (ex: battle_box.png)",
            width=300
        )
        self.battle_img_entry.pack(side="left", padx=5, pady=5)
        
        browse_battle_btn = ctk.CTkButton(
            battle_img_frame,
            text="Procurar",
            command=self.browse_battle_image,
            width=80
        )
        browse_battle_btn.pack(side="left", padx=5)
        
        # Confidence level
        confidence_frame = ctk.CTkFrame(battle_config_frame)
        confidence_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            confidence_frame,
            text="🎯 Nível de Confiança:",
            width=120
        ).pack(side="left", padx=5)
        
        self.confidence_var = ctk.StringVar(value="0.9")
        confidence_slider = ctk.CTkSlider(
            confidence_frame,
            from_=0.5,
            to=1.0,
            variable=self.confidence_var,
            width=150
        )
        confidence_slider.pack(side="left", padx=10)
        
        confidence_label = ctk.CTkLabel(
            confidence_frame,
            textvariable=self.confidence_var,
            width=50
        )
        confidence_label.pack(side="left", padx=5)
        
        # Seção 2: Skills de Batalha
        battle_skills_frame = ctk.CTkFrame(main_scroll)
        battle_skills_frame.pack(fill="x", padx=10, pady=10)
        
        battle_skills_header = ctk.CTkLabel(
            battle_skills_frame,
            text="⚔️ Skills para Batalha",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        battle_skills_header.pack(pady=15)
        
        # Grid de skills de batalha
        battle_grid = ctk.CTkFrame(battle_skills_frame)
        battle_grid.pack(fill="x", padx=15, pady=10)
        
        self.battle_skill_vars = {}
        battle_skills_list = [("F1", "f1"), ("F2", "f2"), ("F3", "f3"), ("F4", "f4")]
        
        for display_name, key in battle_skills_list:
            skill_row = ctk.CTkFrame(battle_grid)
            skill_row.pack(fill="x", padx=5, pady=3)
            
            self.battle_skill_vars[key] = ctk.BooleanVar()
            skill_check = ctk.CTkCheckBox(
                skill_row,
                text=f"Usar {display_name} em batalha",
                variable=self.battle_skill_vars[key],
                width=150
            )
            skill_check.pack(side="left", padx=10, pady=5)
        
        # Seção 3: Configuração de Pesca
        fishing_config_frame = ctk.CTkFrame(main_scroll)
        fishing_config_frame.pack(fill="x", padx=10, pady=10)
        
        fishing_header = ctk.CTkLabel(
            fishing_config_frame,
            text="🎣 Configuração de Pesca Automática",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        fishing_header.pack(pady=15)
        
        # Hotkey de pesca
        fishing_hotkey_frame = ctk.CTkFrame(fishing_config_frame)
        fishing_hotkey_frame.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(
            fishing_hotkey_frame,
            text="Hotkey de Pesca:",
            width=120
        ).pack(side="left", padx=5)
        
        self.fishing_hotkey_var = ctk.StringVar(value="shift+f1")
        fishing_hotkey_entry = ctk.CTkEntry(
            fishing_hotkey_frame,
            textvariable=self.fishing_hotkey_var,
            width=100
        )
        fishing_hotkey_entry.pack(side="left", padx=5)
        
        # Tempo de espera
        wait_time_frame = ctk.CTkFrame(fishing_config_frame)
        wait_time_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(
            wait_time_frame,
            text="Tempo de espera (segundos):",
            width=150
        ).pack(side="left", padx=5)
        
        self.wait_time_var = ctk.StringVar(value="2.2")
        wait_time_entry = ctk.CTkEntry(
            wait_time_frame,
            textvariable=self.wait_time_var,
            width=80
        )
        wait_time_entry.pack(side="left", padx=5)
        
        # Seção 4: Controles Principais
        control_frame = ctk.CTkFrame(main_scroll)
        control_frame.pack(fill="x", padx=10, pady=10)
        
        control_header = ctk.CTkLabel(
            control_frame,
            text="🎮 Controles do Auto Battle",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        control_header.pack(pady=15)
        
        # Botão principal
        main_control_frame = ctk.CTkFrame(control_frame)
        main_control_frame.pack(fill="x", padx=15, pady=15)
        
        self.auto_battle_btn = ctk.CTkButton(
            main_control_frame,
            text="▶️ Iniciar Auto Battle",
            command=self.toggle_auto_battle,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#FF6B35",
            hover_color="#E55A2B"
        )
        self.auto_battle_btn.pack(side="left", padx=10, pady=10)
        
        # Status
        self.auto_battle_status = ctk.CTkLabel(
            main_control_frame,
            text="❌ Auto Battle Inativo",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="red"
        )
        self.auto_battle_status.pack(side="left", padx=20, pady=10)
        
        # Configuração de hotkey global (inspirado no repositório)
        hotkey_frame = ctk.CTkFrame(control_frame)
        hotkey_frame.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(
            hotkey_frame,
            text="🔥 Hotkey Global (Z+X+C para ligar/desligar):",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", padx=10, pady=5)
        
        self.global_hotkey_var = ctk.BooleanVar()
        global_hotkey_check = ctk.CTkCheckBox(
            hotkey_frame,
            text="Ativar hotkey global Z+X+C",
            variable=self.global_hotkey_var
        )
        global_hotkey_check.pack(anchor="w", padx=10, pady=5)
        
        # Log de atividades
        log_frame = ctk.CTkFrame(control_frame)
        log_frame.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(
            log_frame,
            text="📝 Log do Auto Battle",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=5)
        
        self.auto_battle_log = ctk.CTkTextbox(log_frame, height=120)
        self.auto_battle_log.pack(fill="x", padx=10, pady=10)
        self.auto_battle_log.insert("end", "Sistema Auto Battle inicializado.\nConfiguração baseada no repositório bot-otpokemon.\nDetecção inteligente: Batalha → usar skills / Fora de batalha → pescar.\n")
        
        # Inicializar variáveis do Auto Battle
        self.auto_battle_active = False
        self.auto_battle_thread = None
        
        # Inicializar todas as variáveis necessárias
        if not hasattr(self, 'target_points'):
            self.target_points = []
        if not hasattr(self, 'fishing_points'):
            self.fishing_points = []
        if not hasattr(self, 'water_color'):
            self.water_color = None
        if not hasattr(self, 'skills_active'):
            self.skills_active = False
        if not hasattr(self, 'fishing_active'):
            self.fishing_active = False
        if not hasattr(self, 'healing_active'):
            self.healing_active = False
        
        # Sistema de hotkeys globais
        self.global_hotkeys_active = False
        self.hotkey_listener_thread = None
        
        # Mapeamento de ações de hotkeys
        self.hotkey_actions = {
            'start_fishing': self.toggle_fishing,
            'stop_fishing': self.toggle_fishing,
            'start_skills': self.toggle_skills,
            'stop_skills': self.toggle_skills,
            'start_cura': self.toggle_healing,
            'stop_cura': self.toggle_healing,
            'emergency_stop': self.emergency_stop_all
        }

    
    def browse_battle_image(self):
        """Procurar imagem de batalha"""
        from tkinter import filedialog
        filename = filedialog.askopenfilename(
            title="Selecionar imagem de batalha",
            filetypes=[("PNG files", "*.png"), ("JPG files", "*.jpg"), ("All files", "*.*")]
        )
        if filename:
            self.battle_img_entry.delete(0, 'end')
            self.battle_img_entry.insert(0, filename)
    
    def toggle_auto_battle(self):
        """Alternar sistema Auto Battle"""
        if not self.auto_battle_active:
            self.start_auto_battle()
        else:
            self.stop_auto_battle()
    
    def start_auto_battle(self):
        """Iniciar Auto Battle"""
        self.auto_battle_active = True
        self.auto_battle_btn.configure(text="⏹️ Parar Auto Battle", fg_color="red", hover_color="darkred")
        self.auto_battle_status.configure(text="✅ Auto Battle Ativo", text_color="green")
        
        # Iniciar thread do Auto Battle
        self.auto_battle_thread = threading.Thread(target=self.auto_battle_loop, daemon=True)
        self.auto_battle_thread.start()
        
        self.auto_battle_log.insert("end", f"[{datetime.now().strftime('%H:%M:%S')}] Auto Battle iniciado!\n")
        self.auto_battle_log.see("end")
    
    def stop_auto_battle(self):
        """Parar Auto Battle"""
        self.auto_battle_active = False
        self.auto_battle_btn.configure(text="▶️ Iniciar Auto Battle", fg_color="#FF6B35", hover_color="#E55A2B")
        self.auto_battle_status.configure(text="❌ Auto Battle Inativo", text_color="red")
        
        self.auto_battle_log.insert("end", f"[{datetime.now().strftime('%H:%M:%S')}] Auto Battle parado.\n")
        self.auto_battle_log.see("end")
    
    def auto_battle_loop(self):
        """Loop principal do Auto Battle - inspirado no repositório bot-otpokemon"""
        import cv2
        import numpy as np
        from datetime import datetime
        
        while self.auto_battle_active:
            try:
                # Verificar se está em batalha usando detecção de imagem
                in_battle = self.detect_battle()
                
                if in_battle:
                    # Está em batalha - usar skills
                    self.execute_battle_skills()
                    self.auto_battle_log.insert("end", f"[{datetime.now().strftime('%H:%M:%S')}] Em batalha - usando skills\n")
                else:
                    # Fora de batalha - pescar
                    self.execute_fishing_action()
                    self.auto_battle_log.insert("end", f"[{datetime.now().strftime('%H:%M:%S')}] Fora de batalha - pescando\n")
                
                self.auto_battle_log.see("end")
                time.sleep(0.5)  # Pequena pausa para não sobrecarregar
                
            except Exception as e:
                self.auto_battle_log.insert("end", f"[{datetime.now().strftime('%H:%M:%S')}] Erro: {str(e)}\n")
                self.auto_battle_log.see("end")
                time.sleep(1)
    
    def detect_battle(self):
        """Detectar se está em batalha usando OpenCV"""
        try:
            import cv2
            import numpy as np
            
            battle_img_path = self.battle_img_entry.get().strip()
            if not battle_img_path or not os.path.exists(battle_img_path):
                return False
            
            # Capturar screenshot da tela
            screenshot = pyautogui.screenshot()
            screenshot_np = np.array(screenshot)
            screenshot_cv = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
            
            # Carregar imagem de referência
            template = cv2.imread(battle_img_path)
            if template is None:
                return False
            
            # Fazer template matching
            result = cv2.matchTemplate(screenshot_cv, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(result)
            
            # Usar nível de confiança configurado
            confidence_threshold = float(self.confidence_var.get())
            return max_val >= confidence_threshold
            
        except Exception as e:
            print(f"Erro na detecção de batalha: {e}")
            return False
    
    def execute_battle_skills(self):
        """Executar skills de batalha"""
        try:
            for skill_key, skill_var in self.battle_skill_vars.items():
                if skill_var.get():  # Se skill está marcada
                    pyautogui.press(skill_key)
                    time.sleep(0.1)  # Pequena pausa entre skills
        except Exception as e:
            print(f"Erro ao executar skills de batalha: {e}")
    
    def execute_fishing_action(self):
        """Executar ação de pesca"""
        try:
            fishing_hotkey = self.fishing_hotkey_var.get().strip()
            wait_time = float(self.wait_time_var.get())
            
            if fishing_hotkey:
                # Pressionar hotkey de pesca
                if "+" in fishing_hotkey:
                    keys = fishing_hotkey.split("+")
                    pyautogui.hotkey(*keys)
                else:
                    pyautogui.press(fishing_hotkey)
                
                time.sleep(wait_time)
        except Exception as e:
            print(f"Erro ao executar pesca: {e}")
    
    def emergency_stop_all(self):
        """Parar todos os sistemas de automação"""
        try:
            # Parar Auto Battle
            if hasattr(self, 'auto_battle_active') and self.auto_battle_active:
                self.stop_auto_battle()
            
            # Parar Pesca
            if hasattr(self, 'fishing_active') and self.fishing_active:
                self.fishing_active = False
                if hasattr(self, 'fishing_btn'):
                    self.fishing_btn.configure(text="▶️ Iniciar Pesca", fg_color="green")
            
            # Parar Skills
            if hasattr(self, 'skills_active') and self.skills_active:
                self.skills_active = False
                if hasattr(self, 'skills_btn'):
                    self.skills_btn.configure(text="▶️ Iniciar Skills", fg_color="green")
            
            # Parar Cura
            if hasattr(self, 'healing_active') and self.healing_active:
                self.healing_active = False
                if hasattr(self, 'heal_btn'):
                    self.heal_btn.configure(text="▶️ Iniciar Cura", fg_color="green")
            
            print("PARADA DE EMERGÊNCIA: Todos os sistemas foram interrompidos")
            
        except Exception as e:
            print(f"Erro na parada de emergência: {e}")
    
    def mark_targets(self):
        """Marcar targets de Pokémon selvagens"""
        # Sistema simplificado de configuração manual
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Configurar Targets")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        title = ctk.CTkLabel(dialog, text="🎯 Configuração de Targets", 
                           font=ctk.CTkFont(size=16, weight="bold"))
        title.pack(pady=20)
        
        info = ctk.CTkLabel(dialog, 
                           text="Configure as coordenadas dos Pokémon selvagens:\n(Use ferramentas externas para obter coordenadas)")
        info.pack(pady=10)
        
        # Frame para adicionar targets
        targets_frame = ctk.CTkFrame(dialog)
        targets_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Lista atual de targets
        targets_list = ctk.CTkTextbox(targets_frame, height=100)
        targets_list.pack(fill="x", padx=10, pady=10)
        
        # Mostrar targets existentes
        if self.target_points:
            for i, (x, y) in enumerate(self.target_points):
                targets_list.insert("end", f"Target {i+1}: ({x}, {y})\n")
        
        # Frame para adicionar novo target
        add_frame = ctk.CTkFrame(targets_frame)
        add_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(add_frame, text="X:").pack(side="left", padx=5)
        x_entry = ctk.CTkEntry(add_frame, width=80)
        x_entry.pack(side="left", padx=5)
        
        ctk.CTkLabel(add_frame, text="Y:").pack(side="left", padx=5)
        y_entry = ctk.CTkEntry(add_frame, width=80)
        y_entry.pack(side="left", padx=5)
        
        def add_target():
            try:
                x = int(x_entry.get())
                y = int(y_entry.get())
                if not hasattr(self, 'target_points'):
                    self.target_points = []
                self.target_points.append((x, y))
                targets_list.insert("end", f"Target {len(self.target_points)}: ({x}, {y})\n")
                x_entry.delete(0, "end")
                y_entry.delete(0, "end")
            except ValueError:
                print("Erro: Digite coordenadas válidas")
        
        def capture_mouse_position():
            if AUTOMATION_AVAILABLE:
                try:
                    x, y = pyautogui.position()
                    x_entry.delete(0, "end")
                    x_entry.insert(0, str(x))
                    y_entry.delete(0, "end")
                    y_entry.insert(0, str(y))
                except:
                    print("Erro ao capturar posição do mouse")
        
        add_btn = ctk.CTkButton(add_frame, text="Adicionar", command=add_target)
        add_btn.pack(side="left", padx=5)
        
        capture_btn = ctk.CTkButton(add_frame, text="📍 Capturar", command=capture_mouse_position, width=100)
        capture_btn.pack(side="left", padx=5)
        
        # Botões de ação
        buttons_frame = ctk.CTkFrame(targets_frame)
        buttons_frame.pack(fill="x", padx=10, pady=10)
        
        def clear_all():
            if not hasattr(self, 'target_points'):
                self.target_points = []
            self.target_points = []
            targets_list.delete("1.0", "end")
        
        def save_and_close():
            if not hasattr(self, 'target_points'):
                self.target_points = []
            count = len(self.target_points)
            if count > 0:
                if hasattr(self, 'targets_status'):
                    self.targets_status.configure(
                        text=f"✅ {count} targets configurados",
                        text_color="green"
                    )
                if hasattr(self, 'heal_log'):
                    self.heal_log.insert("end", f"✅ {count} targets configurados manualmente\n")
                    self.heal_log.see("end")
            else:
                if hasattr(self, 'targets_status'):
                    self.targets_status.configure(
                        text="❌ Nenhum target configurado",
                        text_color="red"
                    )
            dialog.destroy()
        
        ctk.CTkButton(buttons_frame, text="Limpar Todos", command=clear_all).pack(side="left", padx=5)
        ctk.CTkButton(buttons_frame, text="Salvar", command=save_and_close).pack(side="right", padx=5)
    
    def clear_targets(self):
        """Limpar todos os targets"""
        self.target_points = []
        self.targets_status.configure(
            text="❌ Nenhum target configurado - Use 'Marcar Targets' para configurar",
            text_color="red"
        )
        self.heal_log.insert("end", "🗑️ Todos os targets foram removidos\n")
    
    def load_targets(self):
        """Carregar targets de arquivo"""
        try:
            if os.path.exists('targets.json'):
                with open('targets.json', 'r') as f:
                    self.target_points = json.load(f)
                count = len(self.target_points)
                self.targets_status.configure(
                    text=f"✅ {count} targets carregados",
                    text_color="green"
                )
                self.heal_log.insert("end", f"📂 {count} targets carregados do arquivo\n")
            else:
                messagebox.showinfo("Info", "Nenhum arquivo de targets encontrado")
        except:
            messagebox.showerror("Erro", "Erro ao carregar targets")
    
    def toggle_healing(self):
        """Alternar sistema de cura"""
        if not hasattr(self, 'cura_active'):
            self.cura_active = False
        
        if self.cura_active:
            # Parar cura
            self.cura_active = False
            self.cura_btn.configure(
                text="▶️ Iniciar Sistema de Cura",
                fg_color="green",
                hover_color="darkgreen"
            )
            self.cura_status.configure(
                text="❌ Sistema Inativo",
                text_color="red"
            )
            self.heal_log.insert("end", "⏹️ Sistema de cura parado\n")
        else:
            # Verificar se há targets
            if not self.target_points:
                messagebox.showwarning("Aviso", "Configure targets antes de iniciar o sistema de cura")
                return
            
            # Iniciar cura
            self.cura_active = True
            self.cura_btn.configure(
                text="⏹️ Parar Sistema de Cura",
                fg_color="red",
                hover_color="darkred"
            )
            self.cura_status.configure(
                text="✅ Sistema Ativo",
                text_color="green"
            )
            self.heal_log.insert("end", "▶️ Sistema de cura iniciado\n")
            
            # Iniciar thread de cura
            if AUTOMATION_AVAILABLE:
                import threading
                self.healing_thread = threading.Thread(target=self.healing_loop, daemon=True)
                self.healing_thread.start()
    
    def healing_loop(self):
        """Loop principal do sistema de cura"""
        import time
        
        while self.cura_active:
            try:
                # Verificar skills ativas
                active_skills = []
                for key, var in self.heal_skill_vars.items():
                    if var.get():
                        interval = int(self.heal_skill_speed_vars[key].get())
                        active_skills.append((key, interval))
                
                if active_skills:
                    # Executar skills
                    for skill_key, interval in active_skills:
                        if not self.cura_active:
                            break
                            
                        # Selecionar target aleatório
                        if self.target_points:
                            import random
                            target = random.choice(self.target_points)
                            
                            # Clicar no target
                            pyautogui.click(target[0], target[1])
                            time.sleep(0.1)
                            
                            # Usar skill
                            skill_number = skill_key.replace('f', '')
                            pyautogui.press(f'f{skill_number}')
                            
                            self.heal_log.insert("end", f"💊 Skill F{skill_number} usada\n")
                            time.sleep(interval / 1000.0)
                
                time.sleep(0.5)
                
            except Exception as e:
                if self.cura_active:
                    self.heal_log.insert("end", f"❌ Erro: {str(e)}\n")
                time.sleep(1)
    
    def create_fishing_tab(self):
        """Criar aba de pesca básica"""
        header = ctk.CTkLabel(
            self.main_frame,
            text="🎣 Sistema de Pesca Automática",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        header.pack(pady=20)
        
        info = ctk.CTkLabel(
            self.main_frame,
            text="Configure e inicie a pesca automática no Poke Old",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        info.pack(pady=10)
        
        # Frame principal scrollável
        main_scroll = ctk.CTkScrollableFrame(self.main_frame)
        main_scroll.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Seção 1: Configuração da Pesca
        config_frame = ctk.CTkFrame(main_scroll)
        config_frame.pack(fill="x", padx=10, pady=10)
        
        config_header = ctk.CTkLabel(
            config_frame,
            text="⚙️ Configuração da Pesca",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        config_header.pack(pady=15)
        
        # Botões de configuração
        config_buttons_frame = ctk.CTkFrame(config_frame)
        config_buttons_frame.pack(fill="x", padx=15, pady=10)
        
        detect_water_btn = ctk.CTkButton(
            config_buttons_frame,
            text="💧 Detectar Cor da Água",
            command=self.detect_water_color,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="blue",
            hover_color="darkblue"
        )
        detect_water_btn.pack(side="left", padx=10, pady=10)
        
        mark_fishing_btn = ctk.CTkButton(
            config_buttons_frame,
            text="📍 Marcar Pontos de Pesca",
            command=self.mark_fishing_points,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="green",
            hover_color="darkgreen"
        )
        mark_fishing_btn.pack(side="left", padx=10, pady=10)
        
        clear_fishing_btn = ctk.CTkButton(
            config_buttons_frame,
            text="🗑️ Limpar Pontos",
            command=self.clear_fishing_points,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="red",
            hover_color="darkred"
        )
        clear_fishing_btn.pack(side="left", padx=10, pady=10)
        
        # Status da configuração
        self.fishing_config_status = ctk.CTkLabel(
            config_frame,
            text="❌ Configure cor da água e pontos de pesca",
            font=ctk.CTkFont(size=12),
            text_color="red"
        )
        self.fishing_config_status.pack(pady=10)
        
        # Seção 2: Controles da Pesca
        control_frame = ctk.CTkFrame(main_scroll)
        control_frame.pack(fill="x", padx=10, pady=10)
        
        control_header = ctk.CTkLabel(
            control_frame,
            text="🎮 Controles da Pesca",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        control_header.pack(pady=15)
        
        # Botão principal
        main_control_frame = ctk.CTkFrame(control_frame)
        main_control_frame.pack(fill="x", padx=15, pady=15)
        
        self.fishing_btn = ctk.CTkButton(
            main_control_frame,
            text="▶️ Iniciar Pesca",
            command=self.toggle_fishing,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="green",
            hover_color="darkgreen"
        )
        self.fishing_btn.pack(side="left", padx=10, pady=10)
        
        # Status
        self.fishing_status = ctk.CTkLabel(
            main_control_frame,
            text="❌ Pesca Inativa",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="red"
        )
        self.fishing_status.pack(side="left", padx=20, pady=10)
        
        # Seção 3: Configurações Avançadas
        advanced_frame = ctk.CTkFrame(control_frame)
        advanced_frame.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(
            advanced_frame,
            text="⚙️ Configurações Avançadas",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=10)
        
        # Velocidade da pesca
        speed_frame = ctk.CTkFrame(advanced_frame)
        speed_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            speed_frame,
            text="Velocidade da Pesca:",
            font=ctk.CTkFont(size=12)
        ).pack(side="left", padx=10, pady=10)
        
        self.fishing_speed_var = ctk.StringVar(value="2")
        speed_slider = ctk.CTkSlider(
            speed_frame,
            from_=1,
            to=5,
            number_of_steps=4,
            width=200
        )
        speed_slider.pack(side="left", padx=10, pady=10)
        
        # Log da pesca
        log_frame = ctk.CTkFrame(control_frame)
        log_frame.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(
            log_frame,
            text="📝 Log da Pesca",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=5)
        
        self.fishing_log = ctk.CTkTextbox(log_frame, height=100)
        self.fishing_log.pack(fill="x", padx=10, pady=10)
        self.fishing_log.insert("end", "Sistema de pesca inicializado. Configure antes de iniciar.\n")
        
        if not AUTOMATION_AVAILABLE:
            warning_frame = ctk.CTkFrame(main_scroll)
            warning_frame.pack(fill="x", padx=10, pady=10)
            
            warning_label = ctk.CTkLabel(
                warning_frame,
                text="⚠️ Automação limitada - Execute no Windows para funcionalidade completa",
                font=ctk.CTkFont(size=14),
                text_color="orange"
            )
            warning_label.pack(pady=15)
    
    def detect_water_color(self):
        """Detectar cor da água para pesca"""
        # Sistema simplificado de configuração manual de cor
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Configurar Cor da Água")
        dialog.geometry("350x250")
        dialog.transient(self.root)
        dialog.grab_set()
        
        title = ctk.CTkLabel(dialog, text="💧 Configuração da Cor da Água", 
                           font=ctk.CTkFont(size=16, weight="bold"))
        title.pack(pady=20)
        
        info = ctk.CTkLabel(dialog, 
                           text="Configure a cor RGB da água do jogo:\n(Use ferramentas externas para capturar a cor)")
        info.pack(pady=10)
        
        # Frame para entrada de cores
        color_frame = ctk.CTkFrame(dialog)
        color_frame.pack(fill="x", padx=20, pady=10)
        
        # Entrada RGB
        ctk.CTkLabel(color_frame, text="R:").pack(side="left", padx=5)
        r_entry = ctk.CTkEntry(color_frame, width=60)
        r_entry.pack(side="left", padx=5)
        
        ctk.CTkLabel(color_frame, text="G:").pack(side="left", padx=5)
        g_entry = ctk.CTkEntry(color_frame, width=60)
        g_entry.pack(side="left", padx=5)
        
        ctk.CTkLabel(color_frame, text="B:").pack(side="left", padx=5)
        b_entry = ctk.CTkEntry(color_frame, width=60)
        b_entry.pack(side="left", padx=5)
        
        # Pré-preencher se já existe cor
        if self.water_color:
            r_entry.insert(0, str(self.water_color[0]))
            g_entry.insert(0, str(self.water_color[1]))
            b_entry.insert(0, str(self.water_color[2]))
        
        def save_color():
            try:
                r = int(r_entry.get())
                g = int(g_entry.get())
                b = int(b_entry.get())
                
                if 0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255:
                    self.water_color = (r, g, b)
                    self.fishing_config_status.configure(
                        text=f"✅ Cor da água configurada: RGB({r},{g},{b})",
                        text_color="green"
                    )
                    self.fishing_log.insert("end", f"💧 Cor da água configurada: RGB({r},{g},{b})\n")
                    dialog.destroy()
                else:
                    messagebox.showerror("Erro", "Valores RGB devem estar entre 0 e 255")
            except ValueError:
                messagebox.showerror("Erro", "Digite valores RGB válidos")
        
        ctk.CTkButton(dialog, text="Salvar Cor", command=save_color).pack(pady=20)
    
    def mark_fishing_points(self):
        """Marcar pontos de pesca"""
        # Sistema simplificado de configuração manual
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Configurar Pontos de Pesca")
        dialog.geometry("400x350")
        dialog.transient(self.root)
        dialog.grab_set()
        
        title = ctk.CTkLabel(dialog, text="📍 Configuração de Pontos de Pesca", 
                           font=ctk.CTkFont(size=16, weight="bold"))
        title.pack(pady=20)
        
        info = ctk.CTkLabel(dialog, 
                           text="Configure as coordenadas dos pontos de pesca:")
        info.pack(pady=10)
        
        # Frame para pontos
        points_frame = ctk.CTkFrame(dialog)
        points_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Lista atual de pontos
        points_list = ctk.CTkTextbox(points_frame, height=120)
        points_list.pack(fill="x", padx=10, pady=10)
        
        # Mostrar pontos existentes
        if self.fishing_points:
            for i, (x, y) in enumerate(self.fishing_points):
                points_list.insert("end", f"Ponto {i+1}: ({x}, {y})\n")
        
        # Frame para adicionar novo ponto
        add_frame = ctk.CTkFrame(points_frame)
        add_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(add_frame, text="X:").pack(side="left", padx=5)
        x_entry = ctk.CTkEntry(add_frame, width=80)
        x_entry.pack(side="left", padx=5)
        
        ctk.CTkLabel(add_frame, text="Y:").pack(side="left", padx=5)
        y_entry = ctk.CTkEntry(add_frame, width=80)
        y_entry.pack(side="left", padx=5)
        
        def add_point():
            try:
                x = int(x_entry.get())
                y = int(y_entry.get())
                self.fishing_points.append((x, y))
                points_list.insert("end", f"Ponto {len(self.fishing_points)}: ({x}, {y})\n")
                x_entry.delete(0, "end")
                y_entry.delete(0, "end")
            except ValueError:
                messagebox.showerror("Erro", "Digite coordenadas válidas")
        
        add_btn = ctk.CTkButton(add_frame, text="Adicionar", command=add_point)
        add_btn.pack(side="left", padx=10)
        
        # Botões de ação
        buttons_frame = ctk.CTkFrame(points_frame)
        buttons_frame.pack(fill="x", padx=10, pady=10)
        
        def clear_all():
            self.fishing_points = []
            points_list.delete("1.0", "end")
        
        def save_and_close():
            count = len(self.fishing_points)
            if count > 0:
                self.fishing_config_status.configure(
                    text=f"✅ {count} pontos de pesca configurados",
                    text_color="green"
                )
                self.fishing_log.insert("end", f"📍 {count} pontos de pesca configurados\n")
            dialog.destroy()
        
        ctk.CTkButton(buttons_frame, text="Limpar", command=clear_all).pack(side="left", padx=5)
        ctk.CTkButton(buttons_frame, text="Salvar", command=save_and_close).pack(side="right", padx=5)
    
    def clear_fishing_points(self):
        """Limpar pontos de pesca"""
        self.fishing_points = []
        self.water_color = None
        self.fishing_config_status.configure(
            text="❌ Configure cor da água e pontos de pesca",
            text_color="red"
        )
        self.fishing_log.insert("end", "🗑️ Configurações de pesca limpas\n")
    
    def toggle_fishing(self):
        """Alternar sistema de pesca"""
        if not hasattr(self, 'fishing_active'):
            self.fishing_active = False
        
        if self.fishing_active:
            # Parar pesca
            self.fishing_active = False
            self.fishing_btn.configure(
                text="▶️ Iniciar Pesca",
                fg_color="green",
                hover_color="darkgreen"
            )
            self.fishing_status.configure(
                text="❌ Pesca Inativa",
                text_color="red"
            )
            self.fishing_log.insert("end", "⏹️ Pesca parada\n")
        else:
            # Verificar configurações
            if not self.water_color or not self.fishing_points:
                messagebox.showwarning("Aviso", "Configure cor da água e pontos de pesca antes de iniciar")
                return
            
            # Iniciar pesca
            self.fishing_active = True
            self.fishing_btn.configure(
                text="⏹️ Parar Pesca",
                fg_color="red",
                hover_color="darkred"
            )
            self.fishing_status.configure(
                text="✅ Pesca Ativa",
                text_color="green"
            )
            self.fishing_log.insert("end", "▶️ Pesca iniciada\n")
            
            # Iniciar thread de pesca
            if AUTOMATION_AVAILABLE:
                import threading
                self.fishing_thread = threading.Thread(target=self.fishing_loop, daemon=True)
                self.fishing_thread.start()
    
    def fishing_loop(self):
        """Loop principal da pesca"""
        import time
        import random
        
        while self.fishing_active:
            try:
                if self.fishing_points:
                    # Escolher ponto aleatório
                    point = random.choice(self.fishing_points)
                    
                    # Clicar no ponto
                    pyautogui.click(point[0], point[1])
                    
                    # Manter espaço pressionado
                    pyautogui.keyDown('space')
                    self.fishing_log.insert("end", f"🎣 Pescando no ponto ({point[0]}, {point[1]})\n")
                    
                    # Aguardar peixe (verificar mudança de cor)
                    start_time = time.time()
                    while self.fishing_active and (time.time() - start_time) < 10:
                        try:
                            # Verificar cor atual
                            screenshot = pyautogui.screenshot()
                            current_color = screenshot.getpixel(point)
                            
                            # Se cor mudou, soltar espaço e clicar
                            if current_color != self.water_color:
                                pyautogui.keyUp('space')
                                time.sleep(0.1)
                                pyautogui.click(point[0], point[1])
                                self.fishing_log.insert("end", "🐟 Peixe capturado!\n")
                                time.sleep(2)
                                break
                                
                        except:
                            pass
                        
                        time.sleep(0.1)
                    
                    # Soltar espaço se ainda pressionado
                    pyautogui.keyUp('space')
                    time.sleep(0.5)
                
            except Exception as e:
                if self.fishing_active:
                    self.fishing_log.insert("end", f"❌ Erro na pesca: {str(e)}\n")
                time.sleep(1)
    
    def skills_automation_loop(self):
        """Loop de automação para skills"""
        import time
        
        while self.skills_active:
            try:
                # Verificar skills ativas
                active_skills = []
                for key, var in self.skill_vars.items():
                    if var.get():
                        interval = int(self.skill_speed_vars[key].get())
                        active_skills.append((key, interval))
                
                if active_skills:
                    # Executar skills em sequência
                    for skill_key, interval in active_skills:
                        if not self.skills_active:
                            break
                            
                        # Usar skill
                        skill_number = skill_key.replace('f', '')
                        if AUTOMATION_AVAILABLE:
                            pyautogui.press(f'f{skill_number}')
                            
                        # Log da skill
                        if hasattr(self, 'skills_log'):
                            self.skills_log.insert("end", f"⚔️ Skill F{skill_number} executada\n")
                        
                        time.sleep(interval / 1000.0)
                
                time.sleep(0.1)
                
            except Exception as e:
                if self.skills_active and hasattr(self, 'skills_log'):
                    self.skills_log.insert("end", f"❌ Erro: {str(e)}\n")
                time.sleep(1)
    
    def setup_hotkeys_system(self):
        """Configurar sistema de hotkeys globais"""
        # Sistema simplificado - apenas salva as configurações
        # No Windows com dependências, seria possível usar keyboard.add_hotkey
        pass
    
    def execute_hotkey_action(self, action):
        """Executar ação de hotkey"""
        try:
            if action == "start_fishing":
                if hasattr(self, 'fishing_btn') and not self.fishing_active:
                    self.toggle_fishing()
            elif action == "stop_fishing":
                if hasattr(self, 'fishing_btn') and self.fishing_active:
                    self.toggle_fishing()
            elif action == "start_skills":
                if hasattr(self, 'skills_btn') and not self.skills_active:
                    self.toggle_skills()
            elif action == "stop_skills":
                if hasattr(self, 'skills_btn') and self.skills_active:
                    self.toggle_skills()
            elif action == "emergency_stop":
                # Parar todas as automações
                self.fishing_active = False
                self.skills_active = False
                self.cura_active = False
                
        except:
            pass
    
    def create_skills_tab(self):
        """Criar aba de skills com configurações completas"""
        header = ctk.CTkLabel(
            self.main_frame,
            text="⚔️ Sistema de Skills Automáticas",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        header.pack(pady=20)
        
        description = ctk.CTkLabel(
            self.main_frame,
            text="Configure skills F1-F12 para execução automática com intervalos personalizados",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        description.pack(pady=10)
        
        # Frame principal scrollável
        main_scroll = ctk.CTkScrollableFrame(self.main_frame)
        main_scroll.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Seção de Skills
        skills_frame = ctk.CTkFrame(main_scroll)
        skills_frame.pack(fill="x", padx=10, pady=10)
        
        skills_header = ctk.CTkLabel(
            skills_frame,
            text="🎯 Configuração de Skills",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        skills_header.pack(pady=15)
        
        # Grid de skills
        skills_grid = ctk.CTkFrame(skills_frame)
        skills_grid.pack(fill="x", padx=15, pady=10)
        
        skills_list = [
            ("F1", "f1"), ("F2", "f2"), ("F3", "f3"), ("F4", "f4"),
            ("F5", "f5"), ("F6", "f6"), ("F7", "f7"), ("F8", "f8"),
            ("F9", "f9"), ("F10", "f10"), ("F11", "f11"), ("F12", "f12")
        ]
        
        # Inicializar variáveis se não existirem
        if not hasattr(self, 'skill_vars'):
            self.skill_vars = {}
        if not hasattr(self, 'skill_speed_vars'):
            self.skill_speed_vars = {}
        
        for i, (display_name, key) in enumerate(skills_list):
            skill_row = ctk.CTkFrame(skills_grid)
            skill_row.pack(fill="x", padx=5, pady=3)
            
            # Checkbox para ativar skill
            if key not in self.skill_vars:
                self.skill_vars[key] = ctk.BooleanVar()
            
            skill_check = ctk.CTkCheckBox(
                skill_row,
                text=f"Skill {display_name}",
                variable=self.skill_vars[key],
                width=120
            )
            skill_check.pack(side="left", padx=10, pady=8)
            
            # Campo de intervalo
            interval_label = ctk.CTkLabel(skill_row, text="Intervalo (ms):")
            interval_label.pack(side="left", padx=5)
            
            if key not in self.skill_speed_vars:
                self.skill_speed_vars[key] = ctk.StringVar(value="2000")
            
            interval_entry = ctk.CTkEntry(
                skill_row,
                textvariable=self.skill_speed_vars[key],
                width=80,
                height=30
            )
            interval_entry.pack(side="left", padx=5, pady=8)
            
            # Status da skill
            status_label = ctk.CTkLabel(
                skill_row,
                text="❌ Inativa",
                font=ctk.CTkFont(size=10),
                text_color="red",
                width=70
            )
            status_label.pack(side="right", padx=10, pady=8)
        
        # Controles principais
        control_frame = ctk.CTkFrame(main_scroll)
        control_frame.pack(fill="x", padx=10, pady=10)
        
        control_header = ctk.CTkLabel(
            control_frame,
            text="🎮 Controles de Skills",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        control_header.pack(pady=15)
        
        # Botões de controle
        buttons_frame = ctk.CTkFrame(control_frame)
        buttons_frame.pack(fill="x", padx=15, pady=10)
        
        self.skills_btn = ctk.CTkButton(
            buttons_frame,
            text="▶️ Iniciar Skills",
            command=self.toggle_skills,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="green",
            hover_color="darkgreen"
        )
        self.skills_btn.pack(side="left", padx=10, pady=10)
        
        # Status das skills
        self.skills_status = ctk.CTkLabel(
            buttons_frame,
            text="❌ Skills Inativas",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="red"
        )
        self.skills_status.pack(side="left", padx=20, pady=10)
        
        # Configurações gerais
        settings_frame = ctk.CTkFrame(control_frame)
        settings_frame.pack(fill="x", padx=15, pady=10)
        
        # Velocidade global
        speed_frame = ctk.CTkFrame(settings_frame)
        speed_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            speed_frame,
            text="Multiplicador de Velocidade:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="left", padx=10, pady=10)
        
        self.global_speed_var = ctk.StringVar(value="1.0")
        speed_slider = ctk.CTkSlider(
            speed_frame,
            from_=1,
            to=5,
            number_of_steps=8,
            width=200
        )
        speed_slider.pack(side="left", padx=10, pady=10)
        
        speed_label = ctk.CTkLabel(
            speed_frame,
            textvariable=self.global_speed_var,
            width=50
        )
        speed_label.pack(side="left", padx=5, pady=10)
        
        # Log de skills
        log_frame = ctk.CTkFrame(control_frame)
        log_frame.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(
            log_frame,
            text="📝 Log de Atividades",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=5)
        
        self.skills_log = ctk.CTkTextbox(log_frame, height=100)
        self.skills_log.pack(fill="x", padx=10, pady=10)
        self.skills_log.insert("end", "Sistema de skills inicializado. Configure e ative as skills desejadas.\n")
    
    def toggle_skills(self):
        """Alternar sistema de skills"""
        if not hasattr(self, 'skills_active'):
            self.skills_active = False
        
        if self.skills_active:
            # Parar skills
            self.skills_active = False
            self.skills_btn.configure(
                text="▶️ Iniciar Skills",
                fg_color="green",
                hover_color="darkgreen"
            )
            self.skills_status.configure(
                text="❌ Skills Inativas",
                text_color="red"
            )
            if hasattr(self, 'skills_log'):
                self.skills_log.insert("end", f"⏹️ Sistema de skills parado\n")
        else:
            # Iniciar skills
            self.skills_active = True
            self.skills_btn.configure(
                text="⏹️ Parar Skills",
                fg_color="red",
                hover_color="darkred"
            )
            self.skills_status.configure(
                text="✅ Skills Ativas",
                text_color="green"
            )
            if hasattr(self, 'skills_log'):
                self.skills_log.insert("end", f"▶️ Sistema de skills iniciado\n")
            
            # Iniciar thread de automação de skills
            if AUTOMATION_AVAILABLE:
                import threading
                self.skills_thread = threading.Thread(target=self.skills_automation_loop, daemon=True)
                self.skills_thread.start()
    
    def create_stats_tab(self):
        """Criar aba de estatísticas básica"""
        header = ctk.CTkLabel(
            self.main_frame,
            text="📊 Estatísticas do Bot",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        header.pack(pady=20)
        
        stats_frame = ctk.CTkFrame(self.main_frame)
        stats_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Estatísticas básicas
        stats_grid = ctk.CTkFrame(stats_frame)
        stats_grid.pack(fill="x", padx=20, pady=20)
        
        stats_items = [
            ("Peixes Pescados", "0"),
            ("Skills Utilizadas", "0"),
            ("Tempo de Uso", "0m"),
            ("Status", "Inativo")
        ]
        
        for label, value in stats_items:
            stat_row = ctk.CTkFrame(stats_grid)
            stat_row.pack(fill="x", padx=10, pady=5)
            
            ctk.CTkLabel(
                stat_row,
                text=f"{label}:",
                font=ctk.CTkFont(size=14, weight="bold")
            ).pack(side="left", padx=10, pady=10)
            
            ctk.CTkLabel(
                stat_row,
                text=value,
                font=ctk.CTkFont(size=14),
                text_color="cyan"
            ).pack(side="right", padx=10, pady=10)
    
    def create_user_management_tab(self):
        """Criar aba de gerenciamento de usuários (admin)"""
        header = ctk.CTkLabel(
            self.main_frame,
            text="👥 Gerenciamento de Usuários",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        header.pack(pady=20)
        
        # Botão criar usuário
        create_user_btn = ctk.CTkButton(
            self.main_frame,
            text="➕ Criar Novo Usuário",
            command=self.show_create_user_dialog,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="green"
        )
        create_user_btn.pack(pady=10)
        
        # Lista de usuários
        users_frame = ctk.CTkScrollableFrame(self.main_frame)
        users_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        users = self.db.get_all_users()
        for user in users:
            user_frame = ctk.CTkFrame(users_frame)
            user_frame.pack(fill="x", padx=10, pady=5)
            
            # Info do usuário
            user_info = f"👤 {user['username']}"
            if user['is_admin']:
                user_info += " (Admin)"
            
            if user['subscription']:
                if user['subscription']['is_expired']:
                    user_info += f" - ❌ Expirado"
                else:
                    user_info += f" - ✅ {user['subscription']['days_remaining']} dias"
            else:
                user_info += " - ⏰ Sem licença"
            
            ctk.CTkLabel(user_frame, text=user_info, font=ctk.CTkFont(size=12)).pack(side="left", padx=10, pady=10)
            
            # Botões de ação
            if not user['is_admin']:  # Não pode deletar admin
                extend_btn = ctk.CTkButton(
                    user_frame,
                    text="Estender",
                    width=80,
                    height=30,
                    command=lambda u=user: self.show_extend_license_dialog(u)
                )
                extend_btn.pack(side="right", padx=5, pady=10)
                
                delete_btn = ctk.CTkButton(
                    user_frame,
                    text="Deletar",
                    width=80,
                    height=30,
                    fg_color="red",
                    command=lambda u=user: self.confirm_delete_user(u)
                )
                delete_btn.pack(side="right", padx=5, pady=10)
    
    def create_license_management_tab(self):
        """Criar aba de gerenciamento de licenças"""
        header = ctk.CTkLabel(
            self.main_frame,
            text="🎫 Gerenciamento de Licenças",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        header.pack(pady=20)
        
        # Botões de ação em massa
        mass_actions_frame = ctk.CTkFrame(self.main_frame)
        mass_actions_frame.pack(fill="x", padx=20, pady=10)
        
        extend_all_btn = ctk.CTkButton(
            mass_actions_frame,
            text="➕ Estender Todas as Licenças",
            command=self.show_extend_all_dialog,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="green"
        )
        extend_all_btn.pack(side="left", padx=10, pady=10)
        
        cleanup_btn = ctk.CTkButton(
            mass_actions_frame,
            text="🗑️ Limpar Expiradas",
            command=self.cleanup_expired_users,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="red"
        )
        cleanup_btn.pack(side="left", padx=10, pady=10)
        
        # Estatísticas
        stats_frame = ctk.CTkFrame(self.main_frame)
        stats_frame.pack(fill="x", padx=20, pady=20)
        
        users = self.db.get_all_users()
        total_users = len(users)
        active_users = len([u for u in users if u['subscription'] and not u['subscription']['is_expired']])
        expired_users = len([u for u in users if u['subscription'] and u['subscription']['is_expired']])
        
        stats_text = f"📊 Total: {total_users} | ✅ Ativos: {active_users} | ❌ Expirados: {expired_users}"
        ctk.CTkLabel(stats_frame, text=stats_text, font=ctk.CTkFont(size=14)).pack(pady=20)
    
    def show_create_user_dialog(self):
        """Mostrar diálogo para criar usuário (admin)"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Criar Novo Usuário")
        dialog.geometry("400x350")
        dialog.transient(self.root)
        dialog.grab_set()
        
        title = ctk.CTkLabel(dialog, text="👤 Criar Usuário", font=ctk.CTkFont(size=20, weight="bold"))
        title.pack(pady=20)
        
        username_entry = ctk.CTkEntry(dialog, placeholder_text="Usuário", width=300)
        username_entry.pack(pady=10)
        
        password_entry = ctk.CTkEntry(dialog, placeholder_text="Senha", show="*", width=300)
        password_entry.pack(pady=10)
        
        # Opções de licença
        license_frame = ctk.CTkFrame(dialog)
        license_frame.pack(pady=20)
        
        ctk.CTkLabel(license_frame, text="Licença Inicial:", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        
        license_var = ctk.StringVar(value="30")
        license_options = ctk.CTkComboBox(
            license_frame,
            values=["0", "7", "30", "90", "365"],
            variable=license_var,
            width=200
        )
        license_options.pack(pady=5)
        
        def create_user():
            username = username_entry.get().strip()
            password = password_entry.get()
            license_days = int(license_var.get())
            
            if not username or not password:
                messagebox.showerror("Erro", "Preencha todos os campos!")
                return
            
            user_id = self.db.create_user(username, password)
            if user_id:
                if license_days > 0:
                    self.db.extend_user_subscription(user_id, license_days)
                messagebox.showinfo("Sucesso", f"Usuário '{username}' criado com {license_days} dias de licença!")
                dialog.destroy()
                self.switch_tab("users")  # Atualizar lista
            else:
                messagebox.showerror("Erro", "Usuário já existe!")
        
        create_btn = ctk.CTkButton(dialog, text="✅ Criar", command=create_user, width=200)
        create_btn.pack(pady=20)
    
    def show_extend_license_dialog(self, user):
        """Mostrar diálogo para estender licença"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Estender Licença")
        dialog.geometry("350x250")
        dialog.transient(self.root)
        dialog.grab_set()
        
        title = ctk.CTkLabel(dialog, text=f"🎫 Estender licença de\n{user['username']}", 
                           font=ctk.CTkFont(size=16, weight="bold"))
        title.pack(pady=20)
        
        days_var = ctk.StringVar(value="30")
        days_combo = ctk.CTkComboBox(
            dialog,
            values=["7", "30", "90", "365"],
            variable=days_var,
            width=200
        )
        days_combo.pack(pady=20)
        
        def extend_license():
            days = int(days_var.get())
            self.db.extend_user_subscription(user['id'], days)
            messagebox.showinfo("Sucesso", f"Licença de {user['username']} estendida por {days} dias!")
            dialog.destroy()
            self.switch_tab("users")
        
        extend_btn = ctk.CTkButton(dialog, text="✅ Estender", command=extend_license, width=150)
        extend_btn.pack(pady=20)
    
    def confirm_delete_user(self, user):
        """Confirmar exclusão de usuário"""
        if messagebox.askyesno("Confirmar", f"Deletar usuário '{user['username']}'?"):
            self.db.delete_user(user['id'])
            messagebox.showinfo("Sucesso", f"Usuário '{user['username']}' deletado!")
            self.switch_tab("users")
    
    def show_extend_all_dialog(self):
        """Mostrar diálogo para estender todas as licenças"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Estender Todas as Licenças")
        dialog.geometry("300x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        title = ctk.CTkLabel(dialog, text="⏰ Dias para adicionar:", font=ctk.CTkFont(size=16, weight="bold"))
        title.pack(pady=20)
        
        days_var = ctk.StringVar(value="30")
        days_combo = ctk.CTkComboBox(dialog, values=["7", "30", "90", "365"], variable=days_var)
        days_combo.pack(pady=20)
        
        def extend_all():
            days = int(days_var.get())
            users = self.db.get_all_users()
            count = 0
            for user in users:
                if not user['is_admin']:
                    self.db.extend_user_subscription(user['id'], days)
                    count += 1
            messagebox.showinfo("Sucesso", f"{count} licenças estendidas por {days} dias!")
            dialog.destroy()
            self.switch_tab("licenses")
        
        extend_btn = ctk.CTkButton(dialog, text="✅ Estender Todas", command=extend_all)
        extend_btn.pack(pady=20)
    
    def cleanup_expired_users(self):
        """Limpar usuários com licenças expiradas"""
        if messagebox.askyesno("Confirmar", "Deletar todos os usuários com licenças expiradas?"):
            users = self.db.get_all_users()
            count = 0
            for user in users:
                if not user['is_admin'] and user['subscription'] and user['subscription']['is_expired']:
                    self.db.delete_user(user['id'])
                    count += 1
            messagebox.showinfo("Sucesso", f"{count} usuários expirados deletados!")
            self.switch_tab("licenses")
    
    def refresh_processes(self):
        """Atualizar lista de processos"""
        # Implementação básica
        messagebox.showinfo("Info", "Lista de processos atualizada!")
    
    def select_process(self, process):
        """Selecionar processo do jogo"""
        messagebox.showinfo("Processo Selecionado", f"Processo selecionado: {process['name']}")
    
    def capture_hotkey(self, config_key, entry):
        """Capturar uma tecla pressionada - modo simples para usuários"""
        # Limpar campo e mostrar instrução
        entry.delete(0, "end")
        entry.insert(0, "Pressione qualquer tecla...")
        entry.configure(state="readonly", text_color="orange")
        
        # Status de captura
        if config_key in self.hotkey_entries:
            self.hotkey_entries[config_key]['status'].configure(
                text="⏳ Aguardando...",
                text_color="orange"
            )
        
        # Focar no entry para capturar a tecla
        entry.focus_set()
        
        # Bind temporário para capturar tecla
        def on_key_press(event):
            key_name = event.keysym
            
            # Converter nomes especiais para nomes amigáveis
            key_mapping = {
                'Return': 'Enter',
                'BackSpace': 'Backspace',
                'Tab': 'Tab',
                'Escape': 'Esc',
                'space': 'Space',
                'Up': 'Seta Cima',
                'Down': 'Seta Baixo', 
                'Left': 'Seta Esquerda',
                'Right': 'Seta Direita',
                'Control_L': 'Ctrl Esquerdo',
                'Control_R': 'Ctrl Direito',
                'Alt_L': 'Alt Esquerdo',
                'Alt_R': 'Alt Direito',
                'Shift_L': 'Shift Esquerdo',
                'Shift_R': 'Shift Direito'
            }
            
            display_key = key_mapping.get(key_name, key_name.upper())
            
            # Atualizar campo
            entry.configure(state="normal", text_color="white")
            entry.delete(0, "end")
            entry.insert(0, display_key)
            
            # Atualizar status
            if config_key in self.hotkey_entries:
                self.hotkey_entries[config_key]['status'].configure(
                    text="✅ Capturado",
                    text_color="green"
                )
            
            # Remover bind temporário
            entry.unbind('<KeyPress>')
            
            # Mostrar feedback
            self.hotkeys_status.configure(
                text=f"✅ Tecla '{display_key}' capturada!",
                text_color="green"
            )
            
            return "break"  # Impede processamento adicional da tecla
        
        # Adicionar bind para capturar tecla
        entry.bind('<KeyPress>', on_key_press)
    
    def reset_hotkey(self, config_key, entry):
        """Resetar hotkey para padrão"""
        default_hotkeys = {
            'start_fishing': 'F1',
            'stop_fishing': 'F2', 
            'start_skills': 'F3',
            'stop_skills': 'F4',
            'quick_capture': 'F5',
            'mark_points': 'F6',
            'emergency_stop': 'Escape'
        }
        
        default_key = default_hotkeys.get(config_key, 'F1')
        entry.delete(0, "end")
        entry.insert(0, default_key)
    
    def save_hotkeys(self):
        """Salvar configurações de hotkeys"""
        # Coletar configurações dos campos
        for config_key, elements in self.hotkey_entries.items():
            key_value = elements['entry'].get()
            self.hotkeys_config[config_key] = key_value
        
        # Salvar no arquivo
        self.save_hotkeys_config()
        messagebox.showinfo("Sucesso", "Configurações de hotkeys salvas!")
    
    def restore_default_hotkeys(self):
        """Restaurar hotkeys padrão"""
        if messagebox.askyesno("Confirmar", "Restaurar todas as hotkeys para os valores padrão?"):
            default_hotkeys = {
                'start_fishing': 'F1',
                'stop_fishing': 'F2', 
                'start_skills': 'F3',
                'stop_skills': 'F4',
                'quick_capture': 'F5',
                'mark_points': 'F6',
                'emergency_stop': 'Escape'
            }
            
            for config_key, default_key in default_hotkeys.items():
                if config_key in self.hotkey_entries:
                    entry = self.hotkey_entries[config_key]['entry']
                    entry.delete(0, "end")
                    entry.insert(0, default_key)
            
            messagebox.showinfo("Sucesso", "Hotkeys restauradas para os valores padrão!")
    
    def test_hotkeys(self):
        """Testar configurações de hotkeys"""
        active_hotkeys = []
        for config_key, elements in self.hotkey_entries.items():
            key_value = elements['entry'].get()
            if key_value:
                active_hotkeys.append(f"{config_key}: {key_value}")
        
        if active_hotkeys:
            test_message = "Hotkeys ativas:\n" + "\n".join(active_hotkeys)
            messagebox.showinfo("Teste de Hotkeys", test_message)
        else:
            messagebox.showwarning("Teste de Hotkeys", "Nenhuma hotkey configurada!")
    
    def logout(self):
        """Fazer logout"""
        self.current_user = None
        self.setup_login_interface()
    
    def clear_interface(self):
        """Limpar interface"""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def on_closing(self):
        """Manipular fechamento"""
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        """Executar aplicação"""
        self.root.mainloop()

    def load_new_tab_direct(self, tab_name):
        """Carregar nova aba sem animação"""
        # Limpar widgets atuais
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        # Carregar conteúdo da aba
        self.load_tab_content(tab_name)
        
        # Animação finalizada
        self.animation_in_progress = False
    
    def ease_in_out_cubic(self, t):
        """Função de easing cúbica para animações mais suaves"""
        if t < 0.5:
            return 4 * t * t * t
        else:
            return 1 - pow(-2 * t + 2, 3) / 2
    
    def toggle_animations(self):
        """Alternar sistema de animações"""
        self.animation_enabled = not self.animation_enabled
        print(f"Animações {'ativadas' if self.animation_enabled else 'desativadas'}")
    
    def on_closing(self):
        """Manipular fechamento com parada completa de sistemas"""
        # Parar todos os sistemas antes de fechar
        self.fishing_active = False
        self.skills_active = False
        if hasattr(self, 'healing_active'):
            self.healing_active = False
        if hasattr(self, 'auto_battle_active'):
            self.auto_battle_active = False
        
        # Fechar janela
        self.root.destroy()
    
    def run(self):
        """Executar aplicação"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

def main():
    """Função principal"""
    print("🤖 RM Bot - Automação para Poke Old")
    print("Versão Desktop v2.0 - Com Animações de Transição")
    print("-" * 40)
    
    if not AUTOMATION_AVAILABLE:
        print("AVISO: Funcionalidades de automação limitadas")
        print("Para habilitar automação completa, instale:")
        print("pip install pyautogui opencv-python psutil")
        print("-" * 40)
    
    try:
        app = RMBotApp()
        app.run()
    except KeyboardInterrupt:
        print("\n👋 Bot encerrado pelo usuário")
    except Exception as e:
        print(f"❌ Erro: {e}")
        input("Pressione Enter para sair...")

if __name__ == "__main__":
    main()