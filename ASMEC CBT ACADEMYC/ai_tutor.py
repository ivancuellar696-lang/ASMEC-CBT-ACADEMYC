import json
import random
from typing import List, Dict, Optional
from datetime import datetime
import openai  # Para integración con GPT (opcional)

class MathTutorAI:
    """Tutor AI inteligente para matemáticas"""
    
    def __init__(self, use_openai: bool = False):
        self.use_openai = use_openai
        self.user_profiles = {}
        self.knowledge_base = self.load_knowledge_base()
        
        if use_openai:
            self.setup_openai()
    
    def setup_openai(self):
        """Configurar API de OpenAI"""
        try:
            openai.api_key = "TU_API_KEY_AQUI"  # Cambiar por tu API key
        except:
            print("OpenAI no configurado, usando respuestas locales")
            self.use_openai = False
    
    def load_knowledge_base(self) -> Dict:
        """Cargar base de conocimiento matemático"""
        return {
            'aritmetica': {
                'concepts': [
                    'operaciones_basicas',
                    'fracciones', 
                    'decimales',
                    'porcentajes',
                    'potencias',
                    'raices'
                ],
                'difficulty_levels': {
                    'basico': ['suma', 'resta', 'multiplicacion', 'division'],
                    'intermedio': ['fracciones', 'decimales', 'porcentajes'],
                    'avanzado': ['potencias', 'raices', 'logaritmos']
                }
            },
            'algebra': {
                'concepts': [
                    'ecuaciones_lineales',
                    'sistemas_ecuaciones',
                    'polinomios',
                    'factorizacion',
                    'funciones',
                    'inecuaciones'
                ]
            },
            # Agregar más temas...
        }
    
    def get_daily_recommendation(self, user_id: int) -> str:
        """Generar recomendación diaria personalizada"""
        user_profile = self.get_user_profile(user_id)
        
        # Analizar áreas débiles
        weak_areas = self.identify_weak_areas(user_profile)
        
        # Seleccionar tema para recomendar
        if weak_areas:
            topic = random.choice(weak_areas)
            recommendation = self.generate_topic_recommendation(topic, user_profile)
        else:
            # Recomendar algo nuevo basado en progreso
            next_topic = self.predict_next_topic(user_profile)
            recommendation = f"Te recomendamos aprender sobre {next_topic} para avanzar al siguiente nivel."
        
        return recommendation
    
    def get_user_profile(self, user_id: int) -> Dict:
        """Obtener perfil del usuario"""
        if user_id not in self.user_profiles:
            # Crear perfil inicial
            self.user_profiles[user_id] = {
                'level': 1,
                'strengths': [],
                'weaknesses': [],
                'learning_style': self.detect_learning_style(user_id),
                'progress_history': [],
                'last_topics': [],
                'preferred_difficulty': 'intermedio'
            }
        
        return self.user_profiles[user_id]
    
    def detect_learning_style(self, user_id: int) -> str:
        """Detectar estilo de aprendizaje del usuario"""
        # Implementar detección basada en interacciones
        styles = ['visual', 'auditivo', 'kinestesico', 'lectura_escritura']
        return random.choice(styles)
    
    def identify_weak_areas(self, user_profile: Dict) -> List[str]:
        """Identificar áreas débiles del usuario"""
        # Basado en historial de errores
        weak_areas = []
        
        # Agregar lógica de identificación
        if user_profile.get('error_rate', {}).get('aritmetica', 0) > 0.3:
            weak_areas.append('aritmetica')
        if user_profile.get('error_rate', {}).get('algebra', 0) > 0.4:
            weak_areas.append('algebra')
        
        return weak_areas
    
    def generate_topic_recommendation(self, topic: str, user_profile: Dict) -> str:
        """Generar recomendación específica para un tema"""
        recommendations = {
            'aritmetica': [
                "Practica ejercicios de operaciones combinadas para fortalecer tus bases aritméticas.",
                "Te sugerimos revisar fracciones equivalentes, es fundamental para álgebra.",
                "Los porcentajes son esenciales para la vida diaria, practica con ejercicios reales."
            ],
            'algebra': [
                "Domina las ecuaciones lineales antes de pasar a sistemas más complejos.",
                "La factorización es clave para simplificar expresiones algebraicas.",
                "Practica la resolución de problemas con ecuaciones para mejorar tu pensamiento lógico."
            ],
            'geometria': [
                "Comienza con el cálculo de áreas y perímetros de figuras básicas.",
                "Los teoremas de triángulos son fundamentales para geometría avanzada.",
                "Visualiza los problemas geométricos, te ayudará a comprender mejor."
            ]
        }
        
        topic_recs = recommendations.get(topic, [
            "Continúa practicando para mejorar tus habilidades."
        ])
        
        # Personalizar según estilo de aprendizaje
        learning_style = user_profile.get('learning_style', 'visual')
        style_suggestions = {
            'visual': "Intenta dibujar o visualizar el problema.",
            'auditivo': "Explica el problema en voz alta paso a paso.",
            'kinestesico': "Usa objetos físicos para representar el problema.",
            'lectura_escritura': "Escribe cada paso detalladamente."
        }
        
        recommendation = random.choice(topic_recs)
        style_suggestion = style_suggestions.get(learning_style, "")
        
        return f"{recommendation} {style_suggestion}"
    
    def predict_next_topic(self, user_profile: Dict) -> str:
        """Predecir siguiente tema a aprender"""
        completed_topics = user_profile.get('completed_topics', [])
        current_level = user_profile.get('level', 1)
        
        # Lógica de predicción basada en progreso
        if current_level == 1:
            if 'aritmetica' not in completed_topics:
                return 'Aritmética básica'
            else:
                return 'Introducción al álgebra'
        elif current_level == 2:
            if 'algebra_basica' not in completed_topics:
                return 'Ecuaciones lineales'
            else:
                return 'Geometría plana'
        else:
            # Niveles avanzados
            advanced_topics = ['Trigonometría', 'Cálculo diferencial', 'Estadística']
            for topic in advanced_topics:
                if topic.lower() not in completed_topics:
                    return topic
        
        return 'Repaso general'
    
    def get_topic_help(self, topic: str, user_id: int) -> str:
        """Obtener ayuda personalizada para un tema"""
        user_profile = self.get_user_profile(user_id)
        
        if self.use_openai:
            return self.get_openai_help(topic, user_profile)
        else:
            return self.get_local_help(topic, user_profile)
    
    def get_openai_help(self, topic: str, user_profile: Dict) -> str:
        """Obtener ayuda de OpenAI"""
        try:
            prompt = self.create_help_prompt(topic, user_profile)
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres un tutor de matemáticas paciente y claro."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error con OpenAI: {e}")
            return self.get_local_help(topic, user_profile)
    
    def get_local_help(self, topic: str, user_profile: Dict) -> str:
        """Obtener ayuda local (sin internet)"""
        help_responses = {
            'ecuaciones': [
                "Recuerda: lo que hagas de un lado de la ecuación, debes hacerlo del otro.",
                "Para despejar una variable, usa operaciones inversas.",
                "Siempre verifica tu solución sustituyendo en la ecuación original."
            ],
            'fracciones': [
                "Para sumar fracciones, primero encuentra un denominador común.",
                "Multiplicar fracciones es directo: numerador × numerador, denominador × denominador.",
                "Dividir fracciones es lo mismo que multiplicar por el recíproco."
            ],
            'geometria': [
                "Dibuja siempre la figura para visualizar mejor el problema.",
                "Recuerda las fórmulas de áreas y perímetros de figuras básicas.",
                "Usa el teorema de Pitágoras para triángulos rectángulos."
            ]
        }
        
        # Buscar ayuda específica para el tema
        for key, responses in help_responses.items():
            if key in topic.lower():
                return random.choice(responses)
        
        # Respuesta genérica
        return "Analiza el problema paso a paso. Identifica qué te piden y qué datos tienes disponible."
    
    def create_help_prompt(self, topic: str, user_profile: Dict) -> str:
        """Crear prompt para OpenAI"""
        level = user_profile.get('level', 1)
        learning_style = user_profile.get('learning_style', 'visual')
        
        prompt = f"""
        Eres un tutor de matemáticas ayudando a un estudiante de nivel {level}.
        
        Tema que necesita ayuda: {topic}
        Estilo de aprendizaje del estudiante: {learning_style}
        
        Proporciona una explicación clara y paso a paso sobre este tema.
        Incluye ejemplos relevantes y consejos prácticos.
        Adapta tu explicación al estilo de aprendizaje mencionado.
        
        Explicación:
        """
        
        return prompt
    
    def generate_faq(self, topic: str, limit: int = 3) -> List[tuple]:
        """Generar preguntas frecuentes sobre un tema"""
        faq_database = {
            'algebra': [
                ("¿Qué es una ecuación?", "Una igualdad entre dos expresiones algebraicas."),
                ("¿Cómo se resuelve una ecuación lineal?", "Aislando la variable usando operaciones inversas."),
                ("¿Qué es la factorización?", "Expresar una expresión como producto de factores.")
            ],
            'geometria': [
                ("¿Qué es el perímetro?", "Suma de las longitudes de los lados de una figura."),
                ("¿Cómo se calcula el área de un triángulo?", "Base por altura dividido entre 2."),
                ("¿Qué es el teorema de Pitágoras?", "En un triángulo rectángulo: a² + b² = c²")
            ],
            'aritmetica': [
                ("¿Cómo se suman fracciones?", "Con denominador común: a/b + c/d = (ad + bc)/bd"),
                ("¿Qué es un porcentaje?", "Una fracción de 100 partes."),
                ("¿Cómo se calcula un descuento?", "Precio original × (porcentaje/100)")
            ]
        }
        
        # Buscar FAQ para el tema
        for key, faqs in faq_database.items():
            if key in topic.lower():
                return faqs[:limit]
        
        # FAQ genéricos
        return [
            ("¿Por qué es importante este tema?", "Es fundamental para temas más avanzados."),
            ("¿Cómo puedo practicar?", "Resolviendo ejercicios variados y verificando tus respuestas."),
            ("¿Qué hago si no entiendo?", "Divide el problema en partes más pequeñas y pide ayuda.")
        ]
    
    def get_test_recommendations(self, test_score: float, weak_areas: List[str]) -> str:
        """Generar recomendaciones basadas en resultados de test"""
        if test_score >= 90:
            return "¡Excelente trabajo! Tu comprensión es sólida. Te recomendamos avanzar al siguiente nivel o explorar temas más desafiantes."
        elif test_score >= 70:
            return "Buen trabajo. Tienes una base sólida pero hay áreas para mejorar. Enfócate en practicar los temas donde tuviste dificultades."
        else:
            recommendations = []
            
            if weak_areas:
                recs = "Te recomendamos especialmente practicar:\n"
                for area in weak_areas[:3]:  # Máximo 3 áreas
                    recs += f"• {area.capitalize()}\n"
                recommendations.append(recs)
            
            recommendations.append("No te desanimes. Las matemáticas requieren práctica constante. Vuelve a revisar los conceptos básicos y practica con ejercicios graduales.")
            
            return "\n".join(recommendations)
    
    def explain_concept(self, concept: str, user_id: int) -> str:
        """Explicar un concepto matemático"""
        user_profile = self.get_user_profile(user_id)
        
        explanations = {
            'derivada': "La derivada representa la tasa de cambio instantánea de una función.",
            'integral': "La integral representa el área bajo la curva de una función.",
            'matriz': "Una matriz es un arreglo rectangular de números organizados en filas y columnas.",
            'probabilidad': "La probabilidad mide la posibilidad de que ocurra un evento."
        }
        
        explanation = explanations.get(concept.lower())
        
        if explanation:
            # Personalizar según nivel
            level = user_profile.get('level', 1)
            if level == 1:
                explanation += " Es un concepto básico importante para temas avanzados."
            elif level >= 3:
                explanation += " Este concepto se aplica en muchos campos como física, economía e ingeniería."
            
            return explanation
        
        return f"El concepto '{concept}' es importante en matemáticas. Te sugiero investigar más sobre él o pedir ayuda específica."

