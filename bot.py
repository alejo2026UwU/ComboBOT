import os
import random
import threading
import asyncio
from flask import Flask, render_template, session, redirect, request
import requests
import discord
from discord.ext import commands
import urllib.parse
import wavelink

# ==============================================================================
# 1. CONFIGURACIÓN COMPLETA DE FLASK & CYBER DISCORD BOT
# ==============================================================================
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "cyber_system_ultra_secret_key_2026")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

CLIENT_ID = "1525280479476060210"
CLIENT_SECRET = os.environ.get("CLIENT_SECRET", "TU_CLIENT_SECRET_ACÁ")
REDIRECT_URI = "https://combobot2026.onrender.com/callback"

# CONFIGURACIÓN DE LOS JUEGOS
JUEGOS_DETALLES = {
    1: {"name": "Duelo de Espadas", "hit": "te encajó una estocada letal", "crit": "¡te decapitó con un crítico medieval!"},
    # ... (Se mantienen todos los 100 juegos iguales que antes)
}

# (Se mantienen todas las rutas de Flask idénticas: @app.route('/'), /callback, /server_panel.html)

# ==============================================================================
# 3. CLASES DE VISTA INTERACTIVE (SISTEMA DE BOTONES 1V1)
# ==============================================================================
class JuegoMasivoView(discord.ui.View):
    def __init__(self, j1, j2, numero, config):
        super().__init__(timeout=90)
        self.j1, self.j2 = j1, j2
        self.numero = numero
        self.nombre = config["name"]
        self.hit_txt = config["hit"]
        self.crit_txt = config["crit"]
        self.hp = {j1.id: 100, j2.id: 100}
        self.turno = j1
        self.rival = j2

    async def actualizar(self, inter, evento):
        embed = discord.Embed(title=f"🕹️ JUEGO #{self.numero}: {self.nombre}", color=discord.Color.red())
        embed.add_field(name=f"🥊 {self.j1.name}", value=f"❤️ **HP:** `{self.hp[self.j1.id]}/100`", inline=True)
        embed.add_field(name=f"🥊 {self.j2.name}", value=f"❤️ **HP:** `{self.hp[self.j2.id]}/100`", inline=True)
        embed.description = f"{evento}\n\n⚔️ **Turno de atacar:** {self.turno.mention}"

        if self.hp[self.rival.id] <= 0:
            self.stop()
            embed.description = f"🏆 🎉 **¡{self.turno.mention} DESTROZÓ A {self.rival.mention} EN EL JUEGO DE {self.nombre.upper()}!**"
            await inter.response.edit_message(embed=embed, view=None)
        else:
            await inter.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="💥 Atacar Seguro", style=discord.ButtonStyle.primary)
    async def hit_btn(self, inter, btn):
        if inter.user.id != self.turno.id: 
            return
        dmg = random.randint(10, 20)
        self.hp[self.rival.id] -= dmg
        txt = f"⚔️ {self.turno.mention} {self.hit_txt} a {self.rival.mention} haciendo `{dmg} DMG`."
        if self.hp[self.rival.id] > 0: 
            self.turno, self.rival = self.rival, self.turno
        await self.actualizar(inter, txt)

    @discord.ui.button(label="⚡ Golpe Arriesgado", style=discord.ButtonStyle.danger)
    async def crit_btn(self, inter, btn):
        if inter.user.id != self.turno.id: 
            return
        if random.randint(1, 2) == 1:
            dmg = random.randint(25, 50)
            self.hp[self.rival.id] -= dmg
            txt = f"🔥💥 {self.turno.mention} {self.crit_txt} contra {self.rival.mention} quitando `{dmg} DMG`!"
        else:
            txt = f"💨 {self.turno.mention} intentó una jugada arriesgada en **{self.nombre}** pero la manqueó feo."
        if self.hp[self.rival.id] > 0: 
            self.turno, self.rival = self.rival, self.turno
        await self.actualizar(inter, txt)

