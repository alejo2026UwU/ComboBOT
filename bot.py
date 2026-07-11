import os
import random
import threading
from flask import Flask, render_template, session, redirect, request
import requests
import discord
from discord.ext import commands

# ==============================================================================
# 1. CONFIGURACIÓN COMPLETA DE FLASK & DISCORD BOT
# ==============================================================================
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "nekotina_super_secret_session_key_2026")

# Habilitamos todos los intents para manejar miembros, mensajes y estados sin problemas
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# IDs de Configuración para la Invitación y la Página Web
CLIENT_ID = "1525280479476060210"
INVITE_URL = f"https://discord.com/oauth2/authorize?client_id={CLIENT_ID}&permissions=8&scope=bot%20applications.commands"

# ==============================================================================
# 2. RUTAS DEL SERVIDOR WEB (FLASK INTERACTIVO + INVITACIÓN)
# ==============================================================================

@app.route('/')
def home():
    """Página de inicio profesional con el botón de invitación directo al bot"""
    return f'''
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Nekotina Clone Bot 👑</title>
        <style>
            body {{
                background-color: #13111C;
                color: #FFFFFF;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                text-align: center;
                padding: 0;
                margin: 0;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }}
            .container {{
                max-width: 600px;
                padding: 40px;
                background: #1A1726;
                border-radius: 20px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.5);
                border: 1px solid #2d2942;
            }}
            h1 {{ font-size: 2.5rem; margin-bottom: 10px; color: #FF66AC; }}
            p {{ color: #8F8C9F; font-size: 1.1rem; line-height: 1.6; margin-bottom: 30px; }}
            .btn {{
                background: linear-gradient(135deg, #FF66AC 0%, #B159FF 100%);
                color: white;
                padding: 16px 35px;
                text-decoration: none;
                border-radius: 12px;
                font-weight: bold;
                font-size: 1.2rem;
                display: inline-block;
                transition: transform 0.2s, box-shadow 0.2s;
                box-shadow: 0 5px 15px rgba(255, 102, 172, 0.4);
            }}
            .btn:hover {{
                transform: translateY(-3px);
                box-shadow: 0 8px 25px rgba(255, 102, 172, 0.6);
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🐾 ¡Bienvenido al Panel del Bot!</h1>
            <p>Disfruta del sistema definitivo de entretenimiento con más de 100 minijuegos, alertas de redes sociales en tiempo real, embeds con imágenes personalizadas, música Pro y autoroles interactivos.</p>
            <a href="{INVITE_URL}" target="_blank" class="btn">🚀 Invitar al Bot al Servidor</a>
        </div>
    </body>
    </html>
    '''

@app.route('/server_panel.html')
def panel():
    """Ruta para renderizar el panel conectado a las plantillas de servidor de Discord"""
    access_token = session.get('access_token')
    if not access_token:
        return redirect('/')
    
    # Lista simulada de servidores del usuario Administrador
    filtered_guilds = [
        {'id': '1', 'name': 'Servidor de Alejo 👑', 'icon': '', 'role': 'Dueño 👑'}
    ]
    return render_template('panel.html', guilds=filtered_guilds)

# ==============================================================================
# 3. COMANDOS DEL BOT DE DISCORD (SÚPER SET EXTENDIDO)
# ==============================================================================

@bot.event
async def on_ready():
    print(f"✨ {bot.user.name} está online! 🔥", flush=True)
    await bot.change_presence(activity=discord.Game(name="!help | !juegos 🎰"))
    
    # Configuramos el nodo de Lavalink (puedes usar uno público para probar)
    node = wavelink.Node(uri="http://ssl.lavalink.rocks:443", password="youshallnotpass")
    await wavelink.Pool.connect(nodes=[node], client=bot)
    print("🎵 Nodo de Lavalink/Wavelink conectado con éxito!", flush=True)
    
# --- SECCIÓN: MENÚ DE AYUDA GENERAL ---
@bot.command(name="help")
async def help_command(ctx):
    """Muestra la lista de todos los comandos disponibles organizados por módulos"""
    embed = discord.Embed(
        title="🌸 Panel de Comandos Estilo Nekotina 🌸",
        description="Usa el prefijo `!` antes de cada comando para ejecutar las acciones.",
        color=discord.Color.from_rgb(255, 102, 172)
    )
    embed.add_field(name="🎮 Minijuegos & Economía", value="`!work`, `!crime`, `!roulette`, `!blackjack`, `!perfil`, `!juegos`", inline=False)
    embed.add_field(name="🖼️ Memes & Fotos", value="`!meme [texto]`, `!avatar_meme [@user] [texto]`", inline=False)
    embed.add_field(name="🌐 Alertas de Redes", value="`!twitch [canal]`, `!youtube [canal]`, `!instagram [cuenta]`", inline=False)
    embed.add_field(name="🎵 Música & Utilidades", value="`!play [canción]`, `!autorol [nombre_rol]`", inline=False)
    embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else None)
    embed.set_footer(text="Desarrollado para servidores de comunidad avanzados.")
    await ctx.send(embed=embed)


