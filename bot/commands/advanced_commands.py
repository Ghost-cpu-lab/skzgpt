"""
Comandos slash avançados organizados por categoria
"""
import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional, Literal
import logging

from ..services.groq_service import GroqService
from ..utils.admin_actions import AdminActionExecutor

logger = logging.getLogger(__name__)

class AdvancedCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.groq_service = GroqService()
        self.admin_executor = AdminActionExecutor()
        logger.info("✅ Comandos avançados inicializados")

    # ==================== CHAT IA ====================
    @app_commands.command(name="chat", description="💬 Conversar com a IA")
    @app_commands.describe(mensagem="Sua mensagem para a IA")
    async def chat_ai(self, interaction: discord.Interaction, mensagem: str):
        """Chat simples com IA sem funcionalidades administrativas"""
        await interaction.response.defer()
        
        try:
            response = await self.groq_service.chat_completion(mensagem)
            
            embed = discord.Embed(
                title="🤖 Chat IA",
                description=response,
                color=0x5865F2
            )
            embed.set_footer(text=f"Pergunta de {interaction.user.display_name}")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Erro no chat IA: {e}")
            await interaction.followup.send("❌ Erro na IA. Tente novamente.", ephemeral=True)

    # ==================== INFORMAÇÕES ====================
    @app_commands.command(name="info", description="📊 Informações do servidor")
    @app_commands.describe(
        tipo="Tipo de informação"
    )
    async def server_info(
        self, 
        interaction: discord.Interaction,
        tipo: Literal[
            "servidor", "membros", "cargos", "canais", "bots", 
            "convites", "top_usuarios", "stats", "boost", "emojis"
        ]
    ):
        """Comandos de informação do servidor"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Apenas administradores podem usar este comando.", ephemeral=True)
            return
            
        await interaction.response.defer()
        
        action_map = {
            "servidor": "info_servidor",
            "membros": "listar_membros", 
            "cargos": "listar_cargos",
            "canais": "listar_canais",
            "bots": "listar_bots",
            "convites": "listar_convites",
            "top_usuarios": "top_usuarios",
            "stats": "stats_detalhadas",
            "boost": "boost_info",
            "emojis": "emoji_stats"
        }
        
        action = {"action": action_map[tipo]}
        result = await self.admin_executor.execute_action(action, interaction.guild, interaction)
        
        if not result.startswith("✅"):
            await interaction.followup.send(result, ephemeral=True)

    # ==================== GERENCIAMENTO ====================
    @app_commands.command(name="gerenciar", description="🛠️ Gerenciar servidor")
    @app_commands.describe(
        acao="Ação de gerenciamento",
        nome="Nome do canal/cargo/categoria",
        valor="Valor numérico (segundos, quantidade, etc)"
    )
    async def manage_server(
        self,
        interaction: discord.Interaction,
        acao: Literal[
            "criar_canal", "criar_categoria", "criar_cargo", "duplicar_canal",
            "mover_canal", "slowmode", "bloquear_canal", "desbloquear_canal",
            "webhook_create", "backup_cargos", "limpar_mensagens"
        ],
        nome: str,
        valor: Optional[int] = None
    ):
        """Comandos de gerenciamento do servidor"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Apenas administradores podem usar este comando.", ephemeral=True)
            return
            
        await interaction.response.defer()
        
        action = {
            "action": acao,
            "nome": nome,
            "valor": valor or 0
        }
        
        result = await self.admin_executor.execute_action(action, interaction.guild, interaction)
        await interaction.followup.send(result)

    # ==================== MODERAÇÃO ====================
    @app_commands.command(name="moderar", description="🛡️ Moderação do servidor")
    @app_commands.describe(
        acao="Ação de moderação",
        canal="Nome do canal (quando aplicável)",
        emoji="Emoji para reação (quando aplicável)"
    )
    async def moderate_server(
        self,
        interaction: discord.Interaction,
        acao: Literal[
            "add_reacao", "pin_mensagem", "unpin_mensagem", "auto_mod",
            "word_filter", "spam_protection", "raid_protection"
        ],
        canal: Optional[str] = None,
        emoji: Optional[str] = "👍"
    ):
        """Comandos de moderação"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Apenas administradores podem usar este comando.", ephemeral=True)
            return
            
        await interaction.response.defer()
        
        action = {
            "action": acao,
            "nome": canal or interaction.channel.name,
            "emoji": emoji
        }
        
        result = await self.admin_executor.execute_action(action, interaction.guild, interaction)
        await interaction.followup.send(result)

    # ==================== ENTRETENIMENTO ====================
    @app_commands.command(name="diversao", description="🎮 Jogos e entretenimento")
    @app_commands.describe(
        jogo="Tipo de jogo/entretenimento"
    )
    async def entertainment(
        self,
        interaction: discord.Interaction,
        jogo: Literal[
            "coin_flip", "dice_roll", "8ball", "rock_paper", "random_facts",
            "daily_quote", "trivia_game", "word_game", "emoji_game"
        ]
    ):
        """Comandos de entretenimento"""
        await interaction.response.defer()
        
        action = {"action": jogo}
        result = await self.admin_executor.execute_action(action, interaction.guild, interaction)
        await interaction.followup.send(result)

    # ==================== AUTOMAÇÃO ====================
    @app_commands.command(name="automatizar", description="🤖 Automação do servidor")
    @app_commands.describe(
        funcao="Função de automação",
        ativar="Ativar ou desativar"
    )
    async def automation(
        self,
        interaction: discord.Interaction,
        funcao: Literal[
            "auto_role", "welcome_msg", "goodbye_msg", "level_system",
            "auto_clean", "activity_monitor", "reminder_system"
        ],
        ativar: bool = True
    ):
        """Comandos de automação"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Apenas administradores podem usar este comando.", ephemeral=True)
            return
            
        await interaction.response.defer()
        
        action = {
            "action": funcao,
            "ativar": ativar
        }
        
        result = await self.admin_executor.execute_action(action, interaction.guild, interaction)
        await interaction.followup.send(result)

async def setup(bot):
    await bot.add_cog(AdvancedCommands(bot))