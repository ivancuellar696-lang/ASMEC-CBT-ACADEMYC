"""
ASMET CBT ACADEMYC - Aplicación Educativa Completa
Versión: 3.0.0 Estable
Autor: Sistema ASMET
"""

# CONFIGURACIÓN CRÍTICA PARA WINDOWS - DEBE IR PRIMERO
import os
os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'
os.environ['KIVY_WINDOW'] = 'sdl2'
os.environ['KIVY_TEXT'] = 'sdl2'
os.environ['KIVY_VIDEO'] = 'ffpyplayer'

import json
import random
import math
import sqlite3
import hashlib
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# Kivy imports
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.properties import StringProperty, NumericProperty, ListProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.modalview import ModalView
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.animation import Animation

# Configuración de ventana
Window.size = (360, 640)
Window.minimum_width, Window.minimum_height = 360, 640

# ============================================
# BASE DE DATOS - VERSIÓN CORREGIDA
# ============================================

class DatabaseManager:
    """Gestor de base de datos SQLite - Versión Estable"""
    
    def __init__(self, db_path='asmet_data.db'):
        self.db_path = db_path
        self.conn = None
        self.connect()
    
    def connect(self):
        """Conectar a la base de datos"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.initialize_database()
    
    def initialize_database(self):
        """Inicializar base de datos - MÉTODO CORREGIDO"""
        cursor = self.conn.cursor()
        
        # Tabla de usuarios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                level INTEGER DEFAULT 1,
                total_points INTEGER DEFAULT 0,
                coins INTEGER DEFAULT 0,
                overall_progress REAL DEFAULT 0.0,
                created_at TEXT NOT NULL,
                last_login TEXT
            )
        ''')
        
        # Tabla de progreso por materia
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subject_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                subject TEXT NOT NULL,
                progress REAL DEFAULT 0.0,
                last_updated TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id),
                UNIQUE(user_id, subject)
            )
        ''')
        
        # Tabla de logros
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                icon TEXT,
                points INTEGER DEFAULT 0,
                unlocked BOOLEAN DEFAULT 0,
                unlocked_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Tabla de ejercicios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS exercises (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                exercise_type TEXT NOT NULL,
                correct BOOLEAN,
                points_earned INTEGER,
                time_spent INTEGER,
                timestamp TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        self.conn.commit()
        print("✅ Base de datos inicializada correctamente")
    
    def register_user(self, username: str, password: str, email: str = "") -> Tuple[bool, str]:
        """Registrar nuevo usuario"""
        try:
            cursor = self.conn.cursor()
            
            # Verificar si usuario existe
            cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
            if cursor.fetchone():
                return False, "El usuario ya existe"
            
            # Generar hash de contraseña
            salt = os.urandom(16).hex()
            password_hash = hashlib.pbkdf2_hmac(
                'sha256', 
                password.encode(), 
                salt.encode(), 
                100000
            ).hex()
            
            # Insertar usuario
            created_at = datetime.now().isoformat()
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, salt, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, email, password_hash, salt, created_at))
            
            user_id = cursor.lastrowid
            
            # Inicializar materias
            subjects = ['Aritmética', 'Álgebra', 'Geometría', 'Cálculo', 'Estadística']
            for subject in subjects:
                cursor.execute('''
                    INSERT INTO subject_progress (user_id, subject, last_updated)
                    VALUES (?, ?, ?)
                ''', (user_id, subject, created_at))
            
            self.conn.commit()
            return True, "Usuario registrado exitosamente"
            
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Autenticar usuario"""
        try:
            cursor = self.conn.cursor()
            
            # Buscar usuario
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            user = cursor.fetchone()
            
            if not user:
                return None
            
            # Verificar contraseña
            salt = user['salt']
            stored_hash = user['password_hash']
            input_hash = hashlib.pbkdf2_hmac(
                'sha256', 
                password.encode(), 
                salt.encode(), 
                100000
            ).hex()
            
            if stored_hash != input_hash:
                return None
            
            # Actualizar último login
            cursor.execute('UPDATE users SET last_login = ? WHERE id = ?',
                          (datetime.now().isoformat(), user['id']))
            self.conn.commit()
            
            return dict(user)
            
        except Exception as e:
            print(f"Error en autenticación: {e}")
            return None
    
    def get_user_stats(self, user_id: int) -> Dict:
        """Obtener estadísticas del usuario"""
        cursor = self.conn.cursor()
        
        # Ejercicios completados
        cursor.execute('SELECT COUNT(*) FROM exercises WHERE user_id = ?', (user_id,))
        exercises_done = cursor.fetchone()[0] or 0
        
        # Precisión
        cursor.execute('SELECT COUNT(*), SUM(CASE WHEN correct = 1 THEN 1 ELSE 0 END) FROM exercises WHERE user_id = ?', (user_id,))
        total, correct = cursor.fetchone()
        accuracy = (correct / total * 100) if total > 0 else 0
        
        # Puntos totales
        cursor.execute('SELECT total_points FROM users WHERE id = ?', (user_id,))
        total_points = cursor.fetchone()[0] or 0
        
        return {
            'exercises_done': exercises_done,
            'accuracy': round(accuracy, 1),
            'total_points': total_points,
            'level': 1 + (total_points // 100)  # 1 nivel cada 100 puntos
        }
    
    def save_exercise_result(self, user_id: int, exercise_type: str, 
                           correct: bool, points: int, time_spent: int):
        """Guardar resultado de ejercicio"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            INSERT INTO exercises (user_id, exercise_type, correct, points_earned, time_spent, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, exercise_type, correct, points, time_spent, datetime.now().isoformat()))
        
        # Actualizar puntos del usuario
        if correct:
            cursor.execute('UPDATE users SET total_points = total_points + ? WHERE id = ?',
                          (points, user_id))
        
        self.conn.commit()
    
    def close(self):
        """Cerrar conexión"""
        if self.conn:
            self.conn.close()

# ============================================
# SISTEMA DE GAMIFICACIÓN
# ============================================

class Achievement:
    """Logro del sistema"""
    def __init__(self, name: str, description: str, icon: str, points: int):
        self.name = name
        self.description = description
        self.icon = icon
        self.points = points
        self.unlocked = False
        self.unlocked_at = None

class GamificationSystem:
    """Sistema de gamificación simplificado"""
    
    def __init__(self, user_id: int, db: DatabaseManager):
        self.user_id = user_id
        self.db = db
        self.achievements = self.load_achievements()
    
    def load_achievements(self) -> List[Achievement]:
        """Cargar logros disponibles"""
        return [
            Achievement("Primer Paso", "Completa tu primer ejercicio", "👣", 10),
            Achievement("Aprendiz", "Completa 10 ejercicios", "📚", 50),
            Achievement("Precisión", "Responde 5 ejercidos seguidos correctamente", "🎯", 30),
            Achievement("Velocidad", "Completa un ejercicio en menos de 30 segundos", "⚡", 40),
            Achievement("Maestro", "Alcanza el nivel 5", "👨‍🏫", 100)
        ]
    
    def record_exercise_completion(self, exercise_type: str, correct: bool, 
                                 points: int, time_spent: int):
        """Registrar ejercicio completado"""
        # Guardar en base de datos
        self.db.save_exercise_result(self.user_id, exercise_type, correct, points, time_spent)
        
        # Verificar logros
        self.check_achievements()
    
    def check_achievements(self):
        """Verificar y desbloquear logros"""
        stats = self.db.get_user_stats(self.user_id)
        
        # Verificar cada logro
        for achievement in self.achievements:
            if not achievement.unlocked:
                unlocked = False
                
                if achievement.name == "Primer Paso" and stats['exercises_done'] >= 1:
                    unlocked = True
                elif achievement.name == "Aprendiz" and stats['exercises_done'] >= 10:
                    unlocked = True
                elif achievement.name == "Maestro" and stats['level'] >= 5:
                    unlocked = True
                
                if unlocked:
                    achievement.unlocked = True
                    achievement.unlocked_at = datetime.now()
                    print(f"🎉 Logro desbloqueado: {achievement.name}")
    
    def get_recent_achievements(self, limit: int = 3) -> List[Achievement]:
        """Obtener logros recientes"""
        return [a for a in self.achievements if a.unlocked][-limit:]
    
    def get_weekly_ranking(self, limit: int = 5) -> List[Tuple[str, int]]:
        """Obtener ranking semanal (simulado)"""
        # En una versión real, esto vendría de la base de datos
        return [
            ("Juan", 1250),
            ("María", 1100),
            ("Carlos", 980),
            ("Ana", 850),
            ("Luis", 720)
        ]

class Leaderboard:
    """Sistema de ranking - VERSIÓN CORREGIDA"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def get_rankings(self, limit: int = 10) -> List[Dict]:
        """Obtener ranking general"""
        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT username, total_points, level 
            FROM users 
            ORDER BY total_points DESC 
            LIMIT ?
        ''', (limit,))
        
        rankings = []
        for i, row in enumerate(cursor.fetchall(), 1):
            rankings.append({
                'position': i,
                'username': row['username'],
                'points': row['total_points'],
                'level': row['level']
            })
        
        return rankings

# ============================================
# COMPONENTES DE INTERFAZ
# ============================================

class RoundedButton(Button):
    """Botón con bordes redondeados"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = [0.2, 0.6, 0.9, 1]
        self.color = [1, 1, 1, 1]
        self.font_size = 16
        self.size_hint_y = None
        self.height = 50
    
    def on_press(self):
        anim = Animation(opacity=0.7, duration=0.1)
        anim.start(self)
    
    def on_release(self):
        anim = Animation(opacity=1.0, duration=0.2)
        anim.start(self)

class Card(BoxLayout):
    """Tarjeta con sombra y bordes redondeados"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 15
        self.spacing = 10
        self.size_hint_y = None
        self.background_color = [1, 1, 1, 1]

class EnhancedTextInput(TextInput):
    """Campo de texto mejorado"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = [1, 1, 1, 1]
        self.foreground_color = [0.2, 0.2, 0.2, 1]
        self.padding = [15, 10]
        self.size_hint_y = None
        self.height = 50
        self.multiline = False

# ============================================
# PANTALLAS DE LA APLICACIÓN
# ============================================

class BaseScreen(Screen):
    """Pantalla base sin canvas problemático"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()

class LoginScreen(BaseScreen):
    """Pantalla de login y registro"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Layout principal con fondo
        main_layout = FloatLayout()
        
        # Fondo degradado
        with main_layout.canvas.before:
            Color(0.13, 0.59, 0.95, 1)
            Rectangle(pos=main_layout.pos, size=main_layout.size)
        
        # Logo
        logo = Label(
            text='∑ ASMET',
            font_size=48,
            bold=True,
            pos_hint={'center_x': 0.5, 'center_y': 0.8},
            color=[1, 1, 1, 1]
        )
        
        # Tarjeta de formulario
        form_card = BoxLayout(
            orientation='vertical',
            size_hint=(0.85, 0.5),
            pos_hint={'center_x': 0.5, 'center_y': 0.4},
            spacing=20,
            padding=30
        )
        
        # Tabs
        tabs = BoxLayout(size_hint_y=0.15, spacing=5)
        self.login_tab = Button(text='INICIAR SESIÓN', background_color=[0.2, 0.7, 1, 1])
        self.register_tab = Button(text='REGISTRARSE', background_color=[0.8, 0.8, 0.8, 1])
        self.login_tab.bind(on_press=self.show_login_form)
        self.register_tab.bind(on_press=self.show_register_form)
        tabs.add_widget(self.login_tab)
        tabs.add_widget(self.register_tab)
        
        # Formulario login
        self.login_form = BoxLayout(orientation='vertical', spacing=15)
        self.username_input = EnhancedTextInput(hint_text='Usuario')
        self.password_input = EnhancedTextInput(hint_text='Contraseña', password=True)
        login_btn = RoundedButton(text='Iniciar Sesión')
        login_btn.bind(on_press=self.do_login)
        
        self.login_form.add_widget(self.username_input)
        self.login_form.add_widget(self.password_input)
        self.login_form.add_widget(login_btn)
        
        # Formulario registro (oculto)
        self.register_form = BoxLayout(orientation='vertical', spacing=15)
        self.reg_username = EnhancedTextInput(hint_text='Nuevo usuario')
        self.reg_email = EnhancedTextInput(hint_text='Email (opcional)')
        self.reg_password = EnhancedTextInput(hint_text='Contraseña', password=True)
        self.reg_confirm = EnhancedTextInput(hint_text='Confirmar contraseña', password=True)
        register_btn = RoundedButton(text='Crear Cuenta')
        register_btn.bind(on_press=self.do_register)
        
        self.register_form.add_widget(self.reg_username)
        self.register_form.add_widget(self.reg_email)
        self.register_form.add_widget(self.reg_password)
        self.register_form.add_widget(self.reg_confirm)
        self.register_form.add_widget(register_btn)
        self.register_form.opacity = 0
        
        # Ensamblar
        form_card.add_widget(tabs)
        form_card.add_widget(self.login_form)
        form_card.add_widget(self.register_form)
        
        main_layout.add_widget(logo)
        main_layout.add_widget(form_card)
        self.add_widget(main_layout)
    
    def show_login_form(self, instance):
        """Mostrar formulario de login"""
        self.login_tab.background_color = [0.2, 0.7, 1, 1]
        self.register_tab.background_color = [0.8, 0.8, 0.8, 1]
        Animation(opacity=1, duration=0.3).start(self.login_form)
        Animation(opacity=0, duration=0.3).start(self.register_form)
    
    def show_register_form(self, instance):
        """Mostrar formulario de registro"""
        self.register_tab.background_color = [0.2, 0.7, 1, 1]
        self.login_tab.background_color = [0.8, 0.8, 0.8, 1]
        Animation(opacity=1, duration=0.3).start(self.register_form)
        Animation(opacity=0, duration=0.3).start(self.login_form)
    
    def do_login(self, instance):
        """Procesar login"""
        username = self.username_input.text.strip()
        password = self.password_input.text
        
        if not username or not password:
            self.show_message('Completa todos los campos', 'warning')
            return
        
        user_data = self.app.db.authenticate_user(username, password)
        
        if user_data:
            self.app.current_user = user_data
            self.app.gamification = GamificationSystem(user_data['id'], self.app.db)
            self.app.leaderboard = Leaderboard(self.app.db)
            
            self.manager.current = 'dashboard'
            self.show_message(f'¡Bienvenido, {user_data["username"]}!', 'success')
        else:
            self.show_message('Usuario o contraseña incorrectos', 'error')
    
    def do_register(self, instance):
        """Procesar registro"""
        username = self.reg_username.text.strip()
        email = self.reg_email.text.strip()
        password = self.reg_password.text
        confirm = self.reg_confirm.text
        
        if not username or not password:
            self.show_message('Usuario y contraseña son obligatorios', 'warning')
            return
        
        if password != confirm:
            self.show_message('Las contraseñas no coinciden', 'error')
            return
        
        success, message = self.app.db.register_user(username, password, email)
        
        if success:
            self.show_message('¡Cuenta creada! Ahora inicia sesión', 'success')
            self.show_login_form(None)
            self.username_input.text = username
        else:
            self.show_message(message, 'error')
    
    def show_message(self, text: str, msg_type: str = 'info'):
        """Mostrar mensaje emergente"""
        colors = {
            'success': [0.2, 0.8, 0.4, 1],
            'error': [0.9, 0.3, 0.3, 1],
            'warning': [0.96, 0.77, 0.23, 1],
            'info': [0.2, 0.6, 0.9, 1]
        }
        
        popup = ModalView(size_hint=(0.8, 0.2), background_color=[0,0,0,0])
        content = BoxLayout(orientation='vertical', padding=10)
        
        with content.canvas.before:
            Color(*colors.get(msg_type, [0.2, 0.6, 0.9, 1]))
            RoundedRectangle(pos=content.pos, size=content.size, radius=[10])
        
        content.add_widget(Label(
            text=text, 
            font_size=16, 
            color=[1,1,1,1],
            halign='center'
        ))
        
        ok_btn = Button(
            text='OK', 
            size_hint_y=None, 
            height=40,
            background_color=[1,1,1,0.3]
        )
        ok_btn.bind(on_press=lambda x: popup.dismiss())
        content.add_widget(ok_btn)
        
        popup.add_widget(content)
        popup.open()

class DashboardScreen(BaseScreen):
    """Pantalla principal del dashboard"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Layout principal
        main_layout = BoxLayout(orientation='vertical')
        
        # Header
        self.header = self.create_header()
        
        # Contenido scrollable
        scroll = ScrollView(do_scroll_x=False)
        self.content = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=15,
            padding=[20, 20, 20, 100]
        )
        self.content.bind(minimum_height=self.content.setter('height'))
        
        scroll.add_widget(self.content)
        main_layout.add_widget(self.header)
        main_layout.add_widget(scroll)
        self.add_widget(main_layout)
    
    def create_header(self):
        """Crear encabezado del dashboard"""
        header = BoxLayout(
            orientation='horizontal',
            size_hint_y=0.12,
            padding=[20, 10],
            spacing=15
        )
        
        # Info usuario
        user_box = BoxLayout(orientation='vertical')
        self.welcome_label = Label(
            text='Bienvenido',
            font_size=20,
            bold=True,
            halign='left'
        )
        self.level_label = Label(
            text='Nivel: 1',
            font_size=14,
            color=[0.6, 0.6, 0.6, 1],
            halign='left'
        )
        user_box.add_widget(self.welcome_label)
        user_box.add_widget(self.level_label)
        
        # Puntos
        points_box = BoxLayout(orientation='vertical')
        self.points_label = Label(
            text='0 pts',
            font_size=18,
            color=[0.2, 0.6, 0.9, 1],
            halign='right'
        )
        points_box.add_widget(self.points_label)
        
        header.add_widget(user_box)
        header.add_widget(points_box)
        return header
    
    def on_pre_enter(self):
        """Actualizar contenido al entrar"""
        super().on_pre_enter()
        self.update_content()
    
    def update_content(self):
        """Actualizar contenido del dashboard"""
        self.content.clear_widgets()
        
        if self.app.current_user:
            stats = self.app.db.get_user_stats(self.app.current_user['id'])
            
            # Actualizar header
            self.welcome_label.text = f"Hola, {self.app.current_user['username']}"
            self.level_label.text = f"Nivel: {stats['level']}"
            self.points_label.text = f"{stats['total_points']} pts"
            
            # 1. Progreso
            self.add_progress_card(stats)
            
            # 2. Ejercicios rápidos
            self.add_quick_exercises()
            
            # 3. Logros
            self.add_achievements_card()
            
            # 4. Ranking
            self.add_ranking_card()
        else:
            self.content.add_widget(Label(
                text="No hay usuario activo",
                font_size=18,
                color=[0.5, 0.5, 0.5, 1]
            ))
    
    def add_progress_card(self, stats: Dict):
        """Agregar tarjeta de progreso"""
        card = Card(height=150)
        
        # Título
        title = Label(
            text='📊 Tu Progreso',
            font_size=18,
            bold=True,
            halign='left'
        )
        
        # Estadísticas
        stats_grid = GridLayout(cols=2, spacing=10, size_hint_y=0.6)
        
        stat_items = [
            ('Ejercicios', f"{stats['exercises_done']}"),
            ('Precisión', f"{stats['accuracy']}%"),
            ('Nivel', f"{stats['level']}"),
            ('Puntos', f"{stats['total_points']}")
        ]
        
        for label, value in stat_items:
            stat_box = BoxLayout(orientation='vertical')
            stat_box.add_widget(Label(
                text=label,
                font_size=12,
                color=[0.5, 0.5, 0.5, 1]
            ))
            stat_box.add_widget(Label(
                text=value,
                font_size=16,
                bold=True
            ))
            stats_grid.add_widget(stat_box)
        
        card.add_widget(title)
        card.add_widget(stats_grid)
        self.content.add_widget(card)
    
    def add_quick_exercises(self):
        """Agregar ejercicios rápidos"""
        card = Card(height=180)
        
        title = Label(
            text='⚡ Ejercicios Rápidos',
            font_size=18,
            bold=True,
            halign='left'
        )
        
        exercises_grid = GridLayout(cols=3, spacing=10, size_hint_y=0.7)
        
        exercises = [
            ('🧮', 'Sumas', 'arithmetic'),
            ('➖', 'Restas', 'subtraction'),
            ('✖️', 'Multiplicación', 'multiplication'),
            ('➗', 'División', 'division'),
            ('📐', 'Geometría', 'geometry'),
            ('📈', 'Problemas', 'problems')
        ]
        
        for icon, name, ex_type in exercises:
            ex_card = BoxLayout(
                orientation='vertical',
                padding=5
            )
            ex_card.add_widget(Label(text=icon, font_size=24))
            ex_card.add_widget(Label(text=name, font_size=10))
            
            # Botón invisible para capturar clicks
            btn = Button(background_color=[0,0,0,0])
            btn.bind(on_press=lambda x, t=ex_type: self.start_exercise(t))
            ex_card.add_widget(btn)
            
            exercises_grid.add_widget(ex_card)
        
        card.add_widget(title)
        card.add_widget(exercises_grid)
        self.content.add_widget(card)
    
    def add_achievements_card(self):
        """Agregar tarjeta de logros"""
        if not hasattr(self.app, 'gamification'):
            return
        
        achievements = self.app.gamification.get_recent_achievements(3)
        if not achievements:
            return
        
        card = Card(height=120)
        
        title = Label(
            text='🏆 Logros Recientes',
            font_size=18,
            bold=True,
            halign='left'
        )
        
        ach_box = BoxLayout(spacing=10)
        
        for ach in achievements:
            ach_item = BoxLayout(orientation='vertical')
            ach_item.add_widget(Label(text=ach.icon, font_size=24))
            ach_item.add_widget(Label(
                text=ach.name[:10],
                font_size=10,
                halign='center'
            ))
            ach_box.add_widget(ach_item)
        
        card.add_widget(title)
        card.add_widget(ach_box)
        self.content.add_widget(card)
    
    def add_ranking_card(self):
        """Agregar tarjeta de ranking"""
        if not hasattr(self.app, 'leaderboard'):
            return
        
        rankings = self.app.leaderboard.get_rankings(5)
        
        card = Card(height=180)
        
        title = Label(
            text='🏅 Ranking Top 5',
            font_size=18,
            bold=True,
            halign='left'
        )
        
        # Lista de rankings
        ranking_list = BoxLayout(orientation='vertical', spacing=5)
        
        for rank in rankings:
            rank_item = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=30
            )
            
            # Posición
            pos_color = [0.96, 0.77, 0.23, 1] if rank['position'] <= 3 else [0.6, 0.6, 0.6, 1]
            pos_label = Label(
                text=f"{rank['position']}°",
                font_size=14,
                bold=True,
                color=pos_color,
                size_hint_x=0.2
            )
            
            # Nombre
            name_label = Label(
                text=rank['username'][:12],
                font_size=14,
                halign='left',
                size_hint_x=0.5
            )
            
            # Puntos
            points_label = Label(
                text=str(rank['points']),
                font_size=14,
                color=[0.2, 0.6, 0.9, 1],
                size_hint_x=0.3
            )
            
            rank_item.add_widget(pos_label)
            rank_item.add_widget(name_label)
            rank_item.add_widget(points_label)
            ranking_list.add_widget(rank_item)
        
        card.add_widget(title)
        card.add_widget(ranking_list)
        self.content.add_widget(card)
    
    def start_exercise(self, exercise_type: str):
        """Iniciar ejercicio"""
        self.app.current_exercise = exercise_type
        self.manager.current = 'exercise'

class ExerciseScreen(BaseScreen):
    """Pantalla de ejercicios"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.current_problem = None
        self.start_time = None
        
        # Layout principal
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        # Header
        header = BoxLayout(size_hint_y=0.1)
        back_btn = Button(text='← Volver', size_hint_x=0.3)
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'dashboard'))
        self.problem_label = Label(
            text='Ejercicio',
            font_size=20,
            bold=True
        )
        header.add_widget(back_btn)
        header.add_widget(self.problem_label)
        
        # Área del problema
        self.problem_area = BoxLayout(
            orientation='vertical',
            size_hint_y=0.4
        )
        
        # Input de respuesta
        self.answer_input = EnhancedTextInput(
            hint_text='Escribe tu respuesta aquí...',
            font_size=24,
            halign='center'
        )
        
        # Botones
        btn_layout = BoxLayout(size_hint_y=0.2, spacing=10)
        check_btn = RoundedButton(text='Verificar')
        check_btn.bind(on_press=self.check_answer)
        
        hint_btn = RoundedButton(text='Pista', background_color=[0.96, 0.77, 0.23, 1])
        hint_btn.bind(on_press=self.show_hint)
        
        next_btn = RoundedButton(text='Siguiente', background_color=[0.4, 0.8, 0.4, 1])
        next_btn.bind(on_press=self.next_problem)
        
        btn_layout.add_widget(check_btn)
        btn_layout.add_widget(hint_btn)
        btn_layout.add_widget(next_btn)
        
        # Resultado
        self.result_label = Label(
            text='',
            font_size=18,
            color=[0.5, 0.5, 0.5, 1]
        )
        
        # Ensamblar
        main_layout.add_widget(header)
        main_layout.add_widget(self.problem_area)
        main_layout.add_widget(self.answer_input)
        main_layout.add_widget(btn_layout)
        main_layout.add_widget(self.result_label)
        
        self.add_widget(main_layout)
    
    def on_pre_enter(self):
        """Generar nuevo problema al entrar"""
        super().on_pre_enter()
        self.generate_problem()
    
    def generate_problem(self):
        """Generar un problema matemático"""
        ex_type = getattr(self.app, 'current_exercise', 'arithmetic')
        
        if ex_type == 'arithmetic':
            # Suma
            a, b = random.randint(1, 50), random.randint(1, 50)
            self.current_problem = {
                'text': f'{a} + {b} = ?',
                'answer': a + b,
                'points': 10
            }
        elif ex_type == 'subtraction':
            # Resta
            a, b = random.randint(20, 100), random.randint(1, 20)
            self.current_problem = {
                'text': f'{a} - {b} = ?',
                'answer': a - b,
                'points': 10
            }
        elif ex_type == 'multiplication':
            # Multiplicación
            a, b = random.randint(2, 12), random.randint(2, 12)
            self.current_problem = {
                'text': f'{a} × {b} = ?',
                'answer': a * b,
                'points': 15
            }
        elif ex_type == 'division':
            # División
            b = random.randint(2, 10)
            a = b * random.randint(2, 10)
            self.current_problem = {
                'text': f'{a} ÷ {b} = ?',
                'answer': a // b,
                'points': 15
            }
        else:
            # Problema genérico
            a, b = random.randint(1, 100), random.randint(1, 100)
            self.current_problem = {
                'text': f'{a} + {b} = ?',
                'answer': a + b,
                'points': 10
            }
        
        # Actualizar interfaz
        self.problem_label.text = f"Ejercicio: {ex_type.capitalize()}"
        self.problem_area.clear_widgets()
        self.problem_area.add_widget(Label(
            text=self.current_problem['text'],
            font_size=48,
            bold=True
        ))
        
        self.answer_input.text = ''
        self.result_label.text = ''
        self.start_time = datetime.now()
    
    def check_answer(self, instance):
        """Verificar respuesta"""
        if not self.current_problem:
            return
        
        user_answer = self.answer_input.text.strip()
        
        if not user_answer:
            self.result_label.text = 'Escribe una respuesta primero'
            self.result_label.color = [0.96, 0.77, 0.23, 1]
            return
        
        try:
            user_num = float(user_answer)
            correct = abs(user_num - self.current_problem['answer']) < 0.001
            
            # Calcular tiempo
            time_spent = (datetime.now() - self.start_time).seconds
            
            if correct:
                self.result_label.text = f'✅ ¡Correcto! +{self.current_problem["points"]} puntos'
                self.result_label.color = [0.2, 0.8, 0.4, 1]
                
                # Registrar en gamificación
                if self.app.current_user and hasattr(self.app, 'gamification'):
                    self.app.gamification.record_exercise_completion(
                        self.app.current_exercise,
                        True,
                        self.current_problem['points'],
                        time_spent
                    )
                
                # Efecto de celebración
                self.celebrate()
            else:
                self.result_label.text = f'❌ Incorrecto. La respuesta es {self.current_problem["answer"]}'
                self.result_label.color = [0.9, 0.3, 0.3, 1]
                
                # Registrar fallo
                if self.app.current_user and hasattr(self.app, 'gamification'):
                    self.app.gamification.record_exercise_completion(
                        self.app.current_exercise,
                        False,
                        0,
                        time_spent
                    )
                
        except ValueError:
            self.result_label.text = 'Por favor, escribe un número válido'
            self.result_label.color = [0.96, 0.77, 0.23, 1]
    
    def show_hint(self, instance):
        """Mostrar pista"""
        if not self.current_problem:
            return
        
        hints = {
            'arithmetic': 'Intenta sumar los números paso a paso',
            'subtraction': 'Recuerda que restar es lo opuesto a sumar',
            'multiplication': 'Puedes pensar en esto como sumas repetidas',
            'division': '¿Cuántas veces cabe el segundo número en el primero?'
        }
        
        ex_type = getattr(self.app, 'current_exercise', 'arithmetic')
        hint = hints.get(ex_type, 'Intenta resolverlo paso a paso')
        
        popup = ModalView(size_hint=(0.8, 0.3))
        content = BoxLayout(orientation='vertical', padding=20)
        content.add_widget(Label(text='💡 Pista', font_size=20, bold=True))
        content.add_widget(Label(text=hint, font_size=16))
        
        ok_btn = Button(text='Entendido', size_hint_y=None, height=40)
        ok_btn.bind(on_press=lambda x: popup.dismiss())
        content.add_widget(ok_btn)
        
        popup.add_widget(content)
        popup.open()
    
    def next_problem(self, instance):
        """Generar siguiente problema"""
        self.generate_problem()
    
    def celebrate(self):
        """Animación de celebración"""
        particles = ['🎉', '✨', '🌟', '⭐', '🎊']
        
        for _ in range(10):
            particle = Label(
                text=random.choice(particles),
                font_size=random.randint(20, 40),
                pos=(random.randint(50, 300), random.randint(100, 500))
            )
            
            self.add_widget(particle)
            
            anim = Animation(
                y=600, 
                opacity=0,
                duration=random.uniform(1, 2)
            )
            anim.start(particle)
            
            # Remover después de animación
            Clock.schedule_once(lambda dt, p=particle: self.remove_widget(p), 2)

# ============================================
# APLICACIÓN PRINCIPAL
# ============================================

class ASMETApp(App):
    """Aplicación principal"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "ASMET CBT ACADEMYC"
        self.db = None
        self.current_user = None
        self.gamification = None
        self.leaderboard = None
        self.current_exercise = None
    
    def build(self):
        """Construir aplicación"""
        # Inicializar base de datos
        self.db = DatabaseManager()
        
        # Crear gestor de pantallas
        sm = ScreenManager(transition=FadeTransition())
        
        # Registrar pantallas
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(DashboardScreen(name='dashboard'))
        sm.add_widget(ExerciseScreen(name='exercise'))
        
        return sm
    
    def on_start(self):
        """Ejecutar al iniciar la aplicación"""
        print("🚀 ASMET App iniciada correctamente")
    
    def on_stop(self):
        """Ejecutar al cerrar la aplicación"""
        if self.db:
            self.db.close()
        print("👋 ASMET App finalizada")

# ============================================
# EJECUCIÓN
# ============================================

if __name__ == '__main__':
    ASMETApp().run()