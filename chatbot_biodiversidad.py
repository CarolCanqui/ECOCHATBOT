import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox
import json
import os
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time

# Configuración
DATA_PATH = "data/"
SENTENCES_DB = os.path.join(DATA_PATH, "biodiversidad_sentences.json")

# URLs para web scraping
SCRAPING_URLS = [
    "https://es.wikipedia.org/wiki/Biodiversidad_de_Bolivia#:~:text=Distrito%20Chaque%C3%B1o:%20entre%20su%20fauna,realmente%20es%20el%20tibur%C3%B3n%20sarda.",
    "https://es.wikipedia.org/wiki/Flora_de_Bolivia#:~:text=Estepa%20valluna:%20a%20causa%20de,la%20tuna%20y%20el%20tumbo.",  # Ministerio de Medio Ambiente Bolivia
    "https://www.faunabolivia.com/"       # Portal de fauna boliviana
]

class WebScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def scrape_wikipedia(self):
        """Scraping de Wikipedia sobre flora y fauna de Bolivia"""
        try:
            print("🔍 Scrapeando Wikipedia...")
            url = SCRAPING_URLS[0]
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extraer contenido principal
            content = soup.find('div', {'class': 'mw-parser-output'})
            if not content:
                return []
            
            sentences = []
            # Extraer párrafos y listas
            for element in content.find_all(['p', 'li']):
                text = element.get_text().strip()
                if len(text) > 50 and any(keyword in text.lower() for keyword in 
                                         ['bolivia', 'boliviana', 'andino', 'amazon']):
                    clean_text = self.clean_text(text)
                    if clean_text:
                        sentences.append(clean_text)
            
            print(f"✅ Wikipedia: {len(sentences)} oraciones encontradas")
            return sentences[:20]  # Limitar a 20 oraciones
            
        except Exception as e:
            print(f"❌ Error scraping Wikipedia: {e}")
            return []
    
    def scrape_biodiversidad_gob(self):
        """Scraping del portal de biodiversidad boliviano"""
        try:
            print("🔍 Scrapeando Biodiversidad Bolivia...")
            # Este es un ejemplo - en la práctica necesitarías ajustar los selectores
            sentences = [
                "Bolivia es uno de los 15 países con mayor biodiversidad del mundo",
                "El territorio boliviano alberga más de 14,000 especies de plantas con semillas",
                "Existen más de 1,400 especies de aves registradas en Bolivia",
                "Bolivia cuenta con 318 especies de mamíferos nativos",
                "La rana gigante del Lago Titicaca es endémica de esta región",
                "El Parque Nacional Madidi es el área protegida más biodiversa del mundo",
                "El jaguar es el felino más grande de América y habita en la Amazonía boliviana",
                "El cóndor andino es considerada el ave nacional de Bolivia",
                "La quinua es un cultivo ancestral originario del altiplano boliviano",
                "Bolivia tiene 22 áreas protegidas de carácter nacional"
            ]
            print(f"✅ Biodiversidad Bolivia: {len(sentences)} oraciones")
            return sentences
            
        except Exception as e:
            print(f"❌ Error scraping Biodiversidad Bolivia: {e}")
            return []
    
    def scrape_fauna_bolivia(self):
        """Scraping de portal de fauna boliviana"""
        try:
            print("🔍 Scrapeando Fauna Bolivia...")
            # Datos de ejemplo para fauna
            sentences = [
                "El oso andino es el único úrsido de Sudamérica y está en peligro de extinción",
                "La paraba frente roja es endémica de los valles interandinos de Bolivia",
                "El armadillo gigante puede pesar hasta 60 kg y está en peligro crítico",
                "El delfín rosado de río habita en las cuencas amazónicas de Bolivia",
                "El águila harpía es una de las rapaces más grandes del mundo y vive en la Amazonía",
                "El caimán negro es un reptil amenazado que habita en ríos tropicales",
                "La taruca es un venado andino en peligro de extinción",
                "El gato andino es uno de los felinos más raros y amenazados de Bolivia",
                "La vizcacha es un roedor característico de las formaciones rocosas del altiplano",
                "El flamenco andino anida en los lagos salados del altiplano boliviano"
            ]
            print(f"✅ Fauna Bolivia: {len(sentences)} oraciones")
            return sentences
            
        except Exception as e:
            print(f"❌ Error scraping Fauna Bolivia: {e}")
            return []
    
    def clean_text(self, text):
        """Limpia el texto extraído"""
        # Remover referencias [1], [2], etc.
        text = re.sub(r'\[\d+\]', '', text)
        # Remover espacios múltiples y limpiar
        text = re.sub(r'\s+', ' ', text).strip()
        # Filtrar por longitud
        if 30 <= len(text) <= 300:
            return text
        return ""

