import json
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict, Optional
import random

@dataclass
class Achievement:
    id: str
    name: str
    description: str
    icon: str
    points: int
    condition: str
    condition_value: int
    unlocked: bool = False
    unlocked_at: Optional[datetime] = None

@dataclass
class Challenge:
    id: str
    title: str
    description: str
    reward_points: int
    reward_coins: int
    duration_hours: int
    participants: int
    created_at: datetime
    ends_at: datetime

class GamificationSystem:
    """Sistema completo de gamificación"""
    
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.achievements = self.load_achievements()
        self.current_streak = 0
        self.daily_quests = []
        self.weekly_challenges = []
        
        # Inicializar sistema
        self.initialize_user_gamification()
    
    def initialize_user_gamification(self):
        """Inicializar gamificación para el usuario"""
        # Cargar logros base
        base_achievements = [
            Achievement(
                id='first_login',
                name='Primer Paso',
                description='Inicia sesión por primera vez',
                icon='👣',
                points=10,
                condition='login_count',
                condition_value=1
            ),
            Achievement(
                id='first_exercise',
                name='Primer Ejercicio',
                description='Completa tu primer ejercicio',
                icon='✅',
                points=20,
                condition='exercises_completed',
                condition_value=1
            ),
            # Agregar más logros...
        ]
        
        # Verificar y desbloquear logros iniciales
        for achievement in base_achievements:
            self.check_and_unlock_achievement(achievement)
    
    def record_exercise_completion(self, exercise_id: str, correct: bool, 
                                 points_earned: int, time_spent: int = 0):
        """Registrar completación de ejercicio"""
        # Actualizar estadísticas
        self.update_user_stats(correct, points_earned, time_spent)
        
        # Verificar logros relacionados con ejercicios
        self.check_exercise_achievements()
        
        # Actualizar racha diaria
        self.update_daily_streak()
        
        # Verificar misiones diarias
        self.check_daily_quests()
        
        # Generar recompensa aleatoria
        if correct and random.random() < 0.1:  # 10% de chance
            self.give_random_reward()
    
    def update_user_stats(self, correct: bool, points: int, time_spent: int):
        """Actualizar estadísticas del usuario"""
        # Implementar lógica de actualización
        pass
    
    def check_exercise_achievements(self):
        """Verificar logros relacionados con ejercicios"""
        exercise_achievements = [
            Achievement(
                id='10_exercises',
                name='Aprendiz Constante',
                description='Completa 10 ejercicios',
                icon='📚',
                points=50,
                condition='total_exercises',
                condition_value=10
            ),
            Achievement(
                id='50_correct',
                name='Precisión Matemática',
                description='Responde 50 ejercicios correctamente',
                icon='🎯',
                points=100,
                condition='correct_exercises',
                condition_value=50
            ),
            Achievement(
                id='speed_demon',
                name='Velocidad Mental',
                description='Completa 10 ejercicios en menos de 30 segundos cada uno',
                icon='⚡',
                points=75,
                condition='fast_exercises',
                condition_value=10
            )
        ]
        
        for achievement in exercise_achievements:
            self.check_and_unlock_achievement(achievement)
    
    def check_and_unlock_achievement(self, achievement: Achievement):
        """Verificar y desbloquear logro"""
        # Verificar condición
        condition_met = self.check_condition(
            achievement.condition,
            achievement.condition_value
        )
        
        if condition_met and not achievement.unlocked:
            achievement.unlocked = True
            achievement.unlocked_at = datetime.now()
            
            # Otorgar recompensa
            self.grant_achievement_reward(achievement)
            
            # Mostrar notificación
            self.show_achievement_notification(achievement)
    
    def check_condition(self, condition: str, value: int) -> bool:
        """Verificar condición específica"""
        # Implementar lógica de verificación
        return False
    
    def grant_achievement_reward(self, achievement: Achievement):
        """Otorgar recompensa por logro"""
        # Otorgar puntos
        self.add_points(achievement.points)
        
        # Otorgar monedas
        coins = achievement.points // 2
        self.add_coins(coins)
        
        # Registrar en base de datos
        self.save_achievement_unlock(achievement)
    
    def add_points(self, points: int):
        """Agregar puntos al usuario"""
        # Implementar lógica de puntos
        pass
    
    def add_coins(self, coins: int):
        """Agregar monedas al usuario"""
        # Implementar lógica de monedas
        pass
    
    def show_achievement_notification(self, achievement: Achievement):
        """Mostrar notificación de logro desbloqueado"""
        notification = {
            'title': '¡Logro Desbloqueado!',
            'message': f'{achievement.name} - {achievement.description}',
            'icon': achievement.icon,
            'points': achievement.points
        }
        
        # Implementar sistema de notificaciones
        pass
    
    def update_daily_streak(self):
        """Actualizar racha diaria"""
        today = datetime.now().date()
        last_activity = self.get_last_activity_date()
        
        if last_activity:
            days_diff = (today - last_activity).days
            
            if days_diff == 1:
                # Continuar racha
                self.current_streak += 1
            elif days_diff > 1:
                # Romper racha
                self.current_streak = 1
            else:
                # Mismo día, mantener racha
                pass
        else:
            # Primera actividad
            self.current_streak = 1
        
        # Verificar logros de racha
        self.check_streak_achievements()
        
        # Actualizar en base de datos
        self.save_streak()
    
    def check_streak_achievements(self):
        """Verificar logros de racha"""
        streak_achievements = [
            Achievement(
                id='3_day_streak',
                name='Compromiso Inicial',
                description='Mantén una racha de 3 días',
                icon='🔥',
                points=30,
                condition='streak_days',
                condition_value=3
            ),
            Achievement(
                id='7_day_streak',
                name='Semana Productiva',
                description='Mantén una racha de 7 días',
                icon='🌟',
                points=70,
                condition='streak_days',
                condition_value=7
            ),
            Achievement(
                id='30_day_streak',
                name='Maestro Consistente',
                description='Mantén una racha de 30 días',
                icon='🏆',
                points=300,
                condition='streak_days',
                condition_value=30
            )
        ]
        
        for achievement in streak_achievements:
            self.check_and_unlock_achievement(achievement)
    
    def check_daily_quests(self):
        """Verificar misiones diarias"""
        today = datetime.now().date()
        
        # Generar misiones diarias si no existen
        if not self.daily_quests:
            self.generate_daily_quests()
        
        # Verificar completación de misiones
        for quest in self.daily_quests:
            if not quest['completed'] and self.is_quest_completed(quest):
                quest['completed'] = True
                quest['completed_at'] = datetime.now()
                
                # Otorgar recompensa
                self.grant_quest_reward(quest)
    
    def generate_daily_quests(self):
        """Generar misiones diarias aleatorias"""
        quest_templates = [
            {
                'id': 'complete_5_exercises',
                'title': 'Practicante Diario',
                'description': 'Completa 5 ejercicios',
                'icon': '📝',
                'condition': {'type': 'exercises', 'count': 5},
                'reward': {'points': 25, 'coins': 5}
            },
            {
                'id': 'perfect_accuracy',
                'title': 'Precisión Perfecta',
                'description': 'Completa 3 ejercicios sin errores',
                'icon': '🎯',
                'condition': {'type': 'perfect_streak', 'count': 3},
                'reward': {'points': 40, 'coins': 8}
            },
            {
                'id': 'speed_challenge',
                'title': 'Desafío de Velocidad',
                'description': 'Completa 2 ejercicios en menos de 30 segundos',
                'icon': '⚡',
                'condition': {'type': 'fast_exercises', 'count': 2},
                'reward': {'points': 35, 'coins': 7}
            }
        ]
        
        # Seleccionar 3 misiones aleatorias
        selected_quests = random.sample(quest_templates, 3)
        
        for quest in selected_quests:
            quest['created_at'] = datetime.now()
            quest['completed'] = False
            quest['progress'] = 0
        
        self.daily_quests = selected_quests
    
    def is_quest_completed(self, quest: Dict) -> bool:
        """Verificar si misión está completada"""
        condition = quest['condition']
        
        if condition['type'] == 'exercises':
            return self.get_today_exercises() >= condition['count']
        elif condition['type'] == 'perfect_streak':
            return self.get_perfect_streak() >= condition['count']
        elif condition['type'] == 'fast_exercises':
            return self.get_fast_exercises() >= condition['count']
        
        return False
    
    def grant_quest_reward(self, quest: Dict):
        """Otorgar recompensa por misión completada"""
        reward = quest['reward']
        
        self.add_points(reward['points'])
        self.add_coins(reward['coins'])
        
        # Mostrar notificación
        self.show_quest_completion_notification(quest)
    
    def show_quest_completion_notification(self, quest: Dict):
        """Mostrar notificación de misión completada"""
        notification = {
            'title': '¡Misión Completada!',
            'message': f'{quest["title"]} - {quest["description"]}',
            'icon': quest['icon'],
            'points': quest['reward']['points'],
            'coins': quest['reward']['coins']
        }
        
        # Implementar sistema de notificaciones
        pass
    
    def give_random_reward(self):
        """Dar recompensa aleatoria"""
        rewards = [
            {'type': 'coins', 'amount': random.randint(1, 5)},
            {'type': 'points', 'amount': random.randint(5, 15)},
            {'type': 'hint', 'amount': 1},
            {'type': 'streak_protection', 'amount': 1}
        ]
        
        reward = random.choice(rewards)
        
        if reward['type'] == 'coins':
            self.add_coins(reward['amount'])
            message = f'¡Encontraste {reward["amount"]} monedas!'
        elif reward['type'] == 'points':
            self.add_points(reward['amount'])
            message = f'¡Bonus de {reward["amount"]} puntos!'
        elif reward['type'] == 'hint':
            # Agregar pista gratis
            message = '¡Obtuviste una pista gratis!'
        elif reward['type'] == 'streak_protection':
            # Protección de racha
            message = '¡Protección de racha obtenida!'
        
        # Mostrar notificación
        self.show_random_reward_notification(message, reward)
    
    def show_random_reward_notification(self, message: str, reward: Dict):
        """Mostrar notificación de recompensa aleatoria"""
        # Implementar sistema de notificaciones
        pass
    
    def get_recent_achievements(self, limit: int = 3) -> List[Achievement]:
        """Obtener logros recientes"""
        # Implementar obtención de logros recientes
        return []
    
    def get_last_activity_date(self):
        """Obtener fecha de última actividad"""
        # Implementar obtención de última actividad
        return None
    
    def get_today_exercises(self) -> int:
        """Obtener ejercicios completados hoy"""
        # Implementar conteo de ejercicios de hoy
        return 0
    
    def get_perfect_streak(self) -> int:
        """Obtener racha actual de ejercicios perfectos"""
        # Implementar cálculo de racha perfecta
        return 0
    
    def get_fast_exercises(self) -> int:
        """Obtener ejercicios rápidos completados"""
        # Implementar conteo de ejercicios rápidos
        return 0
    
    def save_achievement_unlock(self, achievement: Achievement):
        """Guardar desbloqueo de logro en base de datos"""
        # Implementar guardado en BD
        pass
    
    def save_streak(self):
        """Guardar racha en base de datos"""
        # Implementar guardado en BD
        pass
    
    def load_achievements(self) -> List[Achievement]:
        """Cargar logros desde base de datos"""
        # Implementar carga desde BD
        return []