# ==============================================================================
# 4. EVENTOS Y CONEXIÓN SEGURA A LAVALINK
# ==============================================================================
async def conectar_node():
    """Probando con otro nodo de Lavalink público y activo 🛡️🎵"""
    try:
        # Probamos con este servidor que está online:
        node = wavelink.Node(uri="https://mi-lavalink.onrender.com:8080", password="youshallnotpass")
        await wavelink.Pool.connect(nodes=[node], client=bot)
        print("🎵 [Lavalink] ¡Conectado exitosamente al nuevo nodo! 🎸", flush=True)
    except Exception as e:
        print(f"⚠️ [Lavalink Alert] Falló la conexión: {e}", flush=True)

@bot.event
async def on_ready():
    print(f"📡 Enlace cuántico establecido. {bot.user.name} online! 🌌", flush=True)
    
    # RPC Activo 🚀
    activity = discord.Activity(
        type=discord.ActivityType.watching, 
        name="¡ComboBOT Premium! 🚀 | /help_cyber 🛸"
    )
    await bot.change_presence(activity=activity)
    
    # Conectamos música en segundo plano de forma segura
    await conectar_node()
    
    try:
        synced = await bot.tree.sync()
        print(f"🌌 Sincronización exitosa: {len(synced)} comandos globales listos.", flush=True)
    except Exception as e:
        print(f"❌ Error al sincronizar comandos: {e}", flush=True)

@bot.event
async def on_wavelink_node_ready(payload: wavelink.NodeReadyEvent):
    print(f"✅ Nodo de Wavelink listo: {payload.node.identifier}", flush=True)

# ==============================================================================
# 🎮 COMANDOS DE MÚSICA SEPARADOS POR PLATAFORMA (YT, SPOTIFY, SOUNDCLOUD)
# ==============================================================================

async def reproducir_tema(interaction: discord.Interaction, busqueda: str, source):
    """Función interna para conectar y reproducir de forma genérica 🛠️"""
    if not interaction.user.voice:
        return await interaction.followup.send("❌ ¡Tenés que estar en un canal de voz para usar esto! 🎤")
    
    if not wavelink.Pool.nodes:
        return await interaction.followup.send("⚠️ El servidor de música está temporalmente caído. 🛠️")

    player: wavelink.Player = interaction.guild.voice_client

    if not player:
        try:
            player = await interaction.user.voice.channel.connect(cls=wavelink.Player)
        except Exception as e:
            return await interaction.followup.send(f"❌ Error al conectar al canal de voz: {e}")

    try:
        if busqueda.startswith("http://") or busqueda.startswith("https://"):
            tracks = await wavelink.Playable.search(busqueda)
        else:
            tracks = await wavelink.Playable.search(busqueda, source=source)
    except Exception as e:
        return await interaction.followup.send(f"❌ Error al buscar el tema: {e} 😢")

    if not tracks:
        return await interaction.followup.send("❌ No encontré ninguna canción. 😢")

    track = tracks[0]
    await player.queue.put(track)
    
    if not player.playing:
        await player.play(player.queue.get())
        await interaction.followup.send(f"🎶 Empezando a sonar: **{track.title}** 🚀")
    else:
        await interaction.followup.send(f"➕ Añadida a la lista: **{track.title}** 📝")


# 1️⃣ --- YOUTUBE PLAY ---
@bot.tree.command(name="play_yt", description="Reproduce música de YouTube 🔴")
async def play_yt(interaction: discord.Interaction, busqueda: str):
    await interaction.response.defer()
    await reproducir_tema(interaction, busqueda, wavelink.TrackSource.YouTube)

@play_yt.autocomplete("busqueda")
async def yt_autocomplete(interaction: discord.Interaction, current: str):
    if not current or len(current) < 2:
        return [discord.app_commands.Choice(name="🔴 Escribí el nombre del video o canción...", value=current)]
    try:
        # Usamos el prefijo de búsqueda explícito de Lavalink para evitar vacíos
        tracks = await wavelink.Playable.search(f"ytsearch:{current}")
        if tracks:
            return [discord.app_commands.Choice(name=f"🎥 {t.title[:80]}", value=t.uri) for t in tracks[:5]]
    except Exception:
        pass
    return [discord.app_commands.Choice(name=f"🔍 Buscar '{current[:50]}' en YouTube", value=current)]