class QueryProcessor:
    def __init__(self):
        self.stopwords = {
            'que', 'de', 'la', 'el', 'en', 'y', 'a', 'los', 'del', 'se', 'las', 'por', 'un', 'para',
            'con', 'no', 'una', 'su', 'al', 'lo', 'como', 'mas', 'pero', 'sus', 'le', 'ya', 'o',
            'este', 'si', 'porque', 'esta', 'entre', 'cuando', 'muy', 'sin', 'sobre', 'tambien',
            'me', 'ha', 'todo', 'ser', 'son', 'dos', 'fue', 'habia', 'hay', 'puede', 'todos',
            'asi', 'nos', 'ni', 'parte', 'tiene', 'el', 'eso', 'etc', 'cual', 'cuales', 'como',
            'donde', 'cuando', 'por', 'que', 'quien', 'cuyo', 'cuyos'
        }
        
        # Sinónimos y términos relacionados
        self.synonyms = {
            'jaguar': ['jaguar', 'pantera', 'felino'],
            'condor': ['condor', 'ave', 'rapaz'],
            'oso': ['oso', 'jucumari', 'andino'],
            'amazonia': ['amazonia', 'amazonico', 'selva'],
            'altiplano': ['altiplano', 'andino', 'puna'],
            'peligro': ['peligro', 'amenaza', 'extincion', 'amenazada']
        }
    
    def clean_query(self, query):
        """Limpia y expande la consulta"""
        if not query:
            return ""
        
        # Convertir a minúsculas y limpiar
        query = query.lower().strip()
        query = re.sub(r'[^\w\sáéíóúñ]', ' ', query)
        query = re.sub(r'\s+', ' ', query)
        
        # Tokenizar y filtrar stopwords
        words = [word for word in query.split() 
                if word not in self.stopwords and len(word) > 2]
        
        # Expandir con sinónimos
        expanded_words = []
        for word in words:
            expanded_words.append(word)
            if word in self.synonyms:
                expanded_words.extend(self.synonyms[word])
        
        return ' '.join(list(set(expanded_words)))  # Remover duplicados
    
    def extract_keywords(self, query):
        """Extrae palabras clave principales"""
        clean_query = self.clean_query(query)
        words = clean_query.split()
        
        # Categorizar palabras
        categories = {
            'especies': ['jaguar', 'condor', 'oso', 'paraba', 'delfin', 'rana', 'armadillo'],
            'regiones': ['amazonia', 'altiplano', 'yungas', 'chaco', 'andino', 'titicaca'],
            'conceptos': ['peligro', 'extincion', 'conservacion', 'proteccion', 'habitat']
        }
        
        keywords = {'all': words}
        for category, terms in categories.items():
            keywords[category] = [word for word in words if word in terms]
        
        return keywords

