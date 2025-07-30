"""
Gerador de resumos usando OpenAI
Substitui a funcionalidade de IA do aplicativo original
"""

import openai
from typing import Optional, Dict, Any
import time

class AISummarizer:
    def __init__(self):
        self.client = None
        self.last_request_time = 0
        self.min_request_interval = 1.0  # Mínimo 1 segundo entre requests
        
    def set_api_key(self, api_key: str):
        """Define a chave da API OpenAI"""
        try:
            self.client = openai.OpenAI(api_key=api_key.strip())
            return True
        except Exception as e:
            print(f"Erro ao configurar OpenAI: {e}")
            return False
            
    def generate_summary(self, text: str, api_key: str, language: str = 'pt') -> str:
        """Gera resumo do texto usando OpenAI"""
        if not api_key or not api_key.strip():
            raise ValueError("Chave da API OpenAI é obrigatória")
            
        # Configurar cliente se necessário
        if not self.client:
            if not self.set_api_key(api_key):
                raise ValueError("Chave da API OpenAI inválida")
                
        # Limitar texto se muito longo (modelo tem limite de tokens)
        max_chars = 8000  # Aproximadamente 2000 tokens
        if len(text) > max_chars:
            text = text[:max_chars] + "..."
            
        # Rate limiting simples
        current_time = time.time()
        if current_time - self.last_request_time < self.min_request_interval:
            time.sleep(self.min_request_interval - (current_time - self.last_request_time))
            
        try:
            # Definir prompts baseado no idioma
            system_prompts = {
                'pt': "Você é um assistente útil que cria resumos concisos e informativos de capítulos de livros. Foque nos pontos principais, conceitos-chave e detalhes importantes. Mantenha os resumos entre 2-4 parágrafos. Responda sempre em português brasileiro.",
                'en': "You are a helpful assistant that creates concise, informative summaries of book chapters. Focus on the main points, key concepts, and important details. Keep summaries between 2-4 paragraphs.",
                'es': "Eres un asistente útil que crea resúmenes concisos e informativos de capítulos de libros. Enfócate en los puntos principales, conceptos clave y detalles importantes. Mantén los resúmenes entre 2-4 párrafos."
            }
            
            user_prompts = {
                'pt': f"Por favor, forneça um resumo do seguinte conteúdo de capítulo:\n\n{text}",
                'en': f"Please provide a summary of the following chapter content:\n\n{text}",
                'es': f"Por favor, proporciona un resumen del siguiente contenido de capítulo:\n\n{text}"
            }
            
            system_prompt = system_prompts.get(language, system_prompts['pt'])
            user_prompt = user_prompts.get(language, user_prompts['pt'])
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=400,
                temperature=0.7,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
            
            self.last_request_time = time.time()
            
            summary = response.choices[0].message.content
            if not summary or summary.strip() == '':
                return "Não foi possível gerar resumo."
                
            return summary.strip()
            
        except openai.AuthenticationError:
            raise ValueError("Chave da API OpenAI inválida. Verifique sua chave nas configurações.")
        except openai.RateLimitError:
            raise ValueError("Limite de taxa da API OpenAI excedido. Tente novamente em alguns minutos.")
        except openai.APIConnectionError:
            raise ValueError("Erro de conexão com a API OpenAI. Verifique sua conexão com a internet.")
        except Exception as e:
            error_msg = str(e)
            if "insufficient_quota" in error_msg.lower():
                raise ValueError("Cota da API OpenAI excedida. Verifique sua conta OpenAI.")
            elif "invalid_api_key" in error_msg.lower():
                raise ValueError("Chave da API OpenAI inválida. Verifique sua chave nas configurações.")
            else:
                raise ValueError(f"Erro na API OpenAI: {error_msg}")
                
    def generate_summary_async(self, text: str, api_key: str, callback, language: str = 'pt'):
        """Gera resumo de forma assíncrona"""
        import threading
        
        def _generate():
            try:
                summary = self.generate_summary(text, api_key, language)
                callback(summary, None)
            except Exception as e:
                callback(None, str(e))
                
        thread = threading.Thread(target=_generate, daemon=True)
        thread.start()
        
    def test_api_key(self, api_key: str) -> Dict[str, Any]:
        """Testa se a chave da API está funcionando"""
        try:
            if not self.set_api_key(api_key):
                return {"success": False, "error": "Falha ao configurar cliente OpenAI"}
                
            # Fazer uma requisição simples para testar
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": "Teste"}
                ],
                max_tokens=5,
                temperature=0.0
            )
            
            return {"success": True, "message": "Chave da API válida"}
            
        except openai.AuthenticationError:
            return {"success": False, "error": "Chave da API inválida"}
        except openai.RateLimitError:
            return {"success": False, "error": "Limite de taxa excedido"}
        except Exception as e:
            return {"success": False, "error": f"Erro: {str(e)}"}
            
    def get_supported_languages(self) -> Dict[str, str]:
        """Retorna idiomas suportados para resumo"""
        return {
            'pt': 'Português',
            'en': 'English',
            'es': 'Español'
        }
        
    def estimate_cost(self, text: str) -> Dict[str, Any]:
        """Estima custo aproximado da requisição"""
        # Estimativa aproximada baseada em GPT-3.5-turbo pricing
        chars_per_token = 4  # Aproximação
        input_tokens = len(text) / chars_per_token
        output_tokens = 400  # Max tokens configurado
        
        # Preços aproximados (podem mudar)
        input_cost_per_1k = 0.0015  # USD
        output_cost_per_1k = 0.002   # USD
        
        input_cost = (input_tokens / 1000) * input_cost_per_1k
        output_cost = (output_tokens / 1000) * output_cost_per_1k
        total_cost = input_cost + output_cost
        
        return {
            'input_tokens': int(input_tokens),
            'output_tokens': output_tokens,
            'total_tokens': int(input_tokens + output_tokens),
            'estimated_cost_usd': round(total_cost, 6),
            'estimated_cost_brl': round(total_cost * 5.5, 4)  # Conversão aproximada
        }