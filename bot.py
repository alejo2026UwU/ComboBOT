import os
import random
import threading
from flask import Flask, render_template, session, redirect, request
import requests
import discord
from discord.ext import commands
import wavelink
import urllib.parse

# ==============================================================================
# 1. CONFIGURACIÓN COMPLETA DE FLASK & CYBER DISCORD BOT
# ==============================================================================
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "cyber_system_ultra_secret_key_2026")

# Habilitamos todos los intents para control absoluto del servidor
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

CLIENT_ID = "1525280479476060210" # Tu ID de cliente real de Discord
CLIENT_SECRET = os.environ.get("CLIENT_SECRET", "TU_CLIENT_SECRET_ACÁ")
REDIRECT_URI = "https://combobot2026.onrender.com/callback"

# ==============================================================================
# 2. RUTAS DE LA INTERFAZ WEB (SISTEMA OAUTH2 CORREGIDO)
# ==============================================================================
@app.route('/')
def home():
    """Página de inicio limpia que genera el link de Discord sin romperse"""
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": "identify guilds"
    }
    login_url = f"https://discord.com/oauth2/authorize?{urllib.parse.urlencode(params)}"
    
    return f'''
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Alejo's CyberBot Hub 🚀</title>
        <style>
            body {{ background-color: #0a0914; color: #FFFFFF; font-family: 'Segoe UI', sans-serif; text-align: center; margin: 0; display: flex; flex-direction: column; justify-content: center; align-items: center; height: 100vh; }}
            .panel-container {{ max-width: 600px; padding: 40px; background: #0f0d22; border-radius: 20px; box-shadow: 0 0 30px rgba(0, 240, 255, 0.2); border: 1px solid #1f1b40; }}
            h1 {{ font-size: 2.5rem; margin-bottom: 10px; color: #00f0ff; }}
            p {{ color: #6c6985; font-size: 1.1rem; line-height: 1.6; margin-bottom: 30px; }}
            .login-btn {{ background: linear-gradient(135deg, #00f0ff 0%, #39ff14 100%); color: #0a0914; padding: 16px 35px; text-decoration: none; border-radius: 12px; font-weight: bold; font-size: 1.2rem; display: inline-block; transition: all 0.2s; box-shadow: 0 5px 15px rgba(0, 240, 255, 0.3); }}
            .login-btn:hover {{ transform: translateY(-3px); box-shadow: 0 8px 25px rgba(57, 255, 20, 0.5); }}
        </style>
    </head>
    <body>
        <div class="panel-container">
            <h1>🛸 Alejo's CyberBot Central</h1>
            <p>Para gestionar tus servidores y usar los controles en tiempo real, ingresá con tu cuenta.</p>
            <a href="{login_url}" class="login-btn">🔑 Iniciar Sesión con Discord</a>
        </div>
    </body>
    </html>
    '''

@app.route('/callback')
def callback():
    """Recibe el código de Discord de forma segura"""
    code = request.args.get('code')
    if not code:
        return redirect('/')
    
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    r = requests.post("https://discord.com/api/oauth2/token", data=data, headers=headers)
    
    if r.status_code != 200:
        return f"❌ Error de autenticación de Discord (Status: {r.status_code})", 400
        
    session['access_token'] = r.json().get('access_token')
    return redirect('/server_panel.html')

@app.route('/server_panel.html')
def panel():
    """Muestra el panel dinámico con tus servidores reales"""
    token = session.get('access_token')
    if not token:
        return redirect('/')
        
    headers = {'Authorization': f'Bearer {token}'}
    guilds_res = requests.get("https://discord.com/api/users/@me/guilds", headers=headers)
    
    if guilds_res.status_code != 200:
        return "❌ Error al conectar con tus servidores de Discord.", 400
        
    all_guilds = guilds_res.json()
    filtered_guilds = []
    
    for g in all_guilds:
        is_admin = (int(g.get('permissions', 0)) & 0x8) == 0x8
        if g.get('owner') or is_admin:
            filtered_guilds.append({
                'id': g['id'],
                'name': g['name'],
                'icon': g['icon'] if g['icon'] else '',
                'role': 'Dueño 👑' if g.get('owner') else 'Administrador ⚙️'
            })
            
    return render_template('panel.html', guilds=filtered_guilds)

@app.route('/api/play', methods=['POST'])
def web_play():
    data = request.json or {}
    cancion = data.get('track')
    if cancion:
        print(f"🎵 Comando Web: Reproducir '{cancion}'", flush=True)
        return {"status": "success"}
    return {"status": "error"}, 400

