"""
Handler para tratamento de erros
"""
import logging
import discord
from discord.ext import commands
from typing import Optional

logger = logging.getLogger(__name__)

class ErrorHandler:
    """Handler para tratamento centralizado de erros"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.setup_error_handlers()
        logger.info("✅ Handler de erros configurado")
    
    def setup_error_handlers(self):
        """Configura os handlers de erro"""
        
        @self.bot.event
        async def on_command_error(ctx, error):
            await self.handle_command_error(ctx, error)
        
        @self.bot.tree.error
        async def on_app_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
            await self.handle_app_command_error(interaction, error)
    
    async def handle_command_error(self, ctx, error):
        """Trata erros de comandos de texto"""
        if isinstance(error, commands.CommandNotFound):
            return  # Ignorar comandos não encontrados
        
        error_msg = self.format_error_message(error)
        logger.error(f"❌ Erro no comando {ctx.command}: {error}")
        
        try:
            await ctx.send(f"❌ {error_msg}", ephemeral=True)
        except discord.HTTPException:
            logger.error("❌ Não foi possível enviar mensagem de erro")
    
    async def handle_app_command_error(self, interaction: discord.Interaction, error):
        """Trata erros de slash commands"""
        error_msg = self.format_error_message(error)
        logger.error(f"❌ Erro no comando {interaction.command}: {error}")
        
        try:
            if interaction.response.is_done():
                await interaction.followup.send(f"❌ {error_msg}", ephemeral=True)
            else:
                await interaction.response.send_message(f"❌ {error_msg}", ephemeral=True)
        except (discord.HTTPException, discord.NotFound):
            # Ignora erros de envio se a mensagem expirou
            pass
    
    def format_error_message(self, error) -> str:
        """Formata mensagens de erro para o usuário"""
        if isinstance(error, discord.app_commands.CommandOnCooldown):
            return f"Comando em cooldown. Tente novamente em {error.retry_after:.1f} segundos."
        
        elif isinstance(error, discord.app_commands.MissingPermissions):
            return "Você não tem permissão para usar este comando."
        
        elif isinstance(error, discord.app_commands.BotMissingPermissions):
            return "O bot não tem as permissões necessárias para executar este comando."
        
        elif isinstance(error, discord.Forbidden):
            return "Não tenho permissão para realizar esta ação."
        
        elif isinstance(error, discord.NotFound):
            return "Item não encontrado."
        
        elif isinstance(error, discord.HTTPException):
            return "Erro de comunicação com o Discord. Tente novamente."
        
        else:
            return "Ocorreu um erro inesperado. Tente novamente."