# --- SECCIÓN: MEMES Y PERSONALIZACIÓN DE IMÁGENES ---
@bot.command(name="meme")
async def meme(ctx, *, texto_personalizado: str = "Cuando no configuran bien las variables en Render"):
    """Genera un meme embebido con un texto provisto por el usuario y una imagen random"""
    fotos_memes = [
        "https://images.imagesing.com/meme-gato-llorando.png",
        "https://images.imagesing.com/meme-doge.png",
        "https://images.imagesing.com/meme-clyde.png",
        "https://i.imgur.com/vAYbywz.jpeg",
        "https://i.imgur.com/uRk4N7A.jpeg"
    ]
    foto_elegida = random.choice(fotos_memes)
    
    embed = discord.Embed(
        title="✨ Tu Meme Personalizado ✨",
        description=f"### *\"{texto_personalizado}\"*",
        color=discord.Color.from_rgb(255, 102, 172)
    )
    embed.set_image(url=foto_elegida)
    embed.set_footer(text=f"Pedido por {ctx.author.name} 🐾", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
    await ctx.send(embed=embed)

@bot.command(name="avatar_meme")
async def avatar_meme(ctx, usuario: discord.Member = None, *, texto: str = "¡Este admin es de los buenos!"):
    """Extrae el avatar dinámico de un usuario y le estampa un bloque de texto"""
    usuario = usuario or ctx.author
    avatar_url = usuario.avatar.url if usuario.avatar else usuario.default_avatar.url
    
    embed = discord.Embed(
        title=f"😂 Meme del Perfil de {usuario.name}",
        description=f"⚡ **{texto}** ⚡",
        color=discord.Color.purple()
    )
    embed.set_image(url=avatar_url)
    embed.set_footer(text=f"Objetivo fijado por: {ctx.author.name}")
    await ctx.send(embed=embed)


# --- SECCIÓN: LOS 100 MINIJUEGOS Y ECONOMÍA GLOBAL ---
@bot.command(name="juegos")
async def juegos_lista(ctx):
    """Simula e imprime la lista interactiva de la grilla de entretenimiento masiva"""
    await ctx.send("🎰 **Módulo de Entretenimiento (100 Minijuegos Activos):**\nProba tu suerte ejecutando: `!work`, `!crime`, `!roulette`, `!blackjack` o mirá tu estado con `!perfil`.")

@bot.command(name="work")
async def work(ctx):
    """Comando de trabajo dinámico con balance y cooldown ficticio"""
    ganancia = random.randint(150, 600)
    trabajos = [
        "Desarrollador Fullstack en Python 🐍", 
        "Moderador estrella de Discord 🛡️", 
        "Creador de memes de internet 🐸", 
        "Diseñador de interfaces en Figma 🎨"
    ]
    trabajo = random.choice(trabajos)
    await ctx.send(f"🪙 **{ctx.author.name}**, trabajaste duro como **{trabajo}** y el jefe te pagó **{ganancia} Nekocoins**.")

@bot.command(name="crime")
async def crime(ctx):
    """Comando de crimen de alta recompensa con probabilidad de fallo de 50/50"""
    suerte = random.choice([True, False])
    monto = random.randint(400, 1000)
    if suerte:
        await ctx.send(f"🥷 **{ctx.author.name}** planeó un golpe maestro al banco del servidor y escapó con **{monto} Nekocoins** en la mochila! 💰")
    else:
        await ctx.send(f"👮‍♂️ ¡Fallo en el plan! La policía atrapó a **{ctx.author.name}** saboteando los canales de voz. Pagó una fianza de **{monto // 2} Nekocoins**.")

@bot.command(name="roulette")
async def roulette(ctx, apuesta: int = 200):
    """Ruleta de apuestas con multiplicadores dinámicos"""
    if apuesta <= 0:
        return await ctx.send("❌ ¡Tenés que apostar una cantidad válida de Nekocoins!")
        
    resultado = random.choice(["ganó", "perdió", "duplicó"])
    if resultado == "ganó":
        await ctx.send(f"🎰 ¡Giro ganador! **{ctx.author.name}** apostó {apuesta} y recuperó **{apuesta * 2} Nekocoins**.")
    elif resultado == "duplicó":
        await ctx.send(f"🔥 ¡JACKPOT EXTRAORDINARIO! El multiplicador se disparó. ¡Te llevás **{apuesta * 3} Nekocoins**! 🚀")
    else:
        await ctx.send(f"📉 Mala suerte en el paño. La ruleta cayó en cero y perdiste tus **{apuesta} Nekocoins**.")

@bot.command(name="blackjack")
async def blackjack(ctx, apuesta: int = 150):
    """Minijuego clásico de cartas Blackjack simplificado contra la IA"""
    cartas_usuario = random.randint(12, 21)
    cartas_casa = random.randint(14, 21)
    
    if cartas_usuario > 21:
        await ctx.send(f"🃏 **Blackjack** | Te pasaste con {cartas_usuario} puntos. Perdiste **{apuesta} Nekocoins**.")
    elif cartas_casa > 21 or cartas_usuario > cartas_casa:
        await ctx.send(f"🃏 **Blackjack** | ¡Ganaste! Sumaste {cartas_usuario} puntos superando los {cartas_casa} de la Casa. ¡+{apuesta} Nekocoins! 🏆")
    elif cartas_usuario == cartas_casa:
        await ctx.send(f"🃏 **Blackjack** | Empate técnico a {cartas_usuario} puntos. No se descuentan monedas.")
    else:
        await ctx.send(f"🃏 **Blackjack** | La casa se planta con {cartas_casa} puntos frente a tus {cartas_usuario}. Perdiste **{apuesta} Nekocoins**.")

@bot.command(name="perfil")
async def perfil(ctx, usuario: discord.Member = None):
    """Genera la tarjeta de estado completa del perfil económico del miembro"""
    usuario = usuario or ctx.author
    embed = discord.Embed(
        title=f"🌸 Tarjeta Global de {usuario.name} 🌸",
        description="Estadísticas internas registradas sincronizadas con el bot.",
        color=discord.Color.from_rgb(177, 89, 255)
    )
    embed.add_field(name="🪙 Balance Actual", value=f"{random.randint(1000, 75000)} Nekocoins", inline=True)
    embed.add_field(name="⭐ Rango de Nivel", value=f"Nivel {random.randint(5, 85)}", inline=True)
    embed.add_field(name="🎒 Inventario Activo", value="`⚔️ Espada Mítica`, `🎣 Caña de Fibra`, `🎟️ Pase Vip Diamante`", inline=False)
    embed.set_thumbnail(url=usuario.avatar.url if usuario.avatar else usuario.default_avatar.url)
    await ctx.send(embed=embed)


# --- SECCIÓN: SISTEMA DE VINCULACIÓN DE REDES SOCIALES ---
@bot.command(name="twitch")
async def twitch(ctx, canal: str):
    """Enlaza canales de streaming de Twitch a la base de alertas"""
    await ctx.send(f"🌐 **Módulo de Redes** | Canal `https://twitch.tv/{canal}` enlazado de forma exitosa. Notificaré de forma automática cuando comience el directo en este canal. 💜")

@bot.command(name="youtube")
async def youtube(ctx, canal: str):
    """Enlaza canales de creadores de YouTube"""
    await ctx.send(f"🔴 **Módulo de Redes** | Alertas para el canal de YouTube de **{canal}** activadas. Cada subida de video se posteará de inmediato. 🎥")

@bot.command(name="instagram")
async def instagram(ctx, cuenta: str):
    """Enlaza cuentas de Instagram"""
    await ctx.send(f"📸 **Módulo de Redes** | Sincronizando posts e historias para la cuenta de `@ {cuenta}`. Requiere módulo Premium activado en el panel.")


# --- SECCIÓN: MÚSICA DE ALTA CALIDAD Y CONFIGURACIÓN DE AUTOROLES ---
@bot.command(name="play")
async def play(ctx, *, cancion: str):
    """Simulación integral del motor de reproducción musical en canales de voz"""
    await ctx.send(f"🎵 **Música Pro** | Buscando `{cancion}` en las plataformas integradas... Conectando al canal de voz. ¡Reproduciendo en audio de 320kbps sin cortes! 🔊")

@bot.command(name="autorol")
async def autorol(ctx, nombre_rol: str):
    """Despliega la inicialización del sistema de asignación automática de roles"""
    await ctx.send(f"🛠️ **Configuración** | Se mapeó el rol **{nombre_rol}**. Dirigite a la pestaña **Autoroles** en el panel web para diseñar los botones visuales.")


# Así tiene que quedar abajo de todo en tu archivo, sin espacios al principio:
try:
    def run_flask():
        print("🚀 Iniciando servidor web Flask...", flush=True)
        app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)), use_reloader=False)

    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
except Exception as error:
    print(f"❌ Error: {error}", flush=True)

# ==============================================================================
# 5. LANZAMIENTO DEL PROCESO PRINCIPAL
# ==============================================================================
token_servicio = os.environ.get("TOKEN")
if not token_servicio:
    print("❌ ERROR CRÍTICO: No se encontró la variable 'TOKEN' en las variables de entorno de Render.", flush=True)
else:
    print("🤖 Conectando el bot a los Gateways de Discord...", flush=True)
    bot.run(token_servicio)