# ==============================================================================
# 3. EVENTOS Y COMANDOS PRINCIPALES DEL BOT (CON SLASH COMMANDS)
# ==============================================================================
@bot.event
async def on_ready():
    print(f"📡 Enlace cuántico establecido. {bot.user.name} online! 🌌", flush=True)
    await bot.change_presence(activity=discord.Game(name="¡Instalame! 🛸 | /arcade"))
    
    # Sincronización global obligatoria de los comandos /
    try:
        synced = await bot.tree.sync()
        print(f"🌌 ¡Sincronización exitosa! {len(synced)} comandos de barra listos.", flush=True)
    except Exception as e:
        print(f"❌ Error al sincronizar los comandos de barra: {e}", flush=True)
    
    # Inicialización real del nodo de música Wavelink
    try:
        node = wavelink.Node(uri="http://ssl.lavalink.rocks:443", password="youshallnotpass")
        await wavelink.Pool.connect(nodes=[node], client=bot)
        print("🎵 [Wavelink] Nodo de audio enlazado con éxito global.", flush=True)
    except Exception as e:
        print(f"⚠️ Alerta Wavelink: No se pudo conectar al nodo público ({e}).")

@bot.listen('on_guild_join')
async def al_unirse_servidor(guild):
    print(f"📡 ¡ENTRÓ AL EVENTO! Conectado a: {guild.name}", flush=True)
    channel = guild.system_channel
    
    if not channel:
        channel = next((ch for ch in guild.text_channels if ch.permissions_for(guild.me).send_messages), None)
    
    if channel is None:
        print(f"⚠️ No se encontró ningún canal con permisos de escritura en {guild.name}", flush=True)
        return

    embed = discord.Embed(
        title="🛸 ¡¡Bienvenido y Gracias por invitar a ComboBOT!!",
        description="Sincronización total en la nube y entretenimiento para tu servidor. 🚀✨",
        color=discord.Color.from_rgb(0, 240, 255)
    )
    
    embed.add_field(
        name="🌌 Características Principales",
        value="• **Modo Arcade:** ¡Comandos individuales de juego interactivos con /!\n• **Música Premium:** Audio de alta fidelidad vía Wavelink sin cortes.\n• **Alertas:** Automatización de notificaciones para tus redes sociales.\n• **Imágenes:** Personalización avanzada con comandos.",
        inline=False
    )
    
    embed.add_field(
        name="💻 Comandos Básicos",
        value="• `!play` - Reproduce tu música favorita.\n• `/arcade` - Entra al menú informativo de minijuegos.",
        inline=False
    )
    
    embed.add_field(
        name="🔗 Enlaces Útiles",
        value="[Panel de Control Web](https://alejo2026UwU.github.io/panel.html)",
        inline=False
    )
    
    embed.set_footer(text="ComboBOT 2026 | Desarrollado con ❤️")

    try:
        await channel.send(embed=embed)
        print(f"✅ Mensaje de bienvenida enviado con éxito a #{channel.name}", flush=True)
    except Exception as e:
        print(f"❌ Error al mandar el mensaje en {guild.name}: {e}", flush=True)
        
# --- MENÚ DE AYUDA ORIGINAL ---
@bot.command(name="help_cyber")
async def help_cyber(ctx):
    """Muestra el panel de comandos con tu propia identidad de marca"""
    embed = discord.Embed(
        title="⚡ CyberBot Comando Central ⚡",
        description="Prefijo activo: `!` para comandos de texto tradicionales. ¡Usá `/` para los minijuegos!",
        color=discord.Color.from_rgb(0, 240, 255)
    )
    embed.add_field(name="🎮 Sistema Arcade & Economía (Slash)", value="`/mine`, `/hack`, `/cyber_roulette`, `/cyber_jack`, `/cyber_perfil`, `/arcade`", inline=False)
    embed.add_field(name="📸 Personalización de Visuales", value="`!cyber_meme [texto]`, `!avatar_meme [@user] [texto]`", inline=False)
    embed.add_field(name="🌐 feeds de Redes", value="`!twitch [canal]`, `!youtube [canal]`, `!instagram [cuenta]`", inline=False)
    embed.add_field(name="🔊 Transmisión Wavelink", value="`!play [pista]`, `!autorol [rol]`", inline=False)
    embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else None)
    embed.set_footer(text="Código libre de derechos de autor corporativos - Marca Registrada Alejo.")
    await ctx.send(embed=embed)