# Añade esto al final del archivo gamification.py (antes del último cierre)

class Leaderboard:
    """Sistema de tablas de clasificación"""
    
    def __init__(self):
        self.leaderboards = {
            'daily': [],
            'weekly': [],
            'monthly': [],
            'all_time': []
        }
    
    def add_score(self, user_id: int, username: str, score: int, 
                  leaderboard_type: str = 'daily'):
        """Agregar puntuación a la tabla de clasificación"""
        if leaderboard_type not in self.leaderboards:
            raise ValueError(f"Tipo de leaderboard no válido: {leaderboard_type}")
        
        entry = {
            'user_id': user_id,
            'username': username,
            'score': score,
            'timestamp': datetime.now()
        }
        
        self.leaderboards[leaderboard_type].append(entry)
        # Ordenar de mayor a menor puntuación
        self.leaderboards[leaderboard_type].sort(
            key=lambda x: x['score'], 
            reverse=True
        )
        
        # Mantener solo las top 100 posiciones
        self.leaderboards[leaderboard_type] = self.leaderboards[leaderboard_type][:100]
    
    def get_leaderboard(self, leaderboard_type: str = 'daily', 
                       limit: int = 10) -> List[Dict]:
        """Obtener tabla de clasificación"""
        if leaderboard_type not in self.leaderboards:
            raise ValueError(f"Tipo de leaderboard no válido: {leaderboard_type}")
        
        return self.leaderboards[leaderboard_type][:limit]
    
    def get_user_position(self, user_id: int, 
                         leaderboard_type: str = 'daily') -> int:
        """Obtener posición del usuario en el leaderboard"""
        if leaderboard_type not in self.leaderboards:
            return -1
        
        for i, entry in enumerate(self.leaderboards[leaderboard_type]):
            if entry['user_id'] == user_id:
                return i + 1  # Posición (1-indexed)
        
        return -1  # Usuario no encontrado
    
    def clear_leaderboard(self, leaderboard_type: str):
        """Limpiar tabla de clasificación"""
        if leaderboard_type in self.leaderboards:
            self.leaderboards[leaderboard_type] = []
    
    def update_weekly_leaderboard(self):
        """Actualizar leaderboard semanal"""
        # Combinar puntuaciones diarias en semanales
        self.leaderboards['weekly'] = self.aggregate_scores('daily', days=7)
    
    def update_monthly_leaderboard(self):
        """Actualizar leaderboard mensual"""
        self.leaderboards['monthly'] = self.aggregate_scores('daily', days=30)
    
    def update_all_time_leaderboard(self):
        """Actualizar leaderboard histórico"""
        # Combinar todas las puntuaciones
        all_scores = {}
        for entry in self.leaderboards['daily']:
            user_id = entry['user_id']
            if user_id not in all_scores:
                all_scores[user_id] = {
                    'user_id': user_id,
                    'username': entry['username'],
                    'score': 0
                }
            all_scores[user_id]['score'] += entry['score']
        
        self.leaderboards['all_time'] = sorted(
            all_scores.values(), 
            key=lambda x: x['score'], 
            reverse=True
        )[:100]
    
    def aggregate_scores(self, source_type: str, days: int = 7) -> List[Dict]:
        """Agregar puntuaciones de múltiples días"""
        aggregated = {}
        
        for entry in self.leaderboards[source_type]:
            user_id = entry['user_id']
            
            # Verificar si la entrada es reciente
            entry_date = entry['timestamp']
            days_diff = (datetime.now() - entry_date).days
            
            if days_diff <= days:
                if user_id not in aggregated:
                    aggregated[user_id] = {
                        'user_id': user_id,
                        'username': entry['username'],
                        'score': 0
                    }
                aggregated[user_id]['score'] += entry['score']
        
        return sorted(
            aggregated.values(), 
            key=lambda x: x['score'], 
            reverse=True
        )[:100]
    
    def get_top_players(self, limit: int = 5) -> List[Dict]:
        """Obtener mejores jugadores de todos los tiempos"""
        return self.leaderboards['all_time'][:limit]
    
    def export_leaderboard(self, leaderboard_type: str = 'daily') -> str:
        """Exportar leaderboard como JSON"""
        import json
        return json.dumps(self.leaderboards.get(leaderboard_type, []), 
                         default=str, 
                         indent=2)
    
    def load_from_json(self, json_data: str, leaderboard_type: str):
        """Cargar leaderboard desde JSON"""
        import json
        data = json.loads(json_data)
        
        # Convertir strings de fecha a objetos datetime
        for entry in data:
            if 'timestamp' in entry and isinstance(entry['timestamp'], str):
                entry['timestamp'] = datetime.fromisoformat(entry['timestamp'])
        
        self.leaderboards[leaderboard_type] = data