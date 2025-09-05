import discord
from discord.ext import commands
import json
import re
import os
import tempfile
import asyncio
import logging
from discord import app_commands
from keep_alive import keep_alive

# ===================== LOGGING CONFIG =====================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ===================== CONFIG =====================
TOKEN = os.getenv("DISCORD_TOKEN", "")
ID_CANAL_REGISTROS = int(os.getenv("CANAL_REGISTROS_ID", "1411090800988913694"))
ID_ADMIN = int(os.getenv("ADMIN_ID", "765701362448072734"))
ARQUIVO_USERS = "users.json"
ARQUIVO_PROCESSADOS = "mensagens_processadas.json"

if not TOKEN:
    logger.error("DISCORD_TOKEN não encontrado nas variáveis de ambiente!")
    raise SystemExit("Token do Discord é obrigatório!")

# ==================================================

# ---------------------------- Funções de persistência ----------------------------
def carregar_users():
    """Carrega os dados de usuários do arquivo JSON"""
    try:
        if os.path.exists(ARQUIVO_USERS):
            with open(ARQUIVO_USERS, "r", encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Erro ao carregar users.json: {e}")
    return {}

def salvar_users(users):
    """Salva os dados de usuários no arquivo JSON de forma segura"""
    try:
        with tempfile.NamedTemporaryFile("w", delete=False, dir=".", encoding='utf-8') as tmp:
            json.dump(users, tmp, indent=4, ensure_ascii=False)
            tmp.flush()
            os.fsync(tmp.fileno())
            os.replace(tmp.name, ARQUIVO_USERS)
        logger.info("Dados de usuários salvos com sucesso")
    except Exception as e:
        logger.error(f"Erro ao salvar users.json: {e}")

def carregar_processados():
    """Carrega IDs de mensagens já processadas"""
    try:
        if os.path.exists(ARQUIVO_PROCESSADOS):
            with open(ARQUIVO_PROCESSADOS, "r", encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Erro ao carregar mensagens processadas: {e}")
    return []

def salvar_processados(processados):
    """Salva IDs de mensagens processadas"""
    try:
        with tempfile.NamedTemporaryFile("w", delete=False, dir=".", encoding='utf-8') as tmp:
            json.dump(processados, tmp, indent=4, ensure_ascii=False)
            tmp.flush()
            os.fsync(tmp.fileno())
            os.replace(tmp.name, ARQUIVO_PROCESSADOS)
        logger.info("Lista de mensagens processadas salva com sucesso")
    except Exception as e:
        logger.error(f"Erro ao salvar mensagens processadas: {e}")

# ---------------------------- Util ----------------------------
def extrair_texto_da_mensagem(message: discord.Message) -> str:
    """Extrai todo o texto de uma mensagem, incluindo embeds"""
    partes = []
    
    # Conteúdo da mensagem
    if message.content:
        partes.append(message.content)

    # Conteúdo dos embeds
    for emb in message.embeds:
        data = emb.to_dict()
        for k in ("title", "description"):
            if data.get(k):
                partes.append(str(data[k]))
        
        # Fields dos embeds
        for field in data.get("fields", []):
            if field.get("name"):
                partes.append(str(field["name"]))
            if field.get("value"):
                partes.append(str(field["value"]))
        
        # Footer do embed
        footer = data.get("footer", {}).get("text")
        if footer:
            partes.append(str(footer))

    return "\n".join(partes).strip()

def parse_valor_br(data: str) -> tuple:
    """Parse valores no formato brasileiro (R$ 10,50 ou R$ 1.234,56)"""
    raw = data.strip()
    
    # Remove símbolos de moeda
    raw = re.sub(r'[R$\s]', '', raw)
    
    # Trata formato brasileiro (1.234,56 ou 10,50)
    if "," in raw and "." in raw:
        # Formato: 1.234,56
        raw = raw.replace(".", "").replace(",", ".")
    elif "," in raw:
        # Formato: 10,50
        raw = raw.replace(",", ".")
    
    try:
        return float(raw), data.strip()
    except ValueError:
        logger.error(f"Erro ao converter valor: {data}")
        return 0.0, data.strip()

# ---------------------------- Bot e intents ----------------------------
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ---------------------------- Eventos do Bot ----------------------------
@bot.event
async def on_ready():
    """Evento executado quando o bot está pronto"""
    logger.info(f"✅ Bot conectado como {bot.user}")
    
    try:
        synced = await bot.tree.sync()
        logger.info(f"🌐 {len(synced)} comandos slash registrados com sucesso!")
    except Exception as e:
        logger.error(f"Erro ao registrar comandos slash: {e}")
    
    # Inicia o keep-alive
    keep_alive()

@bot.event
async def on_error(event, *args, **kwargs):
    """Log de erros do bot"""
    logger.error(f"Erro no evento {event}: {args}, {kwargs}")

@bot.event
async def on_command_error(ctx, error):
    """Log de erros de comandos"""
    logger.error(f"Erro no comando {ctx.command}: {error}")

@bot.event
async def on_message(message: discord.Message):
    """Evento de processamento de mensagens para sistema de créditos"""
    # Ignora mensagens do próprio bot
    if message.author == bot.user:
        return

    # Verifica se é no canal de registros
    if message.channel.id == ID_CANAL_REGISTROS:
        conteudo = extrair_texto_da_mensagem(message)
        logger.info("==== NOVA MENSAGEM NO CANAL DE REGISTROS ====")
        logger.info(f"Autor: {message.author}")
        logger.info(f"Conteúdo: {conteudo[:200]}...")  # Log truncado
        logger.info("=" * 50)

        # Verifica se a mensagem já foi processada
        processados = carregar_processados()
        if str(message.id) in processados:
            logger.info(f"Mensagem {message.id} já foi processada anteriormente")
            return

        # Primeiro verifica se o pagamento foi concluído
        pagamento_concluido = re.search(
            r"(conclu[íi]d[oa]|aprovad[oa]|confirmad[oa]|pag[oa]|sucesso)",
            conteudo,
            re.IGNORECASE,
        )
        
        # Verifica se não está aguardando pagamento
        aguardando_pagamento = re.search(
            r"(aguardando|pendente|processando|em\s*andamento)",
            conteudo,
            re.IGNORECASE,
        )
        
        # Só processa se pagamento foi concluído E não está aguardando
        if not pagamento_concluido or aguardando_pagamento:
            logger.info("⏳ Pagamento ainda não foi concluído - aguardando confirmação")
            return

        # Regex para extrair ID do comprador e valor total
        comprador_match = re.search(
            r"[Ii][Dd]\s*do\s*comprador[:\s*]*\**\s*(\d+)",
            conteudo,
            re.IGNORECASE,
        )
        
        valor_match = re.search(
            r"valor\s*total\s*do\s*carrinho[:\s*]*\**\s*([\d.,R$\s]+)",
            conteudo,
            re.IGNORECASE,
        )

        if comprador_match and valor_match:
            comprador_id = str(comprador_match.group(1))
            valor_float, valor_raw = parse_valor_br(valor_match.group(1))
            
            # Calcula créditos (mínimo 1)
            creditos_ganhos = max(1, int(valor_float))

            # Atualiza saldo do usuário
            users = carregar_users()
            saldo_atual = users.get(comprador_id, 0) + creditos_ganhos
            users[comprador_id] = saldo_atual
            salvar_users(users)

            # Marca mensagem como processada
            processados.append(str(message.id))
            salvar_processados(processados)

            logger.info(
                f"[CRÉDITOS] Comprador: {comprador_id} | "
                f"Valor: '{valor_raw}' -> {valor_float} | "
                f"Créditos: +{creditos_ganhos} | "
                f"Saldo total: {saldo_atual}"
            )

            # Envia DM para o comprador
            try:
                user = await bot.fetch_user(int(comprador_id))
                await user.send(
                    f"🎉 **Parabéns! Você ganhou créditos!**\n\n"
                    f"💰 **+{creditos_ganhos} créditos** adicionados!\n"
                    f"🏦 **Saldo atual:** {saldo_atual} créditos\n\n"
                    f"🛍️ Use `/loja` para ver as recompensas disponíveis\n"
                    f"🎁 Use `/resgatar` para trocar seus créditos\n"
                    f"💳 Use `/saldo` para consultar seu saldo"
                )
                logger.info(f"DM enviada para o usuário {comprador_id}")
            except Exception as e:
                logger.warning(f"Não foi possível enviar DM para {comprador_id}: {e}")

            # Confirma no canal
            try:
                await message.add_reaction("✅")
                await message.channel.send(
                    f"✅ **Créditos processados!**\n"
                    f"👤 <@{comprador_id}> ganhou **{creditos_ganhos} créditos**\n"
                    f"💰 Saldo total: **{saldo_atual} créditos**"
                )
            except Exception as e:
                logger.error(f"Erro ao responder no canal: {e}")
        else:
            logger.warning("⚠️ Não foi possível extrair ID do comprador ou valor total da mensagem")

    # Processa outros comandos
    await bot.process_commands(message)

# ---------------------------- Comandos Slash ----------------------------
@bot.tree.command(name="saldo", description="Consulta seu saldo de créditos")
async def saldo(interaction: discord.Interaction):
    """Comando para consultar saldo de créditos"""
    await interaction.response.defer(ephemeral=True)
    
    user_id = str(interaction.user.id)
    users = carregar_users()
    saldo_atual = users.get(user_id, 0)
    
    embed = discord.Embed(
        title="💰 Seu Saldo de Créditos",
        description=f"Você possui **{saldo_atual} créditos**",
        color=discord.Color.green() if saldo_atual > 0 else discord.Color.red()
    )
    
    embed.add_field(
        name="Como ganhar mais créditos?",
        value="💳 Faça compras em nossa loja!\n🎁 Cada R$ 1,00 = 1 crédito",
        inline=False
    )
    
    embed.set_footer(text="Use /loja para ver as recompensas disponíveis")
    
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="loja", description="Visualiza a loja de recompensas")
async def loja(interaction: discord.Interaction):
    """Comando para mostrar a loja de recompensas"""
    await interaction.response.defer(ephemeral=True)
    
    embed = discord.Embed(
        title="🏪 Loja de Recompensas",
        description="Troque seus créditos por recompensas incríveis!",
        color=discord.Color.gold()
    )
    
    embed.add_field(
        name="💸 10% de Desconto",
        value="**Custo:** 2 créditos\n**Descrição:** Desconto em sua próxima compra",
        inline=False
    )
    
    embed.add_field(
        name="🎮 1 Conta Grátis",
        value="**Custo:** 6 créditos\n**Descrição:** Receba uma conta premium gratuita",
        inline=False
    )
    
    embed.set_footer(text="Use /resgatar para trocar seus créditos por recompensas")
    
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="preco", description="Consulta a tabela de preços das recompensas")
async def preco(interaction: discord.Interaction):
    """Comando para mostrar preços das recompensas"""
    await interaction.response.defer(ephemeral=True)
    
    embed = discord.Embed(
        title="📊 Tabela de Preços",
        description="Confira quanto custa cada recompensa:",
        color=discord.Color.blue()
    )
    
    embed.add_field(name="2️⃣ créditos", value="💸 10% de desconto", inline=True)
    embed.add_field(name="6️⃣ créditos", value="🎮 1 conta grátis", inline=True)
    embed.add_field(name="\u200b", value="\u200b", inline=True)  # Espaço vazio
    
    embed.add_field(
        name="💡 Dica",
        value="Quanto mais você compra, mais créditos ganha!\nCada R$ 1,00 gasto = 1 crédito ganho",
        inline=False
    )
    
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="resgatar", description="Resgata recompensas com seus créditos")
@app_commands.describe(opcao="Escolha a recompensa que deseja resgatar")
@app_commands.choices(opcao=[
    app_commands.Choice(name="💸 10% de desconto (2 créditos)", value="desconto"),
    app_commands.Choice(name="🎮 1 conta grátis (6 créditos)", value="conta")
])
async def resgatar(interaction: discord.Interaction, opcao: app_commands.Choice[str]):
    """Comando para resgatar recompensas"""
    await interaction.response.defer(ephemeral=True)
    
    user_id = str(interaction.user.id)
    users = carregar_users()
    saldo = users.get(user_id, 0)

    try:
        admin = await bot.fetch_user(ID_ADMIN)
    except Exception as e:
        logger.error(f"Erro ao buscar administrador: {e}")
        await interaction.followup.send("❌ Erro interno. Tente novamente mais tarde.")
        return

    if opcao.value == "desconto":
        custo = 2
        recompensa = "10% de desconto"
        emoji = "💸"
        
    elif opcao.value == "conta":
        custo = 6
        recompensa = "1 conta grátis"
        emoji = "🎮"
    
    else:
        await interaction.followup.send("❌ Opção inválida!")
        return

    if saldo >= custo:
        # Deduz créditos
        novo_saldo = saldo - custo
        users[user_id] = novo_saldo
        salvar_users(users)
        
        # Embed de sucesso para o usuário
        embed_user = discord.Embed(
            title="🎁 Resgate Realizado com Sucesso!",
            description=f"Você resgatou: **{emoji} {recompensa}**",
            color=discord.Color.green()
        )
        embed_user.add_field(name="💰 Saldo anterior", value=f"{saldo} créditos", inline=True)
        embed_user.add_field(name="💸 Custo", value=f"{custo} créditos", inline=True)
        embed_user.add_field(name="💳 Novo saldo", value=f"{novo_saldo} créditos", inline=True)
        embed_user.add_field(
            name="📞 Próximo passo",
            value="Entre em contato com um administrador para receber sua recompensa!",
            inline=False
        )
        
        await interaction.followup.send(embed=embed_user)
        
        # Notifica o administrador
        try:
            embed_admin = discord.Embed(
                title="🔔 Novo Resgate Realizado",
                description=f"**Usuário:** {interaction.user.mention} ({interaction.user})",
                color=discord.Color.orange()
            )
            embed_admin.add_field(name="🎁 Recompensa", value=f"{emoji} {recompensa}", inline=True)
            embed_admin.add_field(name="💸 Custo", value=f"{custo} créditos", inline=True)
            embed_admin.add_field(name="💳 Saldo final", value=f"{novo_saldo} créditos", inline=True)
            embed_admin.add_field(name="🆔 ID do usuário", value=f"`{user_id}`", inline=False)
            
            await admin.send(embed=embed_admin)
            logger.info(f"Administrador notificado sobre resgate de {interaction.user}")
        except Exception as e:
            logger.error(f"Erro ao notificar administrador: {e}")
            
    else:
        # Créditos insuficientes
        embed_erro = discord.Embed(
            title="❌ Créditos Insuficientes",
            description=f"Você precisa de **{custo} créditos** para resgatar esta recompensa.",
            color=discord.Color.red()
        )
        embed_erro.add_field(name="💰 Seu saldo atual", value=f"{saldo} créditos", inline=True)
        embed_erro.add_field(name="💸 Faltam", value=f"{custo - saldo} créditos", inline=True)
        embed_erro.add_field(
            name="💡 Como ganhar mais?",
            value="Faça mais compras em nossa loja!\nCada R$ 1,00 gasto = 1 crédito ganho",
            inline=False
        )
        
        await interaction.followup.send(embed=embed_erro)