# 2️⃣ --- SPOTIFY PLAY ---
@bot.tree.command(name="play_spotify", description="Reproduce música de Spotify 🟢")
async def play_spotify(interaction: discord.Interaction, busqueda: str):
    await interaction.response.defer()
    # Nota: Si usás Wavelink 3, Spotify se mapea mediante el plugin LavaSrc
    await reproducir_tema(interaction, busqueda, wavelink.TrackSource.Spotify)

@play_spotify.autocomplete("busqueda")
async def spotify_autocomplete(interaction: discord.Interaction, current: str):
    if not current or len(current) < 2:
        return [discord.app_commands.Choice(name="🟢 Escribí el nombre del tema o playlist...", value=current)]
    try:
        # Intentamos buscar usando el formato compatible con el plugin de Spotify
        tracks = await wavelink.Playable.search(f"spsearch:{current}")
        if not tracks: # Respaldo si no tenés LavaSrc activo para búsquedas directas
            tracks = await wavelink.Playable.search(current, source=wavelink.TrackSource.Spotify)
            
        if tracks:
            return [discord.app_commands.Choice(name=f"🟢 {t.title[:80]}", value=t.uri) for t in tracks[:5]]
    except Exception:
        pass
    return [discord.app_commands.Choice(name=f"🔍 Buscar '{current[:50]}' en Spotify", value=current)]


# 3️⃣ --- SOUNDCLOUD PLAY ---
@bot.tree.command(name="play_soundcloud", description="Reproduce música de SoundCloud 🟠")
async def play_soundcloud(interaction: discord.Interaction, busqueda: str):
    await interaction.response.defer()
    await reproducir_tema(interaction, busqueda, wavelink.TrackSource.SoundCloud)

@play_soundcloud.autocomplete("busqueda")
async def soundcloud_autocomplete(interaction: discord.Interaction, current: str):
    if not current or len(current) < 2:
        return [discord.app_commands.Choice(name="🟠 Escribí el tema de SoundCloud...", value=current)]
    try:
        # Usamos el prefijo explícito de SoundCloud
        tracks = await wavelink.Playable.search(f"scsearch:{current}")
        if tracks:
            return [discord.app_commands.Choice(name=f"🟠 {t.title[:80]}", value=t.uri) for t in tracks[:5]]
    except Exception:
        pass
    return [discord.app_commands.Choice(name=f"🔍 Buscar '{current[:50]}' en SoundCloud", value=current)]
    # ==============================================================================
# 🛸 COMANDO DE AYUDA CON BOTÓN DE INVITACIÓN DIRECTA 🚀
# ==============================================================================

class HelpButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        # Añade un botón que abre el enlace directamente sin escribir código extra
        self.add_item(discord.ui.Button(
            label="👾 Servidor de Soporte", 
            url="https://discord.gg/k2uwRFzHD", 
            style=discord.ButtonStyle.link,
            emoji="💬"
        ))

@bot.tree.command(name="help", description="Muestra la central de ayuda y soporte de ComboBOT 🛸")
async def help_slash(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🛸 ¡Central de Ayuda — ComboBOT!", 
        description=(
            "¡Sincronización total y música premium para tu comunidad! 🚀✨\n\n"
            "Manejá todo de forma instantánea e intuitiva usando comandos de barra `/`. "
            "¡Escribí `/` en el chat para ver todas las opciones disponibles! 🤖"
        ), 
        color=discord.Color.from_rgb(0, 240, 255)
    )
    
    embed.add_field(
        name="🎵 Música Separada por Plataformas", 
        value=(
            "• `/play_yt [canción]` - Busca y reproduce en YouTube 🔴\n"
            "• `/play_spotify [canción]` - Busca y reproduce en Spotify 🟢\n"
            "• `/play_soundcloud [canción]` - Busca y reproduce en SoundCloud 🟠\n"
            "• `/stop` - Detiene la música y saca al bot del canal ⏹️"
        ), 
        inline=False
    )
    
    embed.add_field(
        name="🎮 Entretenimiento e Interacción", 
        value=(
            "• `/juego [1-100] [@rival]` - Desafía a un amigo a un juego interactivo 🥊\n"
            "• `/mine` - Minería espacial para conseguir StarChips 🌌\n"
            "• `/cyber_roulette` - Probá tu suerte en el azar cuántico 🎰"
        ), 
        inline=False
    )
    
    embed.set_footer(text="ComboBOT 2026 | Desarrollado con ❤️")
    
    # Enviamos el embed junto con el botón de Discord
    await interaction.response.send_message(embed=embed, view=HelpButtons())
    # ==========================================

    if not tracks:
        return await interaction.followup.send("❌ No encontré ninguna canción con ese nombre o enlace. 😢")

    track = tracks[0]
    await player.queue.put(track)
    
    if not player.playing:
        await player.play(player.queue.get())
        await interaction.followup.send(f"🎶 Empezando a sonar: **{track.title}** 🚀")
    else:
        await interaction.followup.send(f"➕ Añadida a la lista: **{track.title}** 📝")

@bot.tree.command(name="skip", description="Se salta la canción actual ⏭️")
async def skip(interaction: discord.Interaction):
    player: wavelink.Player = interaction.guild.voice_client
    if not player or not player.playing:
        return await interaction.response.send_message("❌ No hay nada sonando para saltear. 💨", ephemeral=True)
    
    await player.skip()
    await interaction.response.send_message("⏭️ Canción salteada con éxito. ¡Siguiente tema! 🎧")

# --- CENTRAL DE AYUDA (ACTUALIZADA CON MÚSICA) ---
@bot.tree.command(name="help_cyber", description="Muestra la central de comandos del bot 🛸")
async def help_cyber_slash(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🛸 Central de Comandos — ComboBOT (Ir a la Web Oficial)", 
        url="https://alejo2026uwu.github.io",
        description=(
            "¡Todos los comandos actualizados al sistema `/` nativo! 🚀✨\n\n"
            "👉 **[Visitar Web para Invitar](https://alejo2026uwu.github.io)**"
        ), 
        color=discord.Color.from_rgb(0, 240, 255)
    )
    
    embed.add_field(name="🎮 Juegos Multijugador", value="`/juego [1-100] [@rival]`, `/mine`, `/cyber_roulette` 🥊", inline=False)
    embed.add_field(name="🎵 Sistema de Música", value="`/play [canción]`, `/skip`, `/stop` 🎶", inline=False)
    embed.set_footer(text="ComboBOT 2026 | Desarrollado con ❤️")
    
    await interaction.response.send_message(embed=embed)

# --- COMANDOS EXTRAS DE ECONOMÍA ---
@bot.tree.command(name="mine", description="Minería de datos espacial 💎")
async def mine(interaction: discord.Interaction):
    recompensa = random.randint(120, 550)
    await interaction.response.send_message(f"🌌 **{interaction.user.name}** extrajo **{recompensa} StarChips** de servidores encriptados. 💎")

@bot.tree.command(name="cyber_roulette", description="Mesa de azar cuántico 🎰")
async def cyber_roulette(interaction: discord.Interaction, apuesta: int = 200):
    if random.choice([True, False]):
        await interaction.response.send_message(f"🎰 **{interaction.user.name}** ganó **{apuesta * 2} StarChips** en la ruleta! 🎉💥")
    else:
        await interaction.response.send_message(f"📉 Mala suerte, perdiste tus **{apuesta} StarChips**. 😢💸")

# ==============================================================================
# 6. MULTIHILO INTERNO SEGURO EN SEGUNDO PLANO PARA RENDER
# ==============================================================================
try:
    def run_flask():
        app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)), use_reloader=False)
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
except Exception as error:
    print(f"❌ Falló el enlace de Flask: {error}", flush=True)

# ==============================================================================
# 7. EXECUTE DEL PROCESO PRINCIPAL
# ==============================================================================
token_servicio = os.environ.get("TOKEN")
if token_servicio:
    bot.run(token_servicio)
else:
    print("❌ ERROR DE SISTEMA: Variable 'TOKEN' ausente en Render.", flush=True)
