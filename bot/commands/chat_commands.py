"""
Comandos de chat e interação
"""
import logging
import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional

from bot.config import BotConfig
from bot.services.groq_service import GroqService
from bot.services.gif_service import GifService
from bot.utils.security import SecurityValidator
from bot.utils.admin_actions import AdminActionExecutor

logger = logging.getLogger(__name__)

class ChatCommands:
    """Comandos de chat do bot"""
    
    def __init__(self, bot: commands.Bot, groq_service: GroqService, 
                 gif_service: Optional[GifService], config: BotConfig):
        self.bot = bot
        self.groq_service = groq_service
        self.gif_service = gif_service
        self.config = config
        self.security = SecurityValidator()
        self.admin_executor = AdminActionExecutor()
        
        logger.info("✅ Comandos de chat inicializados")
    
    async def handle_skgpt(self, interaction: discord.Interaction, mensagem: str):
        """Chatbot IA com funcionalidades administrativas"""
        await interaction.response.defer(ephemeral=False)
        
        try:
            # Validar entrada
            if not self.security.validate_input(mensagem):
                await interaction.followup.send("❌ Mensagem contém conteúdo inadequado.")
                return
            
            # Verificar se é busca de GIF
            if "gif" in mensagem.lower() and self.gif_service and self.gif_service.is_available():
                gif_url = await self.gif_service.search_gif(mensagem)
                if gif_url:
                    await interaction.followup.send(gif_url)
                    return
                else:
                    await interaction.followup.send(f"❌ Não encontrei GIF para: {mensagem}")
                    return
            
            # Analisar comando com IA
            actions = await self.groq_service.parse_admin_command(mensagem)
            
            # Executar ações
            results = []
            for action in actions:
                action_type = action.get("action", "resposta")
                
                # Verificar permissões para comandos admin
                if (action_type != "resposta" and 
                    not interaction.user.guild_permissions.administrator):
                    results.append("❌ Apenas administradores podem executar comandos administrativos.")
                    continue
                
                # Executar ação
                result = await self.admin_executor.execute_action(
                    action, interaction.guild, interaction
                )
                results.append(result)
            
            # Enviar resultados se houver
            if results and not any("✅ Resposta enviada" in r for r in results):
                response = "\n".join(results)[:2000]  # Limitar a 2000 chars
                await interaction.followup.send(response)
                
        except discord.NotFound:
            logger.warning("⚠️ Mensagem não encontrada - possivelmente expirou")
            # Não tenta responder se a mensagem não existe mais
        except Exception as e:
            logger.error(f"❌ Erro no comando skgpt: {e}")
            try:
                await interaction.followup.send("❌ Ocorreu um erro ao processar sua mensagem.")
            except discord.NotFound:
                # Ignora se não conseguir responder
                pass
    
    async def handle_gif(self, interaction: discord.Interaction, termo: str):
        """Busca GIF pelo termo especificado"""
        if not self.gif_service or not self.gif_service.is_available():
            await interaction.response.send_message(
                "❌ Serviço de GIF não está disponível.", ephemeral=True
            )
            return
        
        await interaction.response.defer()
        
        try:
            # Validar entrada
            if not self.security.validate_input(termo):
                await interaction.followup.send("❌ Termo de busca inadequado.")
                return
            
            gif_url = await self.gif_service.search_gif(termo)
            if gif_url:
                embed = discord.Embed(
                    title=f"🎯 GIF: {termo}",
                    color=0x5865F2
                )
                embed.set_image(url=gif_url)
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send(f"❌ Não encontrei GIF para: {termo}")
                
        except Exception as e:
            logger.error(f"❌ Erro no comando gif: {e}")
            await interaction.followup.send("❌ Erro ao buscar GIF.")
    
    async def handle_help(self, interaction: discord.Interaction):
        """Mostra ajuda dos comandos do bot"""
        embed = discord.Embed(
            title="🤖 Ajuda do Bot",
            description="Lista de comandos disponíveis:",
            color=0x5865F2
        )
        
        embed.add_field(
            name="🗣️ /skgpt <mensagem>",
            value="Conversa com o chatbot IA. Admins podem usar comandos administrativos.",
            inline=False
        )
        
        if self.gif_service and self.gif_service.is_available():
            embed.add_field(
                name="🎬 /gif <termo>",
                value="Busca GIF pelo termo especificado.",
                inline=False
            )
        
        embed.add_field(
            name="❓ /help",
            value="Mostra esta mensagem de ajuda.",
            inline=False
        )
        
        embed.add_field(
            name="💬 Comandos de Chat",
            value=(
                "**`/chat <mensagem>`** - Chat simples com IA\n"
                "**`/skgpt <mensagem>`** - IA com comandos admin\n"
                "**`/gif <termo>`** - Buscar GIFs\n"
            ),
            inline=False
        )
        
        embed.add_field(
            name="📊 Comandos de Informação",
            value=(
                "**`/info servidor`** - Info do servidor\n"
                "**`/info membros`** - Stats de membros\n"
                "**`/info cargos`** - Lista todos os cargos\n"
                "**`/info canais`** - Lista todos os canais\n"
                "**`/info bots`** - Lista todos os bots\n"
                "**`/info stats`** - Estatísticas detalhadas\n"
                "**`/info boost`** - Informações de boost\n"
                "*Disponível apenas para administradores*"
            ),
            inline=False
        )
        
        embed.add_field(
            name="🛠️ Comandos de Gerenciamento",
            value=(
                "**`/gerenciar criar_canal <nome>`** - Criar canal\n"
                "**`/gerenciar criar_categoria <nome>`** - Criar categoria\n"
                "**`/gerenciar slowmode <canal> <segundos>`** - Modo lento\n"
                "**`/gerenciar bloquear_canal <canal>`** - Bloquear canal\n"
                "**`/gerenciar backup_cargos`** - Backup de cargos\n"
                "**`/gerenciar limpar_mensagens <canal>`** - Limpar mensagens\n"
                "*Disponível apenas para administradores*"
            ),
            inline=False
        )
        
        embed.add_field(
            name="🎮 Comandos de Diversão",
            value=(
                "**`/diversao coin_flip`** - Cara ou coroa\n"
                "**`/diversao dice_roll`** - Rolar dados\n"
                "**`/diversao 8ball`** - Bola mágica 8\n"
                "**`/diversao random_facts`** - Fatos aleatórios\n"
                "**`/diversao daily_quote`** - Frase do dia\n"
                "**`/diversao word_game`** - Jogo de palavras\n"
                "*Disponível para todos os usuários*"
            ),
            inline=False
        )
        
        embed.add_field(
            name="🔐 Total de Funcionalidades",
            value=(
                "**95+ FUNCIONALIDADES DISPONÍVEIS:**\n"
                "• 10 Básicas • 15 Informações • 20 Gerenciamento\n"
                "• 20 Moderação • 15 Automação • 15 Entretenimento\n\n"
                "**Use `/skgpt` para acesso completo via IA!**"
            ),
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    # ========== NOVOS HANDLERS PARA COMANDOS ORGANIZADOS ==========
    
    async def handle_chat_only(self, interaction: discord.Interaction, mensagem: str):
        """Handler para chat simples com IA (sem funcionalidades admin)"""
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
    
    async def handle_server_info(self, interaction: discord.Interaction, tipo: str):
        """Handler para informações do servidor"""
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
        
        if tipo not in action_map:
            await interaction.followup.send(f"❌ Tipo '{tipo}' não reconhecido. Use: {', '.join(action_map.keys())}", ephemeral=True)
            return
        
        action = {"action": action_map[tipo]}
        result = await self.admin_executor.execute_action(action, interaction.guild, interaction)
        
        if not result.startswith("✅"):
            await interaction.followup.send(result, ephemeral=True)
    
    async def handle_management(self, interaction: discord.Interaction, acao: str, nome: str, valor: int = 0):
        """Handler para gerenciamento do servidor"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Apenas administradores podem usar este comando.", ephemeral=True)
            return
            
        await interaction.response.defer()
        
        valid_actions = [
            "criar_canal", "criar_categoria", "criar_cargo", "duplicar_canal",
            "mover_canal", "slowmode", "bloquear_canal", "desbloquear_canal",
            "webhook_create", "backup_cargos", "limpar_mensagens"
        ]
        
        if acao not in valid_actions:
            await interaction.followup.send(f"❌ Ação '{acao}' não reconhecida. Use: {', '.join(valid_actions)}", ephemeral=True)
            return
        
        action = {
            "action": acao,
            "nome": nome,
            "valor": valor
        }
        
        result = await self.admin_executor.execute_action(action, interaction.guild, interaction)
        await interaction.followup.send(result)
    
    async def handle_moderation(self, interaction: discord.Interaction, acao: str, canal: str = None, emoji: str = "👍"):
        """Handler para moderação"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Apenas administradores podem usar este comando.", ephemeral=True)
            return
            
        await interaction.response.defer()
        
        valid_actions = [
            "add_reacao", "pin_mensagem", "unpin_mensagem", "auto_mod",
            "word_filter", "spam_protection", "raid_protection"
        ]
        
        if acao not in valid_actions:
            await interaction.followup.send(f"❌ Ação '{acao}' não reconhecida. Use: {', '.join(valid_actions)}", ephemeral=True)
            return
        
        action = {
            "action": acao,
            "nome": canal or interaction.channel.name,
            "emoji": emoji
        }
        
        result = await self.admin_executor.execute_action(action, interaction.guild, interaction)
        await interaction.followup.send(result)
    
    async def handle_entertainment(self, interaction: discord.Interaction, jogo: str):
        """Handler para entretenimento"""
        await interaction.response.defer()
        
        valid_games = [
            "coin_flip", "dice_roll", "8ball", "rock_paper", "random_facts",
            "daily_quote", "trivia_game", "word_game", "emoji_game", "riddle_game"
        ]
        
        if jogo not in valid_games:
            await interaction.followup.send(f"❌ Jogo '{jogo}' não reconhecido. Use: {', '.join(valid_games)}", ephemeral=True)
            return
        
        action = {"action": jogo}
        result = await self.admin_executor.execute_action(action, interaction.guild, interaction)
        await interaction.followup.send(result)
    
    async def handle_automation(self, interaction: discord.Interaction, funcao: str, ativar: bool = True):
        """Handler para automação"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Apenas administradores podem usar este comando.", ephemeral=True)
            return
            
        await interaction.response.defer()
        
        valid_functions = [
            "auto_role", "welcome_msg", "goodbye_msg", "level_system",
            "auto_clean", "activity_monitor", "reminder_system"
        ]
        
        if funcao not in valid_functions:
            await interaction.followup.send(f"❌ Função '{funcao}' não reconhecida. Use: {', '.join(valid_functions)}", ephemeral=True)
            return
        
        action = {
            "action": funcao,
            "ativar": ativar
        }
        
        result = await self.admin_executor.execute_action(action, interaction.guild, interaction)
        await interaction.followup.send(result)