# ---------------------------- Comandos de Admin ----------------------------
@bot.tree.command(name="adicionar", description="[ADMIN] Adiciona créditos manualmente a um usuário")
@app_commands.describe(
    usuario="Usuário que receberá os créditos",
    quantidade="Quantidade de créditos a adicionar"
)
async def adicionar(interaction: discord.Interaction, usuario: discord.User, quantidade: int):
    """Comando administrativo para adicionar créditos"""
    # Verifica permissões
    if not interaction.user.guild_permissions.administrator and interaction.user.id != ID_ADMIN:
        await interaction.response.send_message(
            "❌ **Acesso negado!** Você não tem permissão para usar este comando.", 
            ephemeral=True
        )
        return

    if quantidade <= 0:
        await interaction.response.send_message(
            "❌ A quantidade deve ser maior que zero.", 
            ephemeral=True
        )
        return

    await interaction.response.defer(ephemeral=True)

    # Adiciona créditos
    users = carregar_users()
    user_id = str(usuario.id)
    saldo_anterior = users.get(user_id, 0)
    saldo_atual = saldo_anterior + quantidade
    users[user_id] = saldo_atual
    salvar_users(users)

    # Embed de confirmação para o admin
    embed_admin = discord.Embed(
        title="✅ Créditos Adicionados",
        description=f"Créditos adicionados com sucesso para {usuario.mention}",
        color=discord.Color.green()
    )
    embed_admin.add_field(name="💰 Saldo anterior", value=f"{saldo_anterior} créditos", inline=True)
    embed_admin.add_field(name="➕ Adicionado", value=f"{quantidade} créditos", inline=True)
    embed_admin.add_field(name="💳 Novo saldo", value=f"{saldo_atual} créditos", inline=True)
    
    await interaction.followup.send(embed=embed_admin)

    # Notifica o usuário
    try:
        embed_user = discord.Embed(
            title="🎉 Você Recebeu Créditos!",
            description=f"Um administrador adicionou créditos à sua conta!",
            color=discord.Color.gold()
        )
        embed_user.add_field(name="💰 Créditos recebidos", value=f"{quantidade} créditos", inline=True)
        embed_user.add_field(name="💳 Novo saldo", value=f"{saldo_atual} créditos", inline=True)
        embed_user.add_field(
            name="🛍️ O que fazer agora?",
            value="Use `/loja` para ver as recompensas disponíveis!",
            inline=False
        )
        
        await usuario.send(embed=embed_user)
        logger.info(f"Usuário {usuario} notificado sobre adição de créditos")
    except Exception as e:
        logger.warning(f"Não foi possível notificar {usuario.id} sobre os créditos: {e}")

