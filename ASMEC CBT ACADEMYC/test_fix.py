"""
ASMET - Versión Estable y Funcional
Solución al error gráfico de Kivy en Windows
"""

import sqlite3
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView

# FIX CRÍTICO: Configurar antes de cualquier import gráfico
import os
os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'
os.environ['KIVY_WINDOW'] = 'sdl2'
os.environ['KIVY_TEXT'] = 'sdl2'

Window.size = (360, 600)

class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect('asmet_fixed.db')
        self.init_db()
    
    def init_db(self):
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
        print("Base de datos lista")
    
    def register(self, username, password):
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                'INSERT INTO users (username, password) VALUES (?, ?)',
                (username, password)
            )
            self.conn.commit()
            return True, "Registro exitoso"
        except:
            return False, "Usuario ya existe"
    
    def login(self, username, password):
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT id, username, level, points FROM users WHERE username=? AND password=?',
            (username, password)
        )
        return cursor.fetchone()

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        layout = BoxLayout(orientation='vertical', padding=50, spacing=20)
        
        # Título
        title = Label(
            text='ASMET MATEMÁTICAS',
            font_size=32,
            bold=True,
            color=(0.1, 0.4, 0.8, 1)
        )
        
        # Campos de entrada
        self.username_input = TextInput(
            hint_text='Usuario',
            size_hint_y=None,
            height=50,
            multiline=False
        )
        
        self.password_input = TextInput(
            hint_text='Contraseña',
            password=True,
            size_hint_y=None,
            height=50,
            multiline=False
        )
        
        # Botones
        btn_layout = BoxLayout(spacing=10, size_hint_y=None, height=50)
        
        login_btn = Button(
            text='Iniciar Sesión',
            background_color=(0.2, 0.6, 0.9, 1)
        )
        login_btn.bind(on_press=self.do_login)
        
        register_btn = Button(
            text='Registrarse',
            background_color=(0.4, 0.8, 0.4, 1)
        )
        register_btn.bind(on_press=self.do_register)
        
        btn_layout.add_widget(login_btn)
        btn_layout.add_widget(register_btn)
        
        # Agregar todo al layout
        layout.add_widget(Label(text=''))  # Espacio
        layout.add_widget(title)
        layout.add_widget(Label(text=''))  # Espacio
        layout.add_widget(self.username_input)
        layout.add_widget(self.password_input)
        layout.add_widget(btn_layout)
        layout.add_widget(Label(text=''))  # Espacio
        
        self.add_widget(layout)
    
    def do_login(self, instance):
        user = self.manager.app.db.login(
            self.username_input.text,
            self.password_input.text
        )
        
        if user:
            self.manager.app.user = {
                'id': user[0],
                'username': user[1],
                'level': user[2],
                'points': user[3]
            }
            self.manager.current = 'dashboard'
        else:
            print("Login fallido")
    
    def do_register(self, instance):
        success, msg = self.manager.app.db.register(
            self.username_input.text,
            self.password_input.text
        )
        print(msg)

class DashboardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        main = BoxLayout(orientation='vertical')
        
        # Header
        header = BoxLayout(size_hint_y=0.15, padding=10)
        self.welcome_label = Label(
            text='Bienvenido',
            font_size=24,
            bold=True
        )
        header.add_widget(self.welcome_label)
        
        # Contenido
        scroll = ScrollView()
        content = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=10,
            padding=20
        )
        content.bind(minimum_height=content.setter('height'))
        
        # Opciones
        options = [
            ('🧮', 'Aritmética', 'Sumas, restas, multiplicaciones'),
            ('📐', 'Geometría', 'Formas y medidas'),
            ('📊', 'Álgebra', 'Ecuaciones básicas'),
            ('🏆', 'Desafíos', 'Problemas avanzados'),
            ('📈', 'Progreso', 'Estadísticas de aprendizaje'),
            ('⚙️', 'Configuración', 'Ajustes de la app')
        ]
        
        for icon, title, desc in options:
            option = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=80,
                spacing=15
            )
            
            option.add_widget(Label(
                text=icon,
                font_size=30
            ))
            
            text_box = BoxLayout(orientation='vertical')
            text_box.add_widget(Label(
                text=title,
                font_size=18,
                bold=True,
                halign='left'
            ))
            text_box.add_widget(Label(
                text=desc,
                font_size=14,
                color=(0.5, 0.5, 0.5, 1),
                halign='left'
            ))
            
            option.add_widget(text_box)
            content.add_widget(option)
        
        scroll.add_widget(content)
        
        main.add_widget(header)
        main.add_widget(scroll)
        self.add_widget(main)
    
    def on_pre_enter(self):
        if self.manager.app.user:
            self.welcome_label.text = f"Hola, {self.manager.app.user['username']}"

class AsmetApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DatabaseManager()
        self.user = None
    
    def build(self):
        sm = ScreenManager()
        sm.app = self  # Para acceso desde pantallas
        
        # Registrar pantallas
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(DashboardScreen(name='dashboard'))
        
        return sm

# EJECUCIÓN PRINCIPAL
if __name__ == '__main__':
    AsmetApp().run()