class ExplanationGenerator:
    """Generador de explicaciones paso a paso"""
    
    def generate_step_by_step(self, problem: str, solution: str) -> List[str]:
        """Generar explicación paso a paso"""
        steps = []
        
        # Analizar tipo de problema
        if 'x' in problem and '=' in problem:
            steps = self.generate_algebra_steps(problem, solution)
        elif '+' in problem or '-' in problem or '×' in problem or '÷' in problem:
            steps = self.generate_arithmetic_steps(problem, solution)
        elif 'área' in problem.lower() or 'perímetro' in problem.lower():
            steps = self.generate_geometry_steps(problem, solution)
        else:
            steps = ["Lee el problema cuidadosamente.",
                    "Identifica qué te piden encontrar.",
                    "Escribe los datos conocidos.",
                    "Aplica la fórmula o método apropiado.",
                    "Verifica tu respuesta."]
        
        return steps
    
    def generate_algebra_steps(self, problem: str, solution: str) -> List[str]:
        """Generar pasos para problema algebraico"""
        steps = [
            f"1. Problema: {problem}",
            "2. Identifica la variable a despejar (normalmente x)",
            "3. Aplica operaciones inversas para aislar la variable",
            "4. Realiza la misma operación en ambos lados de la ecuación",
            "5. Simplifica la expresión",
            f"6. Solución: {solution}",
            "7. Verifica sustituyendo la solución en la ecuación original"
        ]
        return steps
    
    def generate_arithmetic_steps(self, problem: str, solution: str) -> List[str]:
        """Generar pasos para problema aritmético"""
        steps = [
            f"1. Problema: {problem}",
            "2. Identifica la operación principal",
            "3. Realiza las operaciones en el orden correcto (PEMDAS)",
            "4. Trabaja paso a paso, sin saltos",
            f"5. Solución: {solution}",
            "6. Verifica con cálculo inverso"
        ]
        return steps
    
    def generate_geometry_steps(self, problem: str, solution: str) -> List[str]:
        """Generar pasos para problema geométrico"""
        steps = [
            f"1. Problema: {problem}",
            "2. Dibuja la figura si es posible",
            "3. Identifica las fórmulas necesarias",
            "4. Sustituye los valores conocidos",
            "5. Realiza los cálculos",
            f"6. Solución: {solution}",
            "7. Incluye las unidades correctas"
        ]
        return steps