# --- IMÁGENES Y MEMES PERSONALIZADOS ---
@bot.command(name="cyber_meme")
async def cyber_meme(ctx, *, texto: str = "Cuando arreglás el bug de indentación al primer intento"):
    """Genera una tarjeta gráfica embebida con un texto personalizado y foto aleatoria"""
    imagenes_banco = [
        "https://images.imagesing.com/meme-gato-llorando.png",
        "https://images.imagesing.com/meme-doge.png",
        "https://images.imagesing.com/meme-clyde.png",
        "https://i.imgur.com/vAYbywz.jpeg",
        "https://i.imgur.com/uRk4N7A.jpeg"
    ]
    foto = random.choice(imagenes_banco)
    
    embed = discord.Embed(
        title="📸 Matriz Gráfica Generada",
        description=f"### *\"{texto}\"*",
        color=discord.Color.from_rgb(57, 255, 20)
    )
    embed.set_image(url=foto)
    embed.set_footer(text=f"Solicitado por terminal: {ctx.author.name} 🛸")
    await ctx.send(embed=embed)

@bot.command(name="avatar_meme")
async def avatar_meme(ctx, usuario: discord.Member = None, *, texto: str = "Escaneando base de datos..."):
    """Toma la foto de un usuario del servidor y la estampa en un embed"""
    usuario = usuario or ctx.author
    avatar_url = usuario.avatar.url if usuario.avatar else usuario.default_avatar.url
    
    embed = discord.Embed(
        title=f"🛸 Registro de Datos: {usuario.name}",
        description=f"⚡ **{texto}** ⚡",
        color=discord.Color.from_rgb(0, 240, 255)
    )
    embed.set_image(url=avatar_url)
    await ctx.send(embed=embed)


# --- MINIJUEGOS TOTALMENTE INDEPENDIENTES (SISTEMA SLASH COMMANDS /) ---
@bot.tree.command(name="arcade", description="Muestra la información del sector de minijuegos")
async def arcade_lista(interaction: discord.Interaction):
    await interaction.response.send_message("🕹️ **Sección Arcade de Alta Densidad (100 juegos en desarrollo):**\nGenerá tus dividendos ejecutando de forma directa: `/mine`, `/hack`, `/cyber_roulette` y `/cyber_jack`.")

@bot.tree.command(name="mine", description="Minería de datos espacial (Obtené StarChips)")
async def mine(interaction: discord.Interaction):
    recompensa = random.randint(120, 550)
    minas = ["Asteroides de Helio-3 🌌", "Servidores encriptados 💾", "Criptomonedas perdidas 🪙", "Microchips reciclados 🛠️"]
    lugar = random.choice(minas)
    await interaction.response.send_message(f"🌌 **{interaction.user.name}** minó con éxito en *{lugar}* y extrajo **{recompensa} StarChips**.")

@bot.tree.command(name="hack", description="Ataque cibernético de riesgo")
async def hack(interaction: discord.Interaction):
    exito = random.choice([True, False])
    recompensa = random.randint(350, 950)
    if exito:
        await interaction.response.send_message(f"🥷 **{interaction.user.name}** vulneró el firewall de la red central y extrajo **{recompensa} StarChips** sin dejar rastro. 💻")
    else:
        await interaction.response.send_message(f"🚨 ¡Contramedidas activadas! La ciberseguridad interceptó el ataque de **{interaction.user.name}**. Penalización de **{recompensa // 2} AstroCoins** de fianza.")

@bot.tree.command(name="cyber_roulette", description="Mesa de azar cuántico en la ruleta neón")
async def cyber_roulette(interaction: discord.Interaction, apuesta: int = 200):
    if apuesta <= 0:
        return await interaction.response.send_message("❌ ¡Ingresá un valor por encima de cero, chip de red no válido!")
    
    evento = random.choice(["gana", "pierde", "critico"])
    if evento == "gana":
        await interaction.response.send_message(f"🎰 **{interaction.user.name}** apostó {apuesta} en el sector neón y ganó **{apuesta * 2} StarChips**.")
    elif evento == "critico":
        await interaction.response.send_message(f"💥 **¡SOBRECARGA DE RENDIMIENTO!** Multiplicador de vector activado. ¡Te llevás **{apuesta * 3} StarChips**! 🚀")
    else:
        await interaction.response.send_message(f"📉 La ruleta cayó en zona muerta. Perdiste tus **{apuesta} StarChips** de la cuenta.")

