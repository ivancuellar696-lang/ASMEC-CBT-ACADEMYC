"""
ASMET CBT ACADEMYC - Versión Simplificada y Estable
"""

import sqlite3
from datetime import datetime

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.modalview import ModalView
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.properties import ListProperty

# Configuración
Window.size = (360, 640)

# Base de datos simple
class DatabaseManager:
    def __init__(self, db_path='asmet_simple.db'):
        self.db_path = db_path
        self.conn = None
        
    def initialize_database(self):
        """Inicializar base de datos simple"""
        self.conn = sqlite3.connect(self.db_path)
        cursor = self.conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT,
                level INTEGER DEFAULT 1,
                points INTEGER DEFAULT 0
            )
        ''')
        
        self.conn.commit()
        print("Base de datos simple inicializada")
        
    def register_user(self, username, password):
        """Registrar usuario simple"""
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO users (username, password) VALUES (?, ?)',
                (username, password)
            )
            self.conn.commit()
            return True, "Usuario registrado"
        except:
            return False, "Usuario ya existe"
            
    def authenticate_user(self, username, password):
        """Autenticar usuario simple"""
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT id, username, level, points FROM users WHERE username = ? AND password = ?',
            (username, password)
        )
        user = cursor.fetchone()
        return user

class SimpleScreen(Screen):
    """Pantalla simple sin canvas complejo"""
    background_color = ListProperty([0.97, 0.97, 0.97, 1])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        
    def on_pre_enter(self):
        """Configurar fondo al entrar"""
        with self.canvas.before:
            Color(*self.background_color)
            Rectangle(pos=self.pos, size=self.size)

class LoginScreen(SimpleScreen):
    """Pantalla de login simple"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = [0.13, 0.59, 0.95, 1]
        
        layout = FloatLayout()
        
        # Logo
        logo = Label(
            text='∑ ASMET',
            font_size=48,
            pos_hint={'center_x': 0.5, 'center_y': 0.8},
            color=[1, 1, 1, 1]
        )
        
        # Formulario
        form_box = BoxLayout(
            orientation='vertical',
            size_hint=(0.8, 0.4),
            pos_hint={'center_x': 0.5, 'center_y': 0.4},
            spacing=20,
            padding=30
        )
        
        self.username = TextInput(
            hint_text='Usuario',
            size_hint_y=None,
            height=50,
            multiline=False
        )
        
        self.password = TextInput(
            hint_text='Contraseña',
            password=True,
            size_hint_y=None,
            height=50,
            multiline=False
        )
        
        login_btn = Button(
            text='Iniciar Sesión',
            size_hint_y=None,
            height=50,
            background_color=[0.2, 0.7, 1, 1],
            color=[1, 1, 1, 1]
        )
        login_btn.bind(on_press=self.do_login)
        
        register_btn = Button(
            text='Registrarse',
            size_hint_y=None,
            height=50,
            background_color=[0.4, 0.8, 0.4, 1],
            color=[1, 1, 1, 1]
        )
        register_btn.bind(on_press=self.do_register)
        
        form_box.add_widget(Label(text='', size_hint_y=0.2))
        form_box.add_widget(self.username)
        form_box.add_widget(self.password)
        form_box.add_widget(login_btn)
        form_box.add_widget(register_btn)
        
        layout.add_widget(logo)
        layout.add_widget(form_box)
        self.add_widget(layout)
    
    def do_login(self, instance):
        """Procesar login"""
        username = self.username.text.strip()
        password = self.password.text
        
        if not username or not password:
            self.show_message('Completa todos los campos', 'warning')
            return
        
        user = self.app.db.authenticate_user(username, password)
        
        if user:
            self.app.current_user = {
                'id': user[0],
                'username': user[1],
                'level': user[2],
                'points': user[3]
            }
            self.manager.current = 'dashboard'
            self.show_message(f'¡Bienvenido {user[1]}!', 'success')
        else:
            self.show_message('Credenciales incorrectas', 'error')
    
    def do_register(self, instance):
        """Procesar registro"""
        username = self.username.text.strip()
        password = self.password.text
        
        if not username or not password:
            self.show_message('Completa todos los campos', 'warning')
            return
        
        success, message = self.app.db.register_user(username, password)
        
        if success:
            self.show_message('¡Cuenta creada! Ahora inicia sesión', 'success')
        else:
            self.show_message(message, 'error')
    
    def show_message(self, message, msg_type):
        """Mostrar mensaje simple"""
        popup = ModalView(size_hint=(0.7, 0.2))
        content = BoxLayout(orientation='vertical', padding=10)
        
        colors = {
            'success': [0.2, 0.8, 0.2, 1],
            'error': [0.9, 0.2, 0.2, 1],
            'warning': [0.9, 0.7, 0.2, 1]
        }
        
        content.add_widget(Label(
            text=message,
            font_size=16,
            color=[1, 1, 1, 1]
        ))
        
        close_btn = Button(
            text='OK',
            size_hint_y=None,
            height=40,
            background_color=colors.get(msg_type, [0.2, 0.6, 0.9, 1])
        )
        close_btn.bind(on_press=lambda x: popup.dismiss())
        content.add_widget(close_btn)
        
        popup.add_widget(content)
        popup.open()

class DashboardScreen(SimpleScreen):
    """Dashboard simple"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        layout = BoxLayout(orientation='vertical')
        
        # Header
        header = BoxLayout(
            orientation='horizontal',
            size_hint_y=0.15,
            padding=20,
            spacing=20
        )
        
        user_info = BoxLayout(orientation='vertical')
        self.welcome_label = Label(
            text='Bienvenido',
            font_size=20,
            bold=True,
            halign='left'
        )
        self.level_label = Label(
            text='Nivel: 1',
            font_size=14,
            color=[0.5, 0.5, 0.5, 1]
        )
        
        user_info.add_widget(self.welcome_label)
        user_info.add_widget(self.level_label)
        
        points_box = BoxLayout(orientation='vertical')
        self.points_label = Label(
            text='0 pts',
            font_size=18,
            color=[0.2, 0.6, 0.9, 1]
        )
        points_box.add_widget(self.points_label)
        
        header.add_widget(user_info)
        header.add_widget(points_box)
        
        # Contenido
        scroll = ScrollView()
        content = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=15,
            padding=20
        )
        content.bind(minimum_height=content.setter('height'))
        
        # Secciones
        sections = [
            ('🧮', 'Aritmética Básica', 'Operaciones fundamentales'),
            ('📐', 'Geometría', 'Formas y medidas'),
            ('📊', 'Álgebra', 'Ecuaciones y variables'),
            ('🎯', 'Desafíos', 'Problemas para resolver'),
            ('📈