@bot.tree.command(name="stats", description="[ADMIN] Mostra estatísticas do sistema de créditos")
async def stats(interaction: discord.Interaction):
    """Comando administrativo para ver estatísticas"""
    if not interaction.user.guild_permissions.administrator and interaction.user.id != ID_ADMIN:
        await interaction.response.send_message(
            "❌ **Acesso negado!** Você não tem permissão para usar este comando.", 
            ephemeral=True
        )
        return

    await interaction.response.defer(ephemeral=True)

    users = carregar_users()
    processados = carregar_processados()
    
    total_usuarios = len(users)
    total_creditos = sum(users.values())
    total_processadas = len(processados)
    
    # Usuário com mais créditos
    top_user_id = max(users.keys(), key=lambda k: users[k]) if users else None
    top_user_credits = users.get(top_user_id, 0) if top_user_id else 0
    
    embed = discord.Embed(
        title="📊 Estatísticas do Sistema",
        description="Dados gerais do sistema de créditos",
        color=discord.Color.blue()
    )
    
    embed.add_field(name="👥 Total de usuários", value=total_usuarios, inline=True)
    embed.add_field(name="💰 Total de créditos", value=total_creditos, inline=True)
    embed.add_field(name="📝 Mensagens processadas", value=total_processadas, inline=True)
    
    if top_user_id:
        try:
            top_user = await bot.fetch_user(int(top_user_id))
            embed.add_field(
                name="🏆 Usuário com mais créditos",
                value=f"{top_user.mention}\n{top_user_credits} créditos",
                inline=False
            )
        except:
            embed.add_field(
                name="🏆 Usuário com mais créditos",
                value=f"ID: {top_user_id}\n{top_user_credits} créditos",
                inline=False
            )
    
    await interaction.followup.send(embed=embed)

# ---------------------------- Manter bot online ----------------------------
async def manter_online():
    """Task para manter o bot online e fazer logs periódicos"""
    while True:
        try:
            # Verifica se a latência é válida
            latency = bot.latency
            if latency and not (latency != latency):  # Check for NaN
                latency_ms = round(latency * 1000)
                logger.info(f"🤖 Bot online - Latência: {latency_ms}ms")
            else:
                logger.info("🤖 Bot online - Latência: calculando...")
            await asyncio.sleep(300)  # Log a cada 5 minutos
        except Exception as e:
            logger.error(f"Erro no keep-alive: {e}")
            await asyncio.sleep(60)

@bot.event
async def setup_hook():
    """Inicia tasks em background"""
    bot.loop.create_task(manter_online())

# ---------------------------- Inicialização ----------------------------
def main():
    """Função principal para iniciar o bot"""
    logger.info("🚀 Iniciando bot Discord...")
    logger.info(f"📊 Canal de registros: {ID_CANAL_REGISTROS}")
    logger.info(f"👑 Admin ID: {ID_ADMIN}")
    
    try:
        bot.run(TOKEN, log_handler=None)  # Usa nosso próprio logging
    except discord.LoginFailure:
        logger.error("❌ Token do Discord inválido!")
        raise SystemExit("Token inválido")
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")
        raise SystemExit(f"Erro fatal: {e}")

if __name__ == "__main__":
    main()