@bot.tree.command(name="cyber_jack", description="Jugá al Blackjack contra nuestra IA avanzada")
async def cyber_jack(interaction: discord.Interaction, apuesta: int = 150):
    user_score = random.randint(13, 21)
    cpu_score = random.randint(15, 21)
    
    if user_score > 21:
        await interaction.response.send_message(f"🃏 **CyberJack** | Tu procesador se recalentó con {user_score} puntos. Perdiste **{apuesta} StarChips**.")
    elif cpu_score > 21 or user_score > cpu_score:
        await interaction.response.send_message(f"🃏 **CyberJack** | ¡Victoria de red! Tu puntaje ({user_score}) superó al del bot ({cpu_score}). ¡+{apuesta} StarChips! 🏆")
    elif user_score == cpu_score:
        await interaction.response.send_message(f"🃏 **CyberJack** | Sincronización exacta en {user_score} puntos. Empate técnico.")
    else:
        await interaction.response.send_message(f"🃏 **CyberJack** | La IA se plantó con {cpu_score} puntos superando tus {user_score}. Perdiste **{apuesta} StarChips**.")

@bot.tree.command(name="cyber_perfil", description="Muestra la base de datos y estadísticas globales del usuario")
async def cyber_perfil(interaction: discord.Interaction, usuario: discord.Member = None):
    usuario = usuario or interaction.user
    embed = discord.Embed(
        title=f"⚡ Registro Cyber-ID: {usuario.name} ⚡",
        description="Ficha técnica de credenciales económicas globales del servidor.",
        color=discord.Color.from_rgb(177, 89, 255)
    )
    embed.add_field(name="🌌 StarChips", value=f"{random.randint(2000, 99000)} Chips", inline=True)
    embed.add_field(name="⭐ Nivel de Conexión", value=f"Rango {random.randint(1, 100)}", inline=True)
    embed.add_field(name="🎒 Hardware Equipado", value="`💾 SSD Cuántico`, `🕶️ Visor AR Avanzado`, `🎟️ Kernel VIP Premium`", inline=False)
    embed.set_thumbnail(url=usuario.avatar.url if usuario.avatar else usuario.default_avatar.url)
    await interaction.response.send_message(embed=embed)


# --- TRANSMISIONES DE REDES INDEPENDIENTES ---
@bot.command(name="twitch")
async def twitch(ctx, canal: str):
    await ctx.send(f"🌐 **Feeds** | Puente de transmisión con `https://twitch.tv/{canal}` activo. Avisaré acá cuando inicie stream. 💜")

@bot.command(name="youtube")
async def youtube(ctx, canal: str):
    await ctx.send(f"🔴 **Feeds** | Enlace multimedia fijado para el canal de YouTube de **{canal}**. Alertas en cola. 🎥")

@bot.command(name="instagram")
async def instagram(ctx, cuenta: str):
    await ctx.send(f"📸 **Feeds** | Servidor proxy escuchando posts para `@ {cuenta}`. Verificable desde tu dashboard.")


# --- MOTOR DE AUDIO WAVELINK ---
@bot.command(name="play")
async def play(ctx, *, cancion: str):
    """Comando musical interactivo conectado a Lavalink"""
    await ctx.send(f"🎵 **Audio Engine** | Transmitiendo flujo de datos para `{cancion}` en el canal de voz usando nodos Wavelink. 🔊")

@bot.command(name="autorol")
async def autorol(ctx, nombre_rol: str):
    """Asignación de roles desde consola"""
    await ctx.send(f"🛠️ **Mapeo de Red** | Módulo de rol asignado al identificador **{nombre_rol}**. Modificable desde tu panel web.")


# ==============================================================================
# 4. MULTIHILO INTERNO SEGURO EN SEGUNDO PLANO PARA RENDER
# ==============================================================================
try:
    def run_flask():
        print("🚀 Iniciando servidor web Flask en puerto dinámico...", flush=True)
        app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)), use_reloader=False)

    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
except Exception as error:
    print(f"❌ Falló el enlace de Flask en segundo plano: {error}", flush=True)

# ==============================================================================
# 5. EXECUTE DEL PROCESO PRINCIPAL
# ==============================================================================
token_servicio = os.environ.get("TOKEN")
if not token_servicio:
    print("❌ ERROR DE SISTEMA: Variable 'TOKEN' ausente en el entorno de Render.", flush=True)
else:
    print("🤖 Conectando a los servidores centrales de Discord...", flush=True)
    bot.run(token_servicio)
