import sqlite3
import json
from datetime import datetime
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
import hashlib
import os

@dataclass
class User:
    id: int
    username: str
    email: str
    level: int
    total_points: int
    coins: int
    overall_progress: float
    created_at: datetime
    last_login: datetime
    
    def add_points(self, points: int):
        self.total_points += points
        self.coins += points // 10  # 1 moneda cada 10 puntos

@dataclass  
class ExerciseResult:
    id: int
    user_id: int
    exercise_id: str
    correct: bool
    time_spent: int
    points_earned: int
    timestamp: datetime

@dataclass
class Achievement:
    id: int
    name: str
    description: str
    icon: str
    points: int
    unlocked: bool
    unlocked_at: Optional[datetime]

class DatabaseManager:
    """Gestor avanzado de base de datos SQLite"""
    
    def __init__(self, db_path='asmet_data.db'):
        self.db_path = db_path
        self.conn = None
        self.connect()
    
    def connect(self):
        """Conectar a la base de datos"""
        self.conn = sqlite3.connect(
            self.db_path,
            check_same_thread=False
        )
        self.conn.row_factory = sqlite3.Row
        self.create_tables()
    
    def create_tables(self):
        """Crear todas las tablas necesarias"""
        cursor = self.conn.cursor()
        
        # Tabla de usuarios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                level INTEGER DEFAULT 1,
                total_points INTEGER DEFAULT 0,
                coins INTEGER DEFAULT 0,
                overall_progress REAL DEFAULT 0.0,
                streak_days INTEGER DEFAULT 0,
                last_streak_date TEXT,
                created_at TEXT NOT NULL,
                last_login TEXT,
                settings TEXT DEFAULT '{}',
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Tabla de progreso por materia
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subject_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                subject TEXT NOT NULL,
                chapter INTEGER DEFAULT 1,
                progress REAL DEFAULT 0.0,
                exercises_completed INTEGER DEFAULT 0,
                average_score REAL DEFAULT 0.0,
                time_spent INTEGER DEFAULT 0,
                last_updated TEXT,
                UNIQUE(user_id, subject),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Tabla de resultados de ejercicios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS exercise_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                exercise_id TEXT NOT NULL,
                exercise_type TEXT NOT NULL,
                correct BOOLEAN NOT NULL,
                user_answer TEXT,
                correct_answer TEXT,
                time_spent INTEGER,
                points_earned INTEGER DEFAULT 0,
                difficulty TEXT,
                topic TEXT,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Tabla de logros
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                achievement_id TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                icon TEXT,
                points INTEGER DEFAULT 0,
                unlocked BOOLEAN DEFAULT 0,
                unlocked_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id),
                UNIQUE(user_id, achievement_id)
            )
        ''')
        
        # Tabla de lecciones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lessons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                topic TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                content TEXT NOT NULL,
                examples TEXT,  -- JSON array
                exercises TEXT,  -- JSON array
                video_url TEXT,
                estimated_time INTEGER,
                points_reward INTEGER DEFAULT 10,
                created_at TEXT NOT NULL,
                updated_at TEXT
            )
        ''')
        
        # Tabla de lecciones completadas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS completed_lessons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                lesson_id INTEGER NOT NULL,
                completed_at TEXT NOT NULL,
                score REAL,
                time_spent INTEGER,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (lesson_id) REFERENCES lessons (id),
                UNIQUE(user_id, lesson_id)
            )
        ''')
        
        # Tabla de bookmarks
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bookmarks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                lesson_id INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (lesson_id) REFERENCES lessons (id),
                UNIQUE(user_id, lesson_id)
            )
        ''')
        
        # Tabla de tests
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                test_type TEXT NOT NULL,
                score REAL NOT NULL,
                total_questions INTEGER,
                correct_answers INTEGER,
                time_spent INTEGER,
                taken_at TEXT NOT NULL,
                weak_areas TEXT,  -- JSON array
                recommendations TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Tabla de notificaciones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                type TEXT NOT NULL,
                read BOOLEAN DEFAULT 0,
                created_at TEXT NOT NULL,
                action_url TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Tabla de configuración de la app
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS app_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        
        self.conn.commit()
    
    def initialize_database(self):
        """Inicializar base de datos"""
        self.create_tables()
        print("Base de datos inicializada")
    
    def register_user(self, username: str, email: str, password: str) -> Tuple[bool, str]:
        """Registrar nuevo usuario con seguridad"""
        try:
            # Verificar si usuario existe
            cursor = self.conn.cursor()
            cursor.execute(
                'SELECT id FROM users WHERE username = ? OR email = ?',
                (username, email)
            )
            if cursor.fetchone():
                return False, 'El usuario o email ya existe'
            
            # Generar salt y hash de contraseña
            salt = os.urandom(32).hex()
            password_hash = self._hash_password(password, salt)
            
            # Insertar usuario
            created_at = datetime.now().isoformat()
            cursor.execute('''
                INSERT INTO users 
                (username, email, password_hash, salt, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, email, password_hash, salt, created_at))
            
            user_id = cursor.lastrowid
            
            # Inicializar progreso por materias
            subjects = ['Aritmética', 'Álgebra', 'Geometría', 'Cálculo', 'Estadística']
            for subject in subjects:
                cursor.execute('''
                    INSERT INTO subject_progress 
                    (user_id, subject, last_updated)
                    VALUES (?, ?, ?)
                ''', (user_id, subject, created_at))
            
            # Crear logros iniciales
            initial_achievements = [
                ('first_login', 'Primer Inicio', 'Bienvenido a ASMET', '👋', 10),
                ('profile_created', 'Perfil Creado', 'Has creado tu cuenta', '🎉', 20)
            ]
            
            for ach_id, name, desc, icon, points in initial_achievements:
                cursor.execute('''
                    INSERT INTO achievements 
                    (user_id, achievement_id, name, description, icon, points)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (user_id, ach_id, name, desc, icon, points))
            
            self.conn.commit()
            return True, 'Usuario registrado exitosamente'
            
        except Exception as e:
            return False, f'Error en registro: {str(e)}'
    
    def authenticate_user(self, identifier: str, password: str) -> Optional[User]:
        """Autenticar usuario por username o email"""
        try:
            cursor = self.conn.cursor()
            
            # Buscar usuario por username o email
            cursor.execute('''
                SELECT * FROM users 
                WHERE (username = ? OR email = ?) AND is_active = 1
            ''', (identifier, identifier))
            
            user_data = cursor.fetchone()
            if not user_data:
                return None
            
            # Verificar contraseña
            stored_hash = user_data['password_hash']
            salt = user_data['salt']
            input_hash = self._hash_password(password, salt)
            
            if stored_hash != input_hash:
                return None
            
            # Actualizar último login
            cursor.execute('''
                UPDATE users SET last_login = ? WHERE id = ?
            ''', (datetime.now().isoformat(), user_data['id']))
            self.conn.commit()
            
            # Crear objeto User
            return User(
                id=user_data['id'],
                username=user_data['username'],
                email=user_data['email'],
                level=user_data['level'],
                total_points=user_data['total_points'],
                coins=user_data['coins'],
                overall_progress=user_data['overall_progress'],
                created_at=datetime.fromisoformat(user_data['created_at']),
                last_login=datetime.fromisoformat(user_data['last_login'])
            )
            
        except Exception as e:
            print(f"Error en autenticación: {e}")
            return None
    
    def get_subject_progress(self, user_id: int) -> List[Tuple[str, float]]:
        """Obtener progreso por materia"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT subject, progress 
            FROM subject_progress 
            WHERE user_id = ?
            ORDER BY progress DESC
        ''', (user_id,))
        
        return [(row['subject'], row['progress']) for row in cursor.fetchall()]
    
    def get_study_stats(self, user_id: int) -> Dict:
        """Obtener estadísticas de estudio"""
        cursor = self.conn.cursor()
        
        # Tiempo total de estudio
        cursor.execute('''
            SELECT SUM(time_spent) as total_time
            FROM exercise_results 
            WHERE user_id = ?
        ''', (user_id,))
        total_time = cursor.fetchone()['total_time'] or 0
        
        # Ejercicios completados
        cursor.execute('''
            SELECT COUNT(*) as exercises_done
            FROM exercise_results 
            WHERE user_id = ?
        ''', (user_id,))
        exercises_done = cursor.fetchone()['exercises_done']
        
        # Precisión
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN correct = 1 THEN 1 ELSE 0 END) as correct
            FROM exercise_results 
            WHERE user_id = ?
        ''', (user_id,))
        stats = cursor.fetchone()
        accuracy = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
        
        # Racha actual
        cursor.execute('''
            SELECT streak_days 
            FROM users 
            WHERE id = ?
        ''', (user_id,))
        streak = cursor.fetchone()['streak_days']
        
        return {
            'total_time': total_time // 60,  # Convertir a horas
            'exercises_done': exercises_done,
            'accuracy': round(accuracy, 1),
            'streak': streak
        }
    
    def get_lesson(self, lesson_id: int) -> Optional[Dict]:
        """Obtener lección completa"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM lessons WHERE id = ?', (lesson_id,))
        
        lesson = cursor.fetchone()
        if not lesson:
            return None
        
        # Convertir JSON strings a objetos
        examples = json.loads(lesson['examples']) if lesson['examples'] else []
        exercises = json.loads(lesson['exercises']) if lesson['exercises'] else []
        
        return {
            'id': lesson['id'],
            'title': lesson['title'],
            'topic': lesson['topic'],
            'difficulty': lesson['difficulty'],
            'content': lesson['content'],
            'examples': examples,
            'exercises': exercises,
            'video_url': lesson['video_url'],
            'estimated_time': lesson['estimated_time'],
            'points_reward': lesson['points_reward']
        }
    
    def toggle_bookmark(self, user_id: int, lesson_id: int, bookmark: bool):
        """Agregar o remover bookmark"""
        cursor = self.conn.cursor()
        
        if bookmark:
            # Agregar bookmark
            cursor.execute('''
                INSERT OR IGNORE INTO bookmarks 
                (user_id, lesson_id, created_at)
                VALUES (?, ?, ?)
            ''', (user_id, lesson_id, datetime.now().isoformat()))
        else:
            # Remover bookmark
            cursor.execute('''
                DELETE FROM bookmarks 
                WHERE user_id = ? AND lesson_id = ?
            ''', (user_id, lesson_id))
        
        self.conn.commit()
    
    def save_test_results(self, user_id: int, test_type: str, score: float, 
                         time_spent: int, weak_areas: List[str] = None):
        """Guardar resultados de test"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            INSERT INTO tests 
            (user_id, test_type, score, time_spent, taken_at, weak_areas)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            user_id, 
            test_type, 
            score, 
            time_spent,
            datetime.now().isoformat(),
            json.dumps(weak_areas) if weak_areas else '[]'
        ))
        
        # Actualizar progreso del usuario
        cursor.execute('''
            UPDATE users 
            SET total_points = total_points + ?,
                overall_progress = overall_progress + 0.5
            WHERE id = ?
        ''', (int(score), user_id))
        
        self.conn.commit()
    
    def get_pending_notifications(self, user_id: int) -> List[Dict]:
        """Obtener notificaciones pendientes"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM notifications 
            WHERE user_id = ? AND read = 0
            ORDER BY created_at DESC
            LIMIT 10
        ''', (user_id,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def save_user_state(self, user_id: int, state: Dict):
        """Guardar estado del usuario"""
        cursor = self.conn.cursor()
        
        # Convertir estado a JSON
        state_json = json.dumps(state)
        
        cursor.execute('''
            INSERT OR REPLACE INTO app_settings (key, value, updated_at)
            VALUES (?, ?, ?)
        ''', (f'user_state_{user_id}', state_json, datetime.now().isoformat()))
        
        self.conn.commit()
    
    def has_saved_user(self) -> bool:
        """Verificar si hay usuario guardado"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) as count FROM users WHERE is_active = 1')
        return cursor.fetchone()['count'] > 0
    
    def get_last_user(self) -> Dict:
        """Obtener último usuario activo"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM users 
            WHERE is_active = 1 
            ORDER BY last_login DESC 
            LIMIT 1
        ''')
        
        user_data = cursor.fetchone()
        return dict(user_data) if user_data else {}
    
    def _hash_password(self, password: str, salt: str) -> str:
        """Generar hash seguro de contraseña"""
        return hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        ).hex()
    
    def close(self):
        """Cerrar conexión a la base de datos"""
        if self.conn:
            self.conn.close()