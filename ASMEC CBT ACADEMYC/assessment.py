import random
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from enum import Enum

class QuestionType(Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"
    CALCULATION = "calculation"
    PROBLEM_SOLVING = "problem_solving"

class Difficulty(Enum):
    EASY = 1
    MEDIUM = 2
    HARD = 3
    EXPERT = 4

class Question:
    """Clase para preguntas de evaluación"""
    
    def __init__(self, id: str, text: str, question_type: QuestionType,
                 correct_answer: str, points: int, difficulty: Difficulty,
                 topic: str, options: List[str] = None, hint: str = None):
        self.id = id
        self.text = text
        self.type = question_type
        self.correct_answer = correct_answer
        self.points = points
        self.difficulty = difficulty
        self.topic = topic
        self.options = options or []
        self.hint = hint
        self.user_answer = None
        self.time_spent = 0
        self.correct = False

class AssessmentEngine:
    """Motor de evaluación adaptativa"""
    
    def __init__(self):
        self.question_bank = self.load_question_bank()
        self.user_proficiency = {}
        self.adaptive_algorithms = AdaptiveAlgorithms()
    
    def load_question_bank(self) -> Dict[str, List[Question]]:
        """Cargar banco de preguntas"""
        return {
            'aritmetica': self.generate_arithmetic_questions(),
            'algebra': self.generate_algebra_questions(),
            'geometria': self.generate_geometry_questions(),
            'calculo': self.generate_calculus_questions(),
            'estadistica': self.generate_statistics_questions()
        }
    
    def generate_arithmetic_questions(self) -> List[Question]:
        """Generar preguntas de aritmética"""
        questions = []
        
        # Nivel fácil
        questions.append(Question(
            id="arith_001",
            text="¿Cuál es el resultado de 15 + 27?",
            question_type=QuestionType.MULTIPLE_CHOICE,
            correct_answer="42",
            points=10,
            difficulty=Difficulty.EASY,
            topic="suma",
            options=["40", "41", "42", "43"]
        ))
        
        questions.append(Question(
            id="arith_002",
            text="Calcula: 48 ÷ 6",
            question_type=QuestionType.SHORT_ANSWER,
            correct_answer="8",
            points=10,
            difficulty=Difficulty.EASY,
            topic="division"
        ))
        
        # Nivel medio
        questions.append(Question(
            id="arith_003",
            text="Un producto cuesta $120. Si tiene un descuento del 15%, ¿cuál es el precio final?",
            question_type=QuestionType.PROBLEM_SOLVING,
            correct_answer="102",
            points=20,
            difficulty=Difficulty.MEDIUM,
            topic="porcentajes",
            hint="Calcula el 15% de 120 y réstalo del precio original"
        ))
        
        # Nivel difícil
        questions.append(Question(
            id="arith_004",
            text="Simplifica: (3/4) + (2/5) - (1/2)",
            question_type=QuestionType.CALCULATION,
            correct_answer="13/20",
            points=30,
            difficulty=Difficulty.HARD,
            topic="fracciones"
        ))
        
        return questions
    
    def generate_algebra_questions(self) -> List[Question]:
        """Generar preguntas de álgebra"""
        questions = []
        
        # Ecuaciones lineales
        questions.append(Question(
            id="alg_001",
            text="Resuelve para x: 2x + 5 = 13",
            question_type=QuestionType.SHORT_ANSWER,
            correct_answer="4",
            points=15,
            difficulty=Difficulty.EASY,
            topic="ecuaciones_lineales"
        ))
        
        questions.append(Question(
            id="alg_002",
            text="Resuelve el sistema: x + y = 10, x - y = 2",
            question_type=QuestionType.PROBLEM_SOLVING,
            correct_answer="x=6, y=4",
            points=25,
            difficulty=Difficulty.MEDIUM,
            topic="sistemas_ecuaciones",
            hint="Usa el método de eliminación o sustitución"
        ))
        
        # Factorización
        questions.append(Question(
            id="alg_003",
            text="Factoriza completamente: x² - 5x + 6",
            question_type=QuestionType.SHORT_ANSWER,
            correct_answer="(x-2)(x-3)",
            points=20,
            difficulty=Difficulty.MEDIUM,
            topic="factorizacion"
        ))
        
        return questions
    
    def generate_geometry_questions(self) -> List[Question]:
        """Generar preguntas de geometría"""
        questions = []
        
        questions.append(Question(
            id="geo_001",
            text="El área de un rectángulo es 24 cm². Si el largo es 6 cm, ¿cuál es el ancho?",
            question_type=QuestionType.PROBLEM_SOLVING,
            correct_answer="4",
            points=15,
            difficulty=Difficulty.EASY,
            topic="areas"
        ))
        
        questions.append(Question(
            id="geo_002",
            text="En un triángulo rectángulo, los catetos miden 3 cm y 4 cm. ¿Cuánto mide la hipotenusa?",
            question_type=QuestionType.SHORT_ANSWER,
            correct_answer="5",
            points=20,
            difficulty=Difficulty.MEDIUM,
            topic="teorema_pitagoras"
        ))
        
        return questions
    
    def generate_calculus_questions(self) -> List[Question]:
        """Generar preguntas de cálculo"""
        return []  # Para implementar
    
    def generate_statistics_questions(self) -> List[Question]:
        """Generar preguntas de estadística"""
        return []  # Para implementar
    
    def get_recommended_lesson(self, user_id: int) -> Optional[Dict]:
        """Obtener lección recomendada basada en evaluación"""
        proficiency = self.get_user_proficiency(user_id)
        
        # Identificar área más débil
        weakest_topic = min(proficiency.items(), key=lambda x: x[1])[0]
        
        # Buscar lección apropiada
        available_lessons = self.get_available_lessons(user_id, weakest_topic)
        
        if available_lessons:
            # Seleccionar lección con dificultad apropiada
            user_level = proficiency.get(weakest_topic, 1)
            appropriate_lessons = [
                lesson for lesson in available_lessons 
                if lesson['difficulty'] <= user_level + 1
            ]
            
            if appropriate_lessons:
                return random.choice(appropriate_lessons)
        
        return None
    
    def get_user_proficiency(self, user_id: int) -> Dict[str, float]:
        """Obtener perfil de proficiencia del usuario"""
        if user_id not in self.user_proficiency:
            # Inicializar proficiencia
            self.user_proficiency[user_id] = {
                'aritmetica': 1.0,
                'algebra': 1.0,
                'geometria': 1.0,
                'calculo': 0.0,
                'estadistica': 0.0
            }
        
        return self.user_proficiency[user_id]
    
    def update_proficiency(self, user_id: int, topic: str, 
                          performance: float, question_difficulty: Difficulty):
        """Actualizar proficiencia del usuario"""
        proficiency = self.get_user_proficiency(user_id)
        
        # Algoritmo de actualización adaptativa
        current_level = proficiency.get(topic, 1.0)
        adjustment = self.adaptive_algorithms.calculate_adjustment(
            performance, 
            question_difficulty.value
        )
        
        new_level = current_level + adjustment
        new_level = max(0.5, min(new_level, 5.0))  # Limitar entre 0.5 y 5.0
        
        proficiency[topic] = new_level
        self.user_proficiency[user_id] = proficiency
    
    def get_available_lessons(self, user_id: int, topic: str) -> List[Dict]:
        """Obtener lecciones disponibles para un tema"""
        # Esto debería conectarse con la base de datos de lecciones
        # Por ahora, devolver lecciones simuladas
        
        lesson_templates = {
            'aritmetica': [
                {'id': 1, 'title': 'Operaciones Básicas', 'difficulty': 1},
                {'id': 2, 'title': 'Fracciones y Decimales', 'difficulty': 2},
                {'id': 3, 'title': 'Porcentajes y Razones', 'difficulty': 3}
            ],
            'algebra': [
                {'id': 4, 'title': 'Introducción al Álgebra', 'difficulty': 1},
                {'id': 5, 'title': 'Ecuaciones Lineales', 'difficulty': 2},
                {'id': 6, 'title': 'Sistemas de Ecuaciones', 'difficulty': 3}
            ],
            'geometria': [
                {'id': 7, 'title': 'Figuras Planas', 'difficulty': 1},
                {'id': 8, 'title': 'Áreas y Perímetros', 'difficulty': 2},
                {'id': 9, 'title': 'Teorema de Pitágoras', 'difficulty': 3}
            ]
        }
        
        return lesson_templates.get(topic, [])

class AdaptiveTest:
    """Sistema de exámenes adaptativos"""
    
    def __init__(self):
        self.assessment_engine = AssessmentEngine()
        self.current_test = None
        self.test_history = []
    
    def start_test(self, test_type: str, user_level: int = 1):
        """Iniciar examen adaptativo"""
        self.current_test = {
            'id': f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'type': test_type,
            'user_level': user_level,
            'questions': [],
            'current_question_index': 0,
            'start_time': datetime.now(),
            'score': 0,
            'estimated_ability': user_level,
            'questions_answered': 0,
            'current_difficulty': Difficulty.EASY
        }
        
        # Generar primera pregunta
        first_question = self.select_next_question()
        self.current_test['questions'].append(first_question)
    
    def select_next_question(self) -> Optional[Question]:
        """Seleccionar siguiente pregunta adaptativamente"""
        if not self.current_test:
            return None
        
        current_ability = self.current_test['estimated_ability']
        current_difficulty = self.current_test['current_difficulty']
        
        # Seleccionar tema basado en distribución
        topic = self.select_topic()
        
        # Filtrar preguntas por dificultad y tema
        available_questions = [
            q for q in self.assessment_engine.question_bank.get(topic, [])
            if q.difficulty == current_difficulty
        ]
        
        if not available_questions:
            # Si no hay preguntas en esa dificultad, ajustar
            if current_difficulty.value < Difficulty.EXPERT.value:
                self.current_test['current_difficulty'] = Difficulty(
                    current_difficulty.value + 1
                )
            else:
                self.current_test['current_difficulty'] = Difficulty.EASY
            
            return self.select_next_question()
        
        # Seleccionar pregunta aleatoria
        selected_question = random.choice(available_questions)
        
        return selected_question
    
    def select_topic(self) -> str:
        """Seleccionar tema para la siguiente pregunta"""
        topics = ['aritmetica', 'algebra', 'geometria']
        
        # Distribución basada en el test
        if self.current_test['type'] == 'diagnostico':
            # Distribución equitativa para diagnóstico
            return random.choice(topics)
        elif self.current_test['type'] == 'progreso':
            # Enfocarse en áreas débiles identificadas
            weak_areas = self.identify_weak_areas()
            if weak_areas:
                return random.choice(weak_areas)
        
        return random.choice(topics)
    
    def identify_weak_areas(self) -> List[str]:
        """Identificar áreas débiles del usuario"""
        # Basado en historial de respuestas
        weak_areas = []
        
        for question in self.current_test['questions']:
            if not question.correct:
                if question.topic not in weak_areas:
                    weak_areas.append(question.topic)
        
        return weak_areas
    
    def submit_answer(self, question_id: str, user_answer: str, 
                     time_spent: int = 0) -> Tuple[bool, str]:
        """Enviar respuesta y obtener feedback"""
        if not self.current_test:
            return False, "No hay examen activo"
        
        # Buscar pregunta actual
        current_index = self.current_test['current_question_index']
        if current_index >= len(self.current_test['questions']):
            return False, "No hay pregunta actual"
        
        question = self.current_test['questions'][current_index]
        
        # Verificar respuesta
        is_correct = self.check_answer(question, user_answer)
        question.user_answer = user_answer
        question.time_spent = time_spent
        question.correct = is_correct
        
        # Actualizar puntaje
        if is_correct:
            self.current_test['score'] += question.points
        
        # Actualizar estadísticas
        self.current_test['questions_answered'] += 1
        
        # Actualizar estimación de habilidad
        self.update_ability_estimate(question, is_correct)
        
        # Ajustar dificultad para siguiente pregunta
        self.adjust_difficulty(is_correct)
        
        # Generar feedback
        feedback = self.generate_feedback(question, is_correct, user_answer)
        
        # Seleccionar siguiente pregunta
        if self.current_test['questions_answered'] < 20:  # Límite de 20 preguntas
            next_question = self.select_next_question()
            if next_question:
                self.current_test['questions'].append(next_question)
                self.current_test['current_question_index'] += 1
        
        return is_correct, feedback
    
    def check_answer(self, question: Question, user_answer: str) -> bool:
        """Verificar si la respuesta es correcta"""
        # Normalizar respuestas
        normalized_user = user_answer.strip().lower()
        normalized_correct = question.correct_answer.strip().lower()
        
        # Comparación exacta para cálculos
        if question.type in [QuestionType.CALCULATION, QuestionType.SHORT_ANSWER]:
            try:
                # Intentar comparación numérica
                user_num = float(normalized_user)
                correct_num = float(normalized_correct)
                return abs(user_num - correct_num) < 0.001
            except:
                # Comparación de texto
                return normalized_user == normalized_correct
        
        # Para opción múltiple, comparar el texto o índice
        elif question.type == QuestionType.MULTIPLE_CHOICE:
            if normalized_user in ['a', 'b', 'c', 'd']:
                # Usuario seleccionó letra
                index = ord(normalized_user) - ord('a')
                if 0 <= index < len(question.options):
                    return question.options[index] == question.correct_answer
            else:
                # Usuario escribió la respuesta
                return normalized_user == normalized_correct
        
        return normalized_user == normalized_correct
    
    def update_ability_estimate(self, question: Question, is_correct: bool):
        """Actualizar estimación de habilidad usando teoría de respuesta al ítem"""
        current_ability = self.current_test['estimated_ability']
        question_difficulty = question.difficulty.value
        
        # Algoritmo simplificado de actualización
        if is_correct:
            # Si respondió correctamente una pregunta difícil, aumentar habilidad más
            adjustment = 0.1 * question_difficulty
        else:
            # Si falló una pregunta fácil, disminuir habilidad más
            adjustment = -0.1 * (1 / question_difficulty)
        
        new_ability = current_ability + adjustment
        new_ability = max(1.0, min(new_ability, 10.0))  # Limitar entre 1 y 10
        
        self.current_test['estimated_ability'] = new_ability
    
    def adjust_difficulty(self, was_correct: bool):
        """Ajustar dificultad para la siguiente pregunta"""
        current_difficulty = self.current_test['current_difficulty']
        
        if was_correct:
            # Aumentar dificultad si respondió correctamente
            if current_difficulty.value < Difficulty.EXPERT.value:
                self.current_test['current_difficulty'] = Difficulty(
                    current_difficulty.value + 1
                )
        else:
            # Disminuir dificultad si respondió incorrectamente
            if current_difficulty.value > Difficulty.EASY.value:
                self.current_test['current_difficulty'] = Difficulty(
                    current_difficulty.value - 1
                )
    
    def generate_feedback(self, question: Question, is_correct: bool, 
                         user_answer: str) -> str:
        """Generar feedback personalizado"""
        if is_correct:
            feedbacks = [
                "¡Excelente trabajo!",
                "¡Correcto! Sigue así.",
                "¡Muy bien! Tu respuesta es precisa.",
                "¡Perfecto! Dominas este concepto."
            ]
            return random.choice(feedbacks)
        else:
            feedback = f"Tu respuesta: {user_answer}\n"
            feedback += f"Respuesta correcta: {question.correct_answer}\n\n"
            
            if question.hint:
                feedback += f"Pista para la próxima: {question.hint}"
            else:
                feedback += "Revisa los conceptos y vuelve a intentar."
            
            return feedback
    
    def calculate_final_score(self, raw_score: int) -> float:
        """Calcular puntaje final normalizado"""
        max_possible = sum(q.points for q in self.current_test['questions'])
        
        if max_possible == 0:
            return 0.0
        
        normalized_score = (raw_score / max_possible) * 100
        return round(normalized_score, 1)
    
    def get_weak_areas(self) -> List[str]:
        """Obtener áreas débiles basadas en el examen"""
        if not self.current_test:
            return []
        
        weak_areas = []
        topic_performance = {}
        
        # Analizar rendimiento por tema
        for question in self.current_test['questions']:
            topic = question.topic
            if topic not in topic_performance:
                topic_performance[topic] = {'correct': 0, 'total': 0}
            
            topic_performance[topic]['total'] += 1
            if question.correct:
                topic_performance[topic]['correct'] += 1
        
        # Identificar áreas con menos del 70% de aciertos
        for topic, stats in topic_performance.items():
            accuracy = stats['correct'] / stats['total'] * 100
            if accuracy < 70:
                weak_areas.append(topic)
        
        return weak_areas
    
    def get_incorrect_answers(self) -> List[Dict]:
        """Obtener respuestas incorrectas para revisión"""
        if not self.current_test:
            return []
        
        incorrect = []
        for question in self.current_test['questions']:
            if not question.correct:
                incorrect.append({
                    'question': question.text,
                    'user_answer': question.user_answer,
                    'correct_answer': question.correct_answer,
                    'topic': question.topic,
                    'hint': question.hint
                })
        
        return incorrect

class AdaptiveAlgorithms:
    """Algoritmos adaptativos para evaluación"""
    
    @staticmethod
    def calculate_adjustment(performance: float, difficulty: int) -> float:
        """Calcular ajuste de proficiencia"""
        # performance: 0.0 a 1.0 (porcentaje de acierto)
        # difficulty: 1 a 4 (nivel de dificultad)
        
        # Ajuste basado en desempeño vs dificultad esperada
        expected_performance = 1.0 - (difficulty - 1) * 0.25  # 100%, 75%, 50%, 25%
        
        difference = performance - expected_performance
        
        # Factor de ajuste
        adjustment = difference * 0.2
        
        return adjustment
    
    @staticmethod
    def calculate_next_difficulty(current_ability: float, 
                                 previous_performance: float) -> Difficulty:
        """Calcular siguiente nivel de dificultad"""
        # current_ability: 1.0 a 10.0
        # previous_performance: 0.0 a 1.0
        
        if current_ability < 3.0:
            base_difficulty = Difficulty.EASY
        elif current_ability < 6.0:
            base_difficulty = Difficulty.MEDIUM
        elif current_ability < 9.0:
            base_difficulty = Difficulty.HARD
        else:
            base_difficulty = Difficulty.EXPERT
        
        # Ajustar basado en desempeño previo
        if previous_performance > 0.8:
            # Si tuvo buen desempeño, aumentar dificultad
            if base_difficulty.value < Difficulty.EXPERT.value:
                return Difficulty(base_difficulty.value + 1)
        elif previous_performance < 0.4:
            # Si tuvo mal desempeño, disminuir dificultad
            if base_difficulty.value > Difficulty.EASY.value:
                return Difficulty(base_difficulty.value - 1)
        
        return base_difficulty

class AdaptiveExerciseGenerator:
    """Generador de ejercicios adaptativos"""
    
    def __init__(self, difficulty: Difficulty, topic: str):
        self.difficulty = difficulty
        self.topic = topic
        self.problem_templates = self.load_templates()
    
    def load_templates(self) -> Dict:
        """Cargar plantillas de problemas"""
        return {
            'aritmetica': {
                Difficulty.EASY: [
                    "¿Cuánto es {a} + {b}?",
                    "Calcula: {a} - {b}",
                    "{a} × {b} = ?",
                    "{a} ÷ {b} = ?"
                ],
                Difficulty.MEDIUM: [
                    "Calcula: ({a} + {b}) × {c}",
                    "¿Cuál es el {p}% de {n}?",
                    "Simplifica: {a}/{b} + {c}/{d}",
                    "Resuelve: {a}² - {b}²"
                ],
                Difficulty.HARD: [
                    "Calcula: √({a} × {b} + {c})",
                    "Resuelve: ({a} + {b}i)({c} - {d}i)",
                    "Encuentra el MCD de {a}, {b} y {c}",
                    "Calcula la media de: {lista}"
                ]
            },
            'algebra': {
                Difficulty.EASY: [
                    "Resuelve: {a}x + {b} = {c}",
                    "Simplifica: {a}x + {b}x",
                    "Evalúa: {a}x² cuando x = {b}",
                    "¿Cuál es el coeficiente de x en {a}x + {b}?"
                ],
                Difficulty.MEDIUM: [
                    "Resuelve el sistema: x + y = {a}, x - y = {b}",
                    "Factoriza: x² + {a}x + {b}",
                    "Grafica: y = {a}x + {b}",
                    "Resuelve: |x - {a}| = {b}"
                ],
                Difficulty.HARD: [
                    "Resuelve: {a}x³ + {b}x² + {c}x + {d} = 0",
                    "Encuentra la inversa de la matriz [[{a},{b}],[{c},{d}]]",
                    "Demuestra que ({a}+{b}i)² = {c}+{d}i",
                    "Resuelve la desigualdad: {a}x² + {b}x + {c} > 0"
                ]
            }
            # Agregar más temas...
        }
    
    def generate_exercise(self) -> Dict:
        """Generar ejercicio adaptativo"""
        templates = self.problem_templates.get(self.topic, {}).get(self.difficulty, [])
        
        if not templates:
            # Fallback a dificultad más baja
            if self.difficulty.value > 1:
                self.difficulty = Difficulty(self.difficulty.value - 1)
                return self.generate_exercise()
            else:
                return self.generate_fallback_exercise()
        
        template = random.choice(templates)
        
        # Generar valores aleatorios
        values = self.generate_values(template)
        
        # Crear problema
        problem = template.format(**values)
        
        # Calcular respuesta
        solution = self.calculate_solution(template, values)
        
        # Determinar puntos
        points = self.difficulty.value * 10
        
        return {
            'id': f"ex_{random.randint(1000, 9999)}",
            'problem': problem,
            'solution': solution,
            'points': points,
            'difficulty': self.difficulty.name,
            'topic': self.topic,
            'values': values
        }
    
    def generate_values(self, template: str) -> Dict[str, int]:
        """Generar valores para el template"""
        values = {}
        
        # Extraer variables del template
        import re
        variables = re.findall(r'\{(\w+)\}', template)
        
        for var in variables:
            if var == 'a' or var == 'b' or var == 'c' or var == 'd':
                values[var] = random.randint(1, 20)
            elif var == 'p':
                values[var] = random.randint(5, 50)  # Porcentaje
            elif var == 'n':
                values[var] = random.randint(50, 500)
            elif var == 'lista':
                values[var] = [random.randint(1, 100) for _ in range(5)]
            else:
                values[var] = random.randint(1, 100)
        
        return values
    
    def calculate_solution(self, template: str, values: Dict) -> str:
        """Calcular solución del problema"""
        try:
            # Evaluar expresión matemática
            if ' + ' in template and '?' in template:
                # Suma simple
                a = values.get('a', 0)
                b = values.get('b', 0)
                return str(a + b)
            elif ' - ' in template:
                # Resta
                a = values.get('a', 0)
                b = values.get('b', 0)
                return str(a - b)
            elif ' × ' in template:
                # Multiplicación
                a = values.get('a', 0)
                b = values.get('b', 0)
                return str(a * b)
            elif ' ÷ ' in template:
                # División
                a = values.get('a', 0)
                b = values.get('b', 1)
                if b == 0:
                    b = 1
                return str(round(a / b, 2))
            elif '%' in template:
                # Porcentaje
                p = values.get('p', 0)
                n = values.get('n', 0)
                return str(round(n * p / 100, 2))
            elif 'x' in template and '=' in template:
                # Ecuación lineal
                a = values.get('a', 1)
                b = values.get('b', 0)
                c = values.get('c', 0)
                if a == 0:
                    a = 1
                return str(round((c - b) / a, 2))
            
            # Para otros casos, devolver placeholder
            return "[Solución calculada]"
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    def generate_fallback_exercise(self) -> Dict:
        """Generar ejercicio de fallback"""
        return {
            'id': 'fallback_001',
            'problem': 'Calcula: 2 + 2',
            'solution': '4',
            'points': 10,
            'difficulty': 'EASY',
            'topic': 'aritmetica',
            'values': {'a': 2, 'b': 2}
        }
    
    def check_answer(self, exercise: Dict, user_answer: str) -> Tuple[bool, str]:
        """Verificar respuesta del usuario"""
        try:
            user_value = float(user_answer)
            correct_value = float(exercise['solution'])
            
            # Permitir margen de error pequeño
            if abs(user_value - correct_value) < 0.001:
                return True, "¡Respuesta correcta!"
            else:
                return False, f"La respuesta correcta es {exercise['solution']}"
                
        except ValueError:
            # Comparación de texto
            if user_answer.strip() == exercise['solution'].strip():
                return True, "¡Respuesta correcta!"
            else:
                return False, f"La respuesta correcta es {exercise['solution']}"
    
    def get_hint(self, exercise: Dict) -> str:
        """Obtener pista para el ejercicio"""
        hints = {
            'aritmetica': [
                "Recuerda el orden de las operaciones (PEMDAS)",
                "Verifica que estés usando los números correctos",
                "Haz los cálculos paso a paso",
                "Revisa las unidades si las hay"
            ],
            'algebra': [
                "Aísla la variable en un lado de la ecuación",
                "Realiza la misma operación en ambos lados",
                "Verifica tu respuesta sustituyendo",
                "Simplifica antes de resolver"
            ],
            'geometria': [
                "Dibuja la figura si es posible",
                "Identifica las fórmulas necesarias",
                "Asegúrate de usar las unidades correctas",
                "Verifica que todos los datos estén en la misma unidad"
            ]
        }
        
        topic_hints = hints.get(self.topic, ["Analiza el problema paso a paso"])
        return random.choice(topic_hints)