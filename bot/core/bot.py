"""
Classe principal do bot do Discord
"""
import logging
import discord
from discord.ext import commands
from typing import Optional

from bot.config import BotConfig
from bot.services.groq_service import GroqService
from bot.services.gif_service import GifService
from bot.commands.chat_commands import ChatCommands
from bot.commands.super_commands import SuperCommands
from bot.handlers.error_handler import ErrorHandler
from bot.handlers.event_handler import EventHandler

logger = logging.getLogger(__name__)

class DiscordBot:
    """Bot principal do Discord"""
    
    def __init__(self, config: BotConfig):
        self.config = config
        
        # Configurar intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.guild_messages = True
        
        # Inicializar bot
        self.bot = commands.Bot(
            command_prefix=config.command_prefix,
            intents=intents,
            help_command=None
        )
        
        # Inicializar serviços
        self.groq_service = GroqService(config.groq_api_key)
        self.gif_service = GifService(config.tenor_api_key) if config.tenor_api_key else None
        
        # Configurar handlers
        self.error_handler = ErrorHandler(self.bot)
        self.event_handler = EventHandler(self.bot, config)
        
        # Registrar comandos
        self._setup_commands()
        
        logger.info("🤖 Bot inicializado com sucesso")
    
    def _setup_commands(self):
        """Configura todos os comandos do bot"""
        
        # Inicializar os comandos de chat uma vez
        self.chat_commands = ChatCommands(
            self.bot, 
            self.groq_service, 
            self.gif_service,
            self.config
        )
        
        @self.bot.tree.command(name="skgpt", description="Chatbot IA com funcionalidades administrativas")
        async def skgpt(interaction: discord.Interaction, mensagem: str):
            """Chatbot IA com funcionalidades administrativas"""
            await self.chat_commands.handle_skgpt(interaction, mensagem)
        
        @self.bot.tree.command(name="gif", description="Busca GIF pelo termo especificado")
        async def gif(interaction: discord.Interaction, termo: str):
            """Busca GIF pelo termo especificado"""
            await self.chat_commands.handle_gif(interaction, termo)
        
        @self.bot.tree.command(name="help", description="Mostra ajuda dos comandos do bot")
        async def help_cmd(interaction: discord.Interaction):
            """Mostra ajuda dos comandos do bot"""
            await self.chat_commands.handle_help(interaction)
        
        # ========== SUPER COMANDOS COM AUTOCOMPLETE VISUAL ==========
        # Os novos comandos são carregados via SuperCommands Cog
        
        logger.info("📝 Comandos básicos registrados")
    
    async def load_super_commands(self):
        """Carrega os super comandos com autocomplete"""
        await self.bot.add_cog(SuperCommands(self.bot, self.groq_service))
        logger.info("✨ Super comandos com autocomplete carregados")
    
    async def start(self):
        """Inicia o bot"""
        try:
            # Carregar super comandos antes de iniciar
            await self.load_super_commands()
            await self.bot.start(self.config.discord_token)
        except discord.LoginFailure:
            logger.error("❌ Token do Discord inválido")
            raise
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar bot: {e}")
            raise
    
    async def close(self):
        """Encerra o bot"""
        await self.bot.close()
        logger.info("🛑 Bot encerrado")