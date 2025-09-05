"""
Handler para eventos do Discord
"""
import logging
import discord
from discord.ext import commands
from bot.config import BotConfig

logger = logging.getLogger(__name__)

class EventHandler:
    """Handler para eventos do Discord"""
    
    def __init__(self, bot: commands.Bot, config: BotConfig):
        self.bot = bot
        self.config = config
        self.setup_events()
        logger.info("✅ Handler de eventos configurado")
    
    def setup_events(self):
        """Configura os eventos do bot"""
        
        @self.bot.event
        async def on_ready():
            await self.on_ready_handler()
        
        @self.bot.event
        async def on_guild_join(guild):
            await self.on_guild_join_handler(guild)
        
        @self.bot.event
        async def on_guild_remove(guild):
            await self.on_guild_remove_handler(guild)
    
    async def on_ready_handler(self):
        """Executado quando o bot fica online"""
        logger.info(f"✅ Bot online como {self.bot.user}")
        logger.info(f"📊 Conectado a {len(self.bot.guilds)} servidor(es)")
        
        # Sincronizar comandos slash
        try:
            synced = await self.bot.tree.sync()
            logger.info(f"🌐 {len(synced)} comandos sincronizados")
        except Exception as e:
            logger.error(f"❌ Erro ao sincronizar comandos: {e}")
    
    async def on_guild_join_handler(self, guild: discord.Guild):
        """Executado quando o bot entra em um servidor"""
        logger.info(f"📈 Bot adicionado ao servidor: {guild.name} ({guild.id})")
        
        # Enviar mensagem de boas-vindas se possível
        if guild.system_channel:
            try:
                embed = discord.Embed(
                    title="👋 Olá! Sou seu novo assistente IA",
                    description=(
                        "Obrigado por me adicionar ao servidor!\n\n"
                        "🤖 Use `/skgpt` para conversar comigo\n"
                        "🎯 Use `/gif` para buscar GIFs\n"
                        "❓ Use `/help` para ver todos os comandos"
                    ),
                    color=0x5865F2
                )
                await guild.system_channel.send(embed=embed)
            except discord.Forbidden:
                logger.warning(f"⚠️ Sem permissão para enviar mensagem em {guild.name}")
    
    async def on_guild_remove_handler(self, guild: discord.Guild):
        """Executado quando o bot sai de um servidor"""
        logger.info(f"📉 Bot removido do servidor: {guild.name} ({guild.id})")
    
    async def send_log_message(self, guild: discord.Guild, message: str):
        """Envia mensagem para o canal de logs se configurado"""
        if not self.config.log_channel_id:
            return
        
        channel = guild.get_channel(self.config.log_channel_id)
        if not channel:
            return
        
        try:
            await channel.send(message[:2000])  # Limitar a 2000 caracteres
        except discord.Forbidden:
            logger.warning("⚠️ Sem permissão para enviar no canal de logs")
        except Exception as e:
            logger.error(f"❌ Erro ao enviar log: {e}")