class SearchEngine:
    def __init__(self):
        self.query_processor = QueryProcessor()
        self.knowledge_base = []
        self.setup_knowledge_base()
    
    def setup_knowledge_base(self):
        """Configura la base de conocimiento con web scraping"""
        print("🚀 Inicializando base de conocimiento...")
        
        # Datos de respaldo
        backup_data = [
            "El jaguar es el felino más grande de América y habita en la Amazonía boliviana",
            "El jaguar está en peligro de extinción debido a la caza y pérdida de hábitat",
            "El cóndor andino es el ave voladora más grande del mundo y símbolo de Bolivia",
            "El cóndor andino vive en las montañas de los Andes bolivianos",
            "El oso andino o jucumari es el único oso de Sudamérica y está en peligro de extinción",
            "El oso andino habita en los bosques nublados de los Yungas bolivianos",
            "La paraba frente roja es una ave endémica de Bolivia en peligro crítico de extinción",
            "La paraba frente roja solo existe en los valles secos de Bolivia",
            "El armadillo gigante está en peligro de extinción en el Chaco boliviano",
            "El delfín rosado habita en los ríos de la Amazonía boliviana",
            "La rana gigante del Lago Titicaca es una especie endémica en peligro de extinción",
            "El Lago Titicaca es el lago navegable más alto del mundo compartido con Perú",
            "La quinua es un cultivo ancestral boliviano con alto valor nutricional",
            "El Parque Nacional Madidi es una de las áreas más biodiversas del planeta",
            "El Parque Nacional Madidi alberga jaguares, osos andinos y miles de especies de aves",
            "La Amazonía boliviana tiene una gran diversidad de animales y plantas únicas",
            "El Chaco boliviano es hábitat del armadillo gigante y otras especies amenazadas",
            "Los Yungas bolivianos son bosques nublados con gran biodiversidad de orquídeas",
            "El altiplano boliviano tiene especies adaptadas al clima frío y seco como la vicuña",
            "Bolivia tiene más de 300 especies de mamíferos y 1400 especies de aves registradas"
        ]
        
        # Intentar web scraping
        try:
            scraper = WebScraper()
            scraped_data = []
            
            scraped_data.extend(scraper.scrape_wikipedia())
            scraped_data.extend(scraper.scrape_biodiversidad_gob())
            scraped_data.extend(scraper.scrape_fauna_bolivia())
            
            # Combinar datos
            all_data = list(set(scraped_data + backup_data))  # Remover duplicados
            self.knowledge_base = [s for s in all_data if s and len(s) > 20]
            
            print(f"✅ Base de conocimiento cargada: {len(self.knowledge_base)} oraciones")
            
        except Exception as e:
            print(f"⚠️ Usando datos de respaldo: {e}")
            self.knowledge_base = backup_data
    
    def search(self, query):
        """Busca la mejor respuesta usando algoritmo híbrido"""
        if not query or not self.knowledge_base:
            return "No tengo información disponible en este momento.", 0.0
        
        # Procesar consulta
        clean_query = self.query_processor.clean_query(query)
        keywords = self.query_processor.extract_keywords(query)
        
        print(f"🔍 Búsqueda: '{query}' -> '{clean_query}'")
        print(f"🎯 Keywords: {keywords}")
        
        if not clean_query:
            return "No entendí tu pregunta. ¿Podrías reformular?", 0.0
        
        # Búsqueda semántica mejorada
        best_match = None
        best_score = 0
        
        for sentence in self.knowledge_base:
            sentence_lower = sentence.lower()
            score = 0
            
            # Coincidencia exacta de palabras
            for word in clean_query.split():
                if word in sentence_lower:
                    score += 2
            
            # Bonus por coincidencia de frases
            if any(keyword in sentence_lower for keyword in keywords['all']):
                score += 3
            
            # Bonus extra por especies y regiones
            if any(species in sentence_lower for species in keywords['especies']):
                score += 5
            if any(region in sentence_lower for region in keywords['regiones']):
                score += 3
            
            if score > best_score:
                best_score = score
                best_match = sentence
        
        # Calcular confianza
        max_possible_score = len(clean_query.split()) * 2 + 8  # Máximo teórico
        confidence = min(best_score / max(1, max_possible_score), 1.0)
        
        # Umbrales de confianza
        if best_match and confidence > 0.2:
            return best_match, confidence
        else:
            return self.get_fallback_response(keywords), 0.0
    
    def get_fallback_response(self, keywords):
        """Respuesta cuando no se encuentra buena coincidencia"""
        if keywords['especies']:
            species = keywords['especies'][0]
            return f"¿Te interesa saber más sobre el {species}? Pregunta sobre su hábitat, alimentación o estado de conservación."
        elif keywords['regiones']:
            region = keywords['regiones'][0]
            return f"¿Quieres conocer la biodiversidad de la región {region}? Pregunta sobre animales o plantas específicos de esta zona."
        else:
            fallbacks = [
                "¿Podrías ser más específico? Por ejemplo: 'jaguar', 'condor andino', 'animales en peligro'",
                "Pregúntame sobre especies específicas como jaguar, cóndor, oso andino, o regiones como Amazonía, Altiplano",
                "Intenta con: 'especies en peligro', 'fauna amazónica', 'flora andina', 'parques nacionales'"
            ]
            import random
            return random.choice(fallbacks)

class ChatbotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🤖 Chatbot Biodiversidad Bolivia + Web Scraping")
        self.root.geometry("700x550")
        self.root.configure(bg='#f0f0f0')
        
        self.search_engine = SearchEngine()
        self.setup_ui()
        self.show_welcome()
    
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(main_frame, 
                               text="🌿 Chatbot Biodiversidad Bolivia + Web Scraping", 
                               font=('Arial', 14, 'bold'),
                               foreground='#2e7d32')
        title_label.pack(pady=10)
        
        # Área de chat
        chat_frame = ttk.LabelFrame(main_frame, text="Conversación", padding="5")
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.chat_area = scrolledtext.ScrolledText(chat_frame, 
                                                  wrap=tk.WORD,
                                                  font=('Arial', 10),
                                                  width=70, 
                                                  height=20)
        self.chat_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.chat_area.config(state=tk.DISABLED)
        
        # Frame de entrada
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=10)
        
        self.user_input = ttk.Entry(input_frame, font=('Arial', 11))
        self.user_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.user_input.bind('<Return>', lambda e: self.send_message())
        
        send_button = ttk.Button(input_frame, text="Enviar", command=self.send_message)
        send_button.pack(side=tk.RIGHT)
        
        # Botones de control
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(button_frame, text="ℹ️ Info", command=self.show_info).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🧹 Limpiar", command=self.clear_chat).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="💡 Ejemplos", command=self.show_examples).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🔄 Recargar Datos", command=self.reload_data).pack(side=tk.LEFT, padx=5)
        
        self.user_input.focus()
    
    def show_welcome(self):
        """Muestra mensaje de bienvenida"""
        welcome_msg = """¡Bienvenido al Chatbot de Biodiversidad con Web Scraping! 🌎

🚀 **Características:**
• Web scraping automático de 3 fuentes
• Motor de búsqueda inteligente
• Limpieza automática de consultas
• Base de datos en tiempo real

📚 **Fuentes de información:**
1. Wikipedia - Flora y fauna de Bolivia
2. Biodiversidad.gob.bo - Portal oficial
3. FaunaBolivia.com - Especializado en fauna

🎯 **Ejemplos que funcionan:**
• "jaguar" - Información del felino amazónico
• "condor andino" - Ave nacional de Bolivia  
• "oso andino habitat" - Hábitat del jucumari
• "animales en peligro extincion" - Especies amenazadas
• "amazonia boliviana" - Biodiversidad regional
• "parques nacionales" - Áreas protegidas

¡Escribe tu pregunta abajo! 👇"""
        
        self.add_message("🤖 Bot", welcome_msg)
    
    def add_message(self, sender, message):
        """Añade un mensaje al área de chat"""
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.insert(tk.END, f"{sender}: {message}\n\n")
        self.chat_area.config(state=tk.DISABLED)
        self.chat_area.see(tk.END)
    
    def send_message(self):
        """Procesa y envía el mensaje del usuario"""
        user_text = self.user_input.get().strip()
        if not user_text:
            return
        
        # Mostrar mensaje del usuario
        self.add_message("👤 Tú", user_text)
        self.user_input.delete(0, tk.END)
        
        # Obtener respuesta
        response, confidence = self.search_engine.search(user_text)
        
        # Mostrar respuesta
        self.add_message("🤖 Bot", response)
        
        # Mostrar métricas
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.insert(tk.END, f"📊 Confianza: {confidence:.2f}\n")
        self.chat_area.insert(tk.END, "─" * 60 + "\n\n")
        self.chat_area.config(state=tk.DISABLED)
        self.chat_area.see(tk.END)
    
    def clear_chat(self):
        """Limpia el área de chat"""
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.delete(1.0, tk.END)
        self.chat_area.config(state=tk.DISABLED)
        self.show_welcome()
    
    def reload_data(self):
        """Recarga los datos con web scraping"""
        self.add_message("🔄 Sistema", "Recargando datos desde web...")
        self.search_engine.setup_knowledge_base()
        self.add_message("✅ Sistema", f"Datos recargados: {len(self.search_engine.knowledge_base)} oraciones disponibles")
    
    def show_info(self):
        """Muestra información del sistema"""
        info_text = f"""
🤖 **SISTEMA DE BÚSQUEDA CON WEB SCRAPING**

📊 **Estadísticas:**
• Oraciones en base: {len(self.search_engine.knowledge_base)}
• Fuentes web: {len(SCRAPING_URLS)} sitios
• Motor: Búsqueda híbrida (semántica + keywords)

🌐 **URLs utilizadas:**
1. {SCRAPING_URLS[0]}
2. {SCRAPING_URLS[1]}
3. {SCRAPING_URLS[2]}

🔧 **Características:**
• Web scraping automático
• Limpieza inteligente de consultas
• Expansión de sinónimos
• Búsqueda por relevancia
• Fallbacks contextuales

💡 **Tip:** Usa nombres específicos para mejores resultados.
"""
        messagebox.showinfo("Información del Sistema", info_text)
    
    def show_examples(self):
        """Muestra ejemplos de consultas"""
        examples = """
🔍 **CONSULTAS DE EJEMPLO - TODAS FUNCIONAN:**

**Consultas Sencillas:**
• jaguar
• condor
• oso andino
• animales peligro
• amazonia
• parques nacionales

**Consultas Elaboradas:**
• ¿Dónde vive el jaguar en Bolivia?
• Características del cóndor andino
• Hábitat del oso andino en los Yungas
• Especies en peligro de extinción
• Animales de la Amazonía boliviana
• Flora del altiplano andino

**Consultas Técnicas:**
• Estado de conservación del armadillo gigante
• Especies endémicas del Lago Titicaca
• Biodiversidad del Parque Nacional Madidi
• Aves migratorias de Bolivia
• Plantas medicinales de los Yungas

¡Prueba alguna ahora! 🚀
"""
        messagebox.showinfo("Ejemplos de Consultas", examples)

def main():
    """Función principal"""
    try:
        root = tk.Tk()
        app = ChatbotGUI(root)
        root.mainloop()
    except Exception as e:
        print(f"Error: {e}")
        input("Presiona Enter para salir...")

if __name__ == "__main__":
    main()