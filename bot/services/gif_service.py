"""
Serviço para buscar GIFs do Tenor
"""
import logging
import requests
from typing import Optional

logger = logging.getLogger(__name__)

class GifService:
    """Serviço para buscar GIFs usando a API Tenor"""
    
    def __init__(self, api_key: Optional[str]):
        self.api_key = api_key
        self.base_url = "https://tenor.googleapis.com/v2/search"
        
        if not api_key:
            logger.warning("⚠️ TENOR_API_KEY não fornecida - funcionalidade de GIF desabilitada")
        else:
            logger.info("✅ Serviço GIF inicializado")
    
    async def search_gif(self, query: str, limit: int = 1) -> Optional[str]:
        """
        Busca GIF pelo termo especificado
        """
        if not self.api_key:
            logger.warning("⚠️ Tentativa de buscar GIF sem API key")
            return None
        
        try:
            params = {
                "q": query,
                "key": self.api_key,
                "limit": limit,
                "media_filter": "gif"
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = data.get("results", [])
            
            if results:
                gif_url = results[0]["media_formats"]["gif"]["url"]
                logger.info(f"✅ GIF encontrado para: {query}")
                return gif_url
            else:
                logger.info(f"ℹ️ Nenhum GIF encontrado para: {query}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"❌ Erro na requisição Tenor: {e}")
            return None
        except KeyError as e:
            logger.error(f"❌ Formato de resposta inesperado do Tenor: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Erro inesperado ao buscar GIF: {e}")
            return None
    
    def is_available(self) -> bool:
        """Verifica se o serviço está disponível"""
        return self.api_key is not None