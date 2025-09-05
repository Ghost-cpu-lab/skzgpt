"""
Serviço para integração com Groq AI
"""
import json
import logging
from typing import List, Dict, Any, Optional
from groq import Groq

logger = logging.getLogger(__name__)

class GroqService:
    """Serviço para interação com a API Groq"""
    
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("GROQ_API_KEY é obrigatório")
        
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"
        logger.info("✅ Serviço Groq inicializado")
    
    async def chat_completion(self, message: str, system_prompt: Optional[str] = None) -> str:
        """
        Gera uma resposta de chat usando Groq
        """
        try:
            messages = []
            
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            messages.append({"role": "user", "content": message})
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"❌ Erro no chat completion: {e}")
            return "Desculpe, ocorreu um erro ao processar sua mensagem. Tente novamente."
    
    async def parse_admin_command(self, message: str) -> List[Dict[str, Any]]:
        """
        Analisa comandos administrativos usando IA
        """
        system_prompt = """
Você é um assistente inteligente para servidor Discord com 95+ funcionalidades administrativas.
Retorne SEMPRE um JSON válido com a lista de ações a executar.

BÁSICO (10):
- "resposta": Resposta simples de chat
- "criar_embed": Criar embed personalizado
- "criar_canal": Criar canal texto/voz
- "criar_cargo": Criar cargo/role
- "limpar_mensagens": Limpar mensagens
- "enviar_dm": Enviar mensagem privada
- "anuncio_global": Anúncio em todos os canais
- "criar_poll": Criar enquete/votação
- "auto_react": Auto reagir mensagens
- "canal_temp": Criar canal temporário

INFORMAÇÕES (15):
- "listar_cargos": Todos os cargos
- "listar_canais": Todos os canais
- "listar_membros": Stats membros
- "info_servidor": Info completa servidor
- "listar_bots": Todos os bots
- "audit_log": Log auditoria
- "listar_convites": Convites ativos
- "top_usuarios": Ranking usuários
- "stats_detalhadas": Estatísticas avançadas
- "historico_mensagens": Histórico canal
- "member_info": Info detalhada membro
- "canal_stats": Estatísticas canal
- "emoji_stats": Stats emojis servidor
- "boost_info": Info boost servidor
- "permissions_check": Verificar permissões

GERENCIAMENTO (20):
- "slowmode": Modo lento canal
- "bloquear_canal": Bloquear canal
- "desbloquear_canal": Desbloquear canal
- "criar_categoria": Nova categoria
- "mover_canal": Mover canal
- "duplicar_canal": Duplicar canal
- "webhook_create": Criar webhook
- "backup_cargos": Backup cargos
- "restore_cargos": Restaurar cargos
- "bulk_create_channels": Criar múltiplos canais
- "channel_template": Template de canal
- "auto_archive": Auto arquivar threads
- "mass_role_assign": Atribuir cargo em massa
- "server_template": Template servidor
- "channel_sync": Sincronizar permissões
- "role_hierarchy": Reorganizar hierarquia
- "bulk_permissions": Permissões em massa
- "server_backup": Backup completo
- "clone_server": Clonar estrutura
- "mass_move": Mover canais em massa

MODERAÇÃO (20):
- "timeout_usuario": Timeout usuário
- "remover_timeout": Remover timeout
- "add_reacao": Adicionar reação
- "pin_mensagem": Fixar mensagem
- "unpin_mensagem": Desfixar mensagens
- "nick_usuario": Alterar apelido
- "reset_nicks": Reset apelidos
- "mass_ban": Ban em massa
- "mass_kick": Kick em massa
- "auto_mod": Auto moderação
- "word_filter": Filtro palavras
- "spam_protection": Proteção spam
- "raid_protection": Proteção raid
- "auto_warn": Sistema warnings
- "mute_sistema": Sistema mute
- "captcha_verify": Verificação captcha
- "anti_bot": Proteção anti bot
- "link_filter": Filtro links
- "image_filter": Filtro imagens
- "toxic_filter": Filtro toxicidade

AUTOMAÇÃO (15):
- "auto_role": Auto cargo entrada
- "welcome_msg": Mensagem boas vindas
- "goodbye_msg": Mensagem saída
- "level_system": Sistema level
- "xp_rewards": Recompensas XP
- "daily_backup": Backup diário
- "scheduled_msg": Mensagens agendadas
- "auto_clean": Limpeza automática
- "activity_monitor": Monitor atividade
- "inactive_cleanup": Limpar inativos
- "auto_promote": Promoção automática
- "event_scheduler": Agendar eventos
- "reminder_system": Sistema lembretes
- "auto_archive_old": Arquivar antigos
- "smart_notifications": Notificações IA

ENTRETENIMENTO (15):
- "mini_games": Mini jogos
- "quiz_system": Sistema quiz
- "music_queue": Fila música
- "meme_generator": Gerador memes
- "random_facts": Fatos aleatórios
- "daily_quote": Frase do dia
- "fortune_teller": Adivinhação
- "rock_paper": Pedra papel tesoura
- "coin_flip": Cara ou coroa
- "dice_roll": Rolar dados
- "8ball": Bola mágica
- "trivia_game": Jogo trivia
- "word_game": Jogo palavras
- "emoji_game": Jogo emoji
- "riddle_game": Jogo charadas

Formato de resposta:
[{"action": "tipo_acao", "resposta": "texto", "titulo": "titulo", "descricao": "desc", "cor": "5865F2", "nome": "nome", "valor": 30, "categoria": "Geral", "emoji": "👍"}]

IMPORTANTE: Sempre retorne JSON válido, mesmo para erros.
"""
        
        try:
            response = await self.chat_completion(message, system_prompt)
            
            # Tentar extrair JSON da resposta
            try:
                # Procurar por JSON na resposta
                start = response.find('[')
                end = response.rfind(']') + 1
                
                if start != -1 and end != -1:
                    json_str = response[start:end]
                    actions = json.loads(json_str)
                    return actions if isinstance(actions, list) else [actions]
                else:
                    # Se não encontrou JSON, retornar resposta simples
                    return [{"action": "resposta", "resposta": response}]
                    
            except json.JSONDecodeError:
                logger.warning("⚠️ Resposta da IA não é JSON válido")
                return [{"action": "resposta", "resposta": response}]
                
        except Exception as e:
            logger.error(f"❌ Erro ao analisar comando admin: {e}")
            return [{"action": "resposta", "resposta": "Erro ao processar comando administrativo."}]