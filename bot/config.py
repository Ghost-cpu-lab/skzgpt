"""
Configurações do bot
"""
import os
import logging
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

@dataclass
class BotConfig:
    """Configurações do bot"""
    discord_token: str
    groq_api_key: str
    tenor_api_key: Optional[str] = None
    log_channel_id: Optional[int] = None
    command_prefix: str = "!"
    
    def __post_init__(self):
        """Validação das configurações"""
        if not self.discord_token:
            raise ValueError("DISCORD_TOKEN é obrigatório")
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY é obrigatório")

def load_config() -> BotConfig:
    """Carrega as configurações do arquivo .env"""
    load_dotenv()
    
    try:
        config = BotConfig(
            discord_token=os.getenv("DISCORD_TOKEN", ""),
            groq_api_key=os.getenv("GROQ_API_KEY", ""),
            tenor_api_key=os.getenv("TENOR_API_KEY"),
            log_channel_id=int(os.getenv("LOG_CHANNEL_ID", "0")) or None,
            command_prefix=os.getenv("COMMAND_PREFIX", "!")
        )
        
        logger.info("✅ Configurações carregadas com sucesso")
        return config
        
    except ValueError as e:
        logger.error(f"❌ Erro na configuração: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Erro inesperado ao carregar configuração: {e}")
        raise