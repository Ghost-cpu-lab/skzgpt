import discord
from discord.ext import commands
from groq import Groq
import os
import json
import requests
from dotenv import load_dotenv

# ====================== CARREGAR VARIÁVEIS ======================
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TENOR_API_KEY = os.getenv("TENOR_API_KEY")

# ====================== INICIALIZAÇÃO ======================
client = Groq(api_key=GROQ_API_KEY)
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="/", intents=intents)
LOG_CHANNEL_ID = None  # opcional: ID do canal de logs

@bot.event
async def on_ready():
    print(f"✅ Bot online como {bot.user}")
    await bot.tree.sync()
    print("🌐 Comandos sincronizados!")

async def send_log(guild: discord.Guild, mensagem: str):
    if LOG_CHANNEL_ID:
        canal = guild.get_channel(LOG_CHANNEL_ID)
        if canal:
            await canal.send(mensagem)

# ====================== FUNÇÃO GIF ======================
def buscar_gif(termo):
    url = f"https://tenor.googleapis.com/v2/search?q={termo}&key={TENOR_API_KEY}&limit=1"
    res = requests.get(url).json()
    try:
        return res["results"][0]["media_formats"]["gif"]["url"]
    except (KeyError, IndexError):
        return None

# ====================== COMANDO PRINCIPAL ======================
@bot.tree.command(name="skgpt", description="Chatbot IA full power")
async def skgpt(interaction: discord.Interaction, mensagem: str):
    await interaction.response.defer(ephemeral=False)
    guild = interaction.guild
    resultados = []

    termo_lower = mensagem.lower()

    # ====================== GIF DIRETO ======================
    if "gif" in termo_lower:
        url = buscar_gif(mensagem)
        if url:
            await interaction.followup.send(url)
            resultados.append(f"✅ GIF enviado: {url}")
        else:
            resultados.append(f"❌ Não encontrei GIF para: {mensagem}")
        await send_log(guild, f"Usuário {interaction.user} pediu GIF: {mensagem}\n" + "\n".join(resultados))
        return

    # ====================== CHAT / COMANDOS ADMIN ======================
    prompt = f"""
Você é um assistente de servidor Discord.
Pode responder perguntas como ChatGPT, criar/editar/deletar embeds, canais e cargos, alterar permissões e limpar mensagens.
Retorne sempre JSON válido com a lista de ações:
[{{"action":"resposta/criar_embed/criar_canal/criar_cargo/editar_canal/deletar_canal/editar_cargo/deletar_cargo/limpar_mensagens","resposta":"","titulo":"","descricao":"","cor":"","nome":"","permissoes":{{"read_messages": true,"manage_messages": false}},"mensagens":10}}]
Instrução do usuário: "{mensagem}"
"""

    try:
        resposta = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role":"user","content":prompt}],
            temperature=0
        )
        conteudo = resposta.choices[0].message.content
        acoes = json.loads(conteudo)

        for acao in acoes:
            tipo = acao.get("action")

            # ================= SEGURANÇA =================
            if tipo not in ["resposta"] and not interaction.user.guild_permissions.administrator:
                resultados.append("❌ Apenas admins podem executar esta ação.")
                continue

            try:
                # ================= RESPOSTA =================
                if tipo == "resposta":
                    texto = acao.get("resposta", "🤖 Não sei como responder.")
                    await interaction.followup.send(texto)
                    resultados.append("✅ Resposta enviada")

                # ================= EMBED =================
                elif tipo == "criar_embed":
                    embed = discord.Embed(
                        title=acao.get("titulo", ""),
                        description=acao.get("descricao", ""),
                        color=int(acao.get("cor", "5865F2"), 16)
                    )
                    if acao.get("imagem"):
                        embed.set_image(url=acao["imagem"])
                    if acao.get("thumbnail"):
                        embed.set_thumbnail(url=acao["thumbnail"])
                    if acao.get("footer"):
                        embed.set_footer(text=acao["footer"])
                    await interaction.followup.send(embed=embed)
                    resultados.append("✅ Embed criada")

                # ================= CANAIS =================
                elif tipo == "criar_canal":
                    nome = acao.get("nome", "novo-canal")
                    canal = await guild.create_text_channel(nome)
                    resultados.append(f"✅ Canal criado: {canal.mention}")

                elif tipo == "editar_canal":
                    canal = discord.utils.get(guild.channels, name=acao.get("nome", ""))
                    if canal:
                        await canal.edit(name=acao.get("novo_nome", canal.name))
                        resultados.append(f"✅ Canal editado: {canal.name}")
                    else:
                        resultados.append(f"❌ Canal não encontrado: {acao.get('nome')}")

                elif tipo == "deletar_canal":
                    canal = discord.utils.get(guild.channels, name=acao.get("nome", ""))
                    if canal:
                        await canal.delete()
                        resultados.append(f"✅ Canal deletado: {acao.get('nome')}")
                    else:
                        resultados.append(f"❌ Canal não encontrado: {acao.get('nome')}")

                # ================= CARGOS =================
                elif tipo == "criar_cargo":
                    nome = acao.get("nome", "Novo Cargo")
                    role = await guild.create_role(name=nome)
                    resultados.append(f"✅ Cargo criado: {role.name}")

                elif tipo == "editar_cargo":
                    role = discord.utils.get(guild.roles, name=acao.get("nome", ""))
                    if role:
                        await role.edit(name=acao.get("novo_nome", role.name))
                        resultados.append(f"✅ Cargo editado: {role.name}")
                    else:
                        resultados.append(f"❌ Cargo não encontrado: {acao.get('nome')}")

                elif tipo == "deletar_cargo":
                    role = discord.utils.get(guild.roles, name=acao.get("nome", ""))
                    if role:
                        await role.delete()
                        resultados.append(f"✅ Cargo deletado: {acao.get('nome')}")
                    else:
                        resultados.append(f"❌ Cargo não encontrado: {acao.get('nome')}")

                # ================= LIMPAR MENSAGENS =================
                elif tipo == "limpar_mensagens":
                    canal = discord.utils.get(guild.channels, name=acao.get("nome", ""))
                    if canal:
                        mensagens = acao.get("mensagens", 100)
                        deleted = await canal.purge(limit=mensagens)
                        resultados.append(f"✅ {len(deleted)} mensagens apagadas no canal {canal.name}")
                    else:
                        resultados.append(f"❌ Canal não encontrado: {acao.get('nome')}")

                else:
                    resultados.append(f"❌ A IA não reconheceu a ação: {tipo}")

            except Exception as e:
                resultados.append(f"❌ Erro ao executar {tipo}: {e}")

        await send_log(guild, f"Usuário {interaction.user} executou: {mensagem}\nResultados:\n" + "\n".join(resultados))

    except json.JSONDecodeError:
        await interaction.followup.send("❌ A IA retornou JSON inválido.")
    except Exception as e:
        await interaction.followup.send(f"❌ Erro: {e}")

bot.run(DISCORD_TOKEN)
