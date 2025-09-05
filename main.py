#!/usr/bin/env python3
"""
Bot do Discord melhorado com arquitetura modular
"""

import asyncio
import logging
from bot.core.bot import DiscordBot
from bot.config import load_config

def setup_logging():
    """Configura o sistema de logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('bot.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

async def main():
    """Função principal do bot"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Carrega a configuração
        config = load_config()
        
        # Inicializa o bot
        bot = DiscordBot(config)
        
        logger.info("🚀 Iniciando bot do Discord...")
        await bot.start()
        
    except KeyboardInterrupt:
        logger.info("⏹️ Bot interrompido pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")
    finally:
        logger.info("🛑 Bot finalizado")

if __name__ == "__main__":
    asyncio.run(main())