import discord
from discord import app_commands
from discord.ext import commands
import random
import os
import wavelink
import threading

# --- INTENTS CONFIGURADOS ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  
bot = commands.Bot(command_prefix="/", intents=intents)

# --- CONFIGURACIÓN DE LOS 100 TEMAS ÚNICOS ---
JUEGOS_DETALLES = {
    1: {"name": "Duelo de Espadas", "hit": "te encajó una estocada letal", "crit": "¡te decapitó con un crítico medieval!"},
    2: {"name": "Martillazo de Feria", "hit": "le dio un masazo al medidor", "crit": "¡hizo sonar la campana con fuerza extrema!"},
    3: {"name": "Piedra Cósmica", "hit": "te tiró un cometa de energía", "crit": "¡te pulverizó con un Big Bang cósmico!"},
    4: {"name": "Carrera de Autos", "hit": "te pasó por el costado tirando nitro", "crit": "¡te chocó el coche y te dejó en la banquina!"},
    5: {"name": "Ruleta Rusa", "hit": "te apuntó y el tambor giró", "crit": "¡💥 PUM! El balazo fue directo a la frente"},
    6: {"name": "Pelea de Boxeo", "hit": "te metió un gancho al hígado", "crit": "¡te metió un KO brutal que te mandó a dormir!"},
    7: {"name": "Duelo de Magos", "hit": "te tiró un hechizo desarmador", "crit": "¡¡AVADA KEDAVRA!! Te extinguió por completo"},
    8: {"name": "Batalla de Rap", "hit": "te tiró una rima re picante", "crit": "¡te humilló frente a toda la plaza con un rimaso!"},
    9: {"name": "Combate de Sumo", "hit": "te empujó hacia el borde", "crit": "¡te aplastó con sus 200 kilos fuera del ring!"},
    10: {"name": "Guerra de Nieve", "hit": "te pegó un gélido pelotazo", "crit": "¡te encajó un gualicazo de hielo con una piedra adentro!"},
    11: {"name": "Tiro con Arco", "hit": "te clavó una flecha en la pierna", "crit": "¡Te metió un Headshot certero en el ojo!"},
    12: {"name": "Pelea de Almohadas", "hit": "te dio un cazote de plumas", "crit": "¡te reventó la almohada en la cara y te dejó ciego!"},
    13: {"name": "Sable de Luz", "hit": "te cortó la defense Jedi", "crit": "¡te rebanó el brazo como si fueras Anakin!"},
    14: {"name": "Pulgar de Hierro", "hit": "te ganó la posición del dedo", "crit": "¡te dobló el pulgar hasta hacértelo crujir!"},
    15: {"name": "Lanzamiento de Hacha", "hit": "te rozó el hombro con el filo", "crit": "¡te clavó el hacha de guerra en medio del pecho!"},
    16: {"name": "Batalla de Tanques", "hit": "te disparó un misil ligero", "crit": "¡te perforó el blindaje con un tiro de cañón pesado!"},
    17: {"name": "Paintball", "hit": "te manchó todo el chaleco", "crit": "¡te dio un ráfagazo de pintura directo en la nuca!"},
    18: {"name": "Kung Fu", "hit": "te metió una patada giratoria", "crit": "¡te aplicó el golpe de los cinco puntos de presión!"},
    19: {"name": "Piratas en Alta Mar", "hit": "te pegó un tiro de trabuco", "crit": "¡te tiró a los tiburones caminando por la tabla!"},
    20: {"name": "Guerra de Miradas", "hit": "te sostuvo la vista firme", "crit": "¡te hizo parpadear usando poderes mentales!"},
    21: {"name": "Penales de Fútbol", "hit": "te la clavó junto al palo", "crit": "¡te pinchó la pelota a lo Panenka dejando pagando al arquero!"},
    22: {"name": "Volcada de Básquet", "hit": "te metió un triple en la cara", "crit": "¡te saltó por encima y te rompió el tablero!"},
    23: {"name": "Carrera de 100m", "hit": "te sacó una zancada de ventaja", "crit": "¡activó el modo Usain Bolt y te sacó tres cuadras!"},
    24: {"name": "Tenis de Mesa", "hit": "te metió un efecto endemoniado", "crit": "¡te clavó un smash inalcanzable en la esquina!"},
    25: {"name": "Lanzamiento de Disco", "hit": "tiró unos metros más lejos", "crit": "¡batió el récord olímpico destruyendo tu marca!"},
    26: {"name": "Salto en Largo", "hit": "cayó un centímetro adelante", "crit": "¡voló por los aires como un superhéroe!"},
    27: {"name": "Hipódromo", "hit": "su caballo picó en punta", "crit": "¡su yegua ganó por puesta de cabeza en el final!"},
    28: {"name": "Torneo de Golf", "hit": "la dejó adentro del Green", "crit": "¡metió un Hole-in-One legendario desde 300 yardas!"},
    29: {"name": "Billar de Bar", "hit": "te embocó la bola lisa", "crit": "¡limpió la mesa con una carambola a tres bandas!"},
    30: {"name": "Bowling", "hit": "te metió un semi-pleno", "crit": "¡clavó una chuzada perfecta tirando todos los pinos!"},
    31: {"name": "Carrera de Bicis", "hit": "te ganó el sprint en la subida", "crit": "¡te tiró la bicicleta encima cruzando la meta!"},
    32: {"name": "Pesca Pesada", "hit": "sacó un bagre decente", "crit": "¡sacó un tiburón blanco mutante con caña de mojarra!"},
    33: {"name": "Dardos", "hit": "clavó en la zona del 20", "crit": "¡metió el dardo justo en el centro del Bullseye!"},
    34: {"name": "Ajedrez Relámpago", "hit": "te comió un alfil descuidado", "crit": "¡te clavó el Jaque Mate del Pastor en tres movimientos!"},
    35: {"name": "Surf Extremo", "hit": "corrió la ola con estilo", "crit": "¡se metió adentro del tubo y salió intacto!"},
    36: {"name": "Skate Trucos", "hit": "tiró un Kickflip limpio", "crit": "¡clavó un 900 bajando la rampa a lo Tony Hawk!"},
    37: {"name": "Boxeo de Robots", "hit": "te abolló el procesador", "crit": "¡te arrancó la cabeza mecánica dejando los cables expuestos!"},
    38: {"name": "Carrera de Karts", "hit": "te tiró un caparazón verde", "crit": "¡te reventó con un caparazón azul a un metro de la meta!"},
    39: {"name": "Vóley de Playa", "hit": "te la colocó atrás de la red", "crit": "¡te pegó un pelotazo en la cara que te enterró en la arena!"},
    40: {"name": "Herraduras", "hit": "la dejó pegada al caño", "crit": "¡embocó la herradura justo adentro del poste!"},
    41: {"name": "Geometry Dash 1v1", "hit": "pasó el triple pincho", "crit": "¡completó Bloodbath en un intento al 100%!"},
    42: {"name": "Solo Mid LoL", "hit": "te metió un hostigamiento bruto", "crit": "¡te deleteó abajo de torre con el combo de Riven!"},
    43: {"name": "Snipers en Rust", "hit": "te pegó en el chaleco", "crit": "¡te voló la gorra a 400 metros con el L96!"},
    44: {"name": "Speedrun Minecraft", "hit": "consiguió las perlas rápido", "crit": "¡mató al dragón con camas en tiempo récord mundial!"},
    45: {"name": "Super Smash", "hit": "te sacó un 40% de daño", "crit": "¡te metió un Home-Run Contest sacándote del mapa!"},
    46: {"name": "Cartas Pokémon", "hit": "te atacó con una energía", "crit": "¡usó el ataque de Charizard y te quemó el mazo!"},
    47: {"name": "Clash Royale", "hit": "te tiró un montapuercos", "crit": "¡te tiró un cohete a la torre del rey en el último segundo!"},
    48: {"name": "Trivia GTA 6", "hit": "respondió un dato básico", "crit": "¡filtró el mapa entero del juego con sus respuestas!"},
    49: {"name": "Guitar Hero", "hit": "metió una racha de 50 notas", "crit": "¡tocó Through the Fire and Flames al 100% de precisión!"},
    50: {"name": "Baile Fortnite", "hit": "tiró unos pasos de baile", "crit": "¡te tiró el Take the L en la cara después de lofearte!"},
    51: {"name": "Tetris Blitz", "hit": "limpió dos líneas juntas", "crit": "¡te mandó 4 líneas limpias metiendo un Tetris perfecto!"},
    52: {"name": "Pacman Racha", "hit": "se comió una bolita de poder", "crit": "¡se comió a los 4 fantasmas acorralándote en el pasillo!"},
    53: {"name": "Adivinar Personaje", "hit": "te descartó las pistas buenas", "crit": "¡te sacó el personaje oculto en la primera pregunta!"},
    54: {"name": "Zombies Coop", "hit": "te dejó sin balas de la pistola", "crit": "¡te tiró una granada de mono salvándote la partida!"},
    55: {"name": "DayZ Survival", "hit": "te robó una lata de atún", "crit": "¡te quebró las piernas con un tiro desde la montaña!"},
    56: {"name": "Casino Ruleta", "hit": "le pegó al color rojo", "crit": "¡le embocó al número exacto multiplicando el botín!"},
    57: {"name": "Póker Express", "hit": "te robó las ciegas chicaneando", "crit": "¡te metió un All-In con una Escalera Real oculta!"},
    58: {"name": "Blackjack 21", "hit": "pidió carta y sumó 19", "crit": "¡clavó un 21 clavado en la jeta del repartidor!"},
    59: {"name": "Moneda Cósmica", "hit": "la gravedad tiró para su lado", "crit": "¡la moneda distorsionó el espacio y ganó el universo!"},
    60: {"name": "Adivinar Número", "hit": "le erró por poquito", "crit": "¡leyó tu mente y puso el número exacto que pensabas!"},
    61: {"name": "Carrera de Caracoles", "hit": "su caracol avanzó un milímetro", "crit": "¡su caracol tomó speed y cruzó derrapando!"},
    62: {"name": "Chancla Voladora", "hit": "te pegó en el hombro de rebote", "crit": "¡te pegó un chancletazo teledirigido doblando la esquina!"},
    63: {"name": "Chistes Malos", "hit": "te contó uno de Jaimito", "crit": "¡te contó un chiste tan rancio que te estallaste de la risa!"},
    64: {"name": "Comer Hamburguesas", "hit": "se bajó un cuarto de libra", "crit": "¡se tragó un combo gigante de 4 pisos en un bocado!"},
    65: {"name": "Sin Respirar", "hit": "aguantó un par de segundos más", "crit": "¡se quedó azul y superó los 5 minutos bajo el agua!"},
    66: {"name": "Sillones de Oficina", "hit": "giró veloz por el pasillo", "crit": "¡chocó el escritorio del jefe y te dejó atrás de un empujón!"},
    67: {"name": "Escape de la Policía", "hit": "saltó una reja alta", "crit": "¡se subió a un patrullero vacío y escapó derrapando!"},
    68: {"name": "Toro Mecánico", "hit": "se sostuvo de la cuerda", "crit": "¡aguantó la velocidad nivel 100 sin soltar el sombrero!"},
    69: {"name": "Atrapar Mosca", "hit": "le rozó las alas a la mosca", "crit": "¡atrapó al bicho en el aire al puro estilo Miyagi!"},
    70: {"name": "Aviones de Papel", "hit": "su avión planeó un ratito", "crit": "¡su avión agarró una corriente de aire y cruzó la habitación!"},
    71: {"name": "Guerra de Chinchón", "hit": "te cortó con pocos puntos", "crit": "¡metió un chinchón de una con el as de espadas!"},
    72: {"name": "Dormir Rápido", "hit": "empezó a bostezar fuerte", "crit": "¡entró en coma profundo a los dos segundos de acostarse!"},
    73: {"name": "Batalla de Cojines", "hit": "te desacomodó el pelo", "crit": "¡te pegó un almohadazo con el cierre dejándote mareado!"},
    74: {"name": "El Piso es Lava", "hit": "se trepó a la mesa ratona", "crit": "¡saltó arriba del mueble caro esquivando el magma!"},
    75: {"name": "Última Pizza", "hit": "te manoteó el borde", "crit": "¡te sacó la porción de muzzarella de la boca!"},
    76: {"name": "Trébol de 4 Hojas", "hit": "encontró uno de tres", "crit": "¡pisó la planta de la suerte y se ganó la lotería!"},
    77: {"name": "Susto a la Oscuridad", "hit": "te hizo un ruido raro", "crit": "¡te saltó atrás de la puerta y te hizo pegar un grito letal!"},
    78: {"name": "Tortazo a la Cara", "hit": "te manchó la oreja de crema", "crit": "¡te estampó una torta de crema directo en la nariz!"},
    79: {"name": "Gallos de Granja", "hit": "su gallo tiró un picotazo", "crit": "¡su gallo metió una patada voladora ganando el corral!"},
    80: {"name": "Tortugas Turbo", "hit": "su tortuga avanzó un tramo", "crit": "¡le puso un motor de cohete a la tortuga y voló!"},
    81: {"name": "Hackeo NASA", "hit": "descifró una IP pública", "crit": "¡entró al servidor central y apagó los satélites!"},
    82: {"name": "Cohetes a Marte", "hit": "su propulsor encendió bien", "crit": "¡aterrizó en el planeta rojo antes que Elon Musk!"},
    83: {"name": "Mina de Oro", "hit": "picó un pedazo de carbón", "crit": "¡encontró una veta gigante de diamantes puros!"},
    84: {"name": "Meteorito", "hit": "esquivó un fragmento chico", "crit": "¡armó un búnker anti-atómico perfecto bajo tierra!"},
    85: {"name": "Dinosaurios T-Rex", "hit": "te pegó un colazo en los pies", "crit": "¡te pegó un mordisco que te mandó a la prehistoria!"},
    86: {"name": "Virus Mutante", "hit": "contagió a un par de células", "crit": "¡creó la cepa zombie definitiva infectando el planeta!"},
    87: {"name": "Aliens vs Depredador", "hit": "te disparó con el cañón de hombro", "crit": "¡te atravesó con las garras ocultas desde los árboles!"},
    88: {"name": "Viaje en el Tiempo", "hit": "viajó un par de días atrás", "crit": "¡alteró la línea temporal y borró a tus ancestros!"},
    89: {"name": "Agua en el Desierto", "hit": "encontró un pozo seco", "crit": "¡descubrió un oasis paradisíaco con agua helada!"},
    90: {"name": "Planta Mutante", "hit": "su semilla brotó un poquito", "crit": "¡su planta creció hasta las nubes y se comió tu casa!"},
    91: {"name": "Invasión Extraterrestre", "hit": "te apuntó con un rayo láser", "crit": "¡te abdujo adentro del plato volador para estudiarte!"},
    92: {"name": "Escape de Prisión", "hit": "limó los barrotes de la celda", "crit": "¡escapó por el túnel cavado atrás del póster!"},
    93: {"name": "Física Cuántica", "hit": "resolvió una ecuación simple", "crit": "¡abrió un agujero de gusano en el living de su casa!"},
    94: {"name": "Apocalipsis Nuclear", "hit": "consiguió una máscara de gas", "crit": "¡compró el último traje de radiación del mercado!"},
    95: {"name": "Rey de la Colina", "hit": "te empujó un paso abajo", "crit": "¡te tiró de una patada y se quedó con la corona!"},
    96: {"name": "Duelo de Samuráis", "hit": "te rozó con la Katana", "crit": "¡te hizo el corte definitivo antes de que envaines!"},
    97: {"name": "Guerra de Memes", "hit": "te mandó un sticker gracioso", "crit": "¡te mandó un meme tan potente que mató de risa al grupo!"},
    98: {"name": "Lanzar el Tejo", "hit": "dejó el disco cerca del centro", "crit": "¡metió el tejo directo en la ranura sumando el triple!"},
    99: {"name": "Búsqueda del Tesoro", "hit": "encontró una pista vieja", "crit": "¡abrió el cofre lleno de lingotes de oro pirata!"},
    100: {"name": "Última Sobreviviente", "hit": "se curó con un vendaje", "crit": "¡te metió un headshot ganando la partida definitiva!"}
}

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
        if inter.user.id != self.turno.id: return
        dmg = random.randint(10, 20)
        self.hp[self.rival.id] -= dmg
        txt = f"⚔️ {self.turno.mention} {self.hit_txt} a {self.rival.mention} haciendo `{dmg} DMG`."
        if self.hp[self.rival.id] > 0: self.turno, self.rival = self.rival, self.turno
        await self.actualizar(inter, txt)

    @discord.ui.button(label="⚡ Golpe Arriesgado", style=discord.ButtonStyle.danger)
    async def crit_btn(self, inter, btn):
        if inter.user.id != self.turno.id: return
        if random.randint(1, 2) == 1:
            dmg = random.randint(25, 50)
            self.hp[self.rival.id] -= dmg
            txt = f"🔥💥 {self.turno.mention} {self.crit_txt} contra {self.rival.mention} quitando `{dmg} DMG`!"
        else:
            txt = f"💨 {self.turno.mention} intentó una jugada arriesgada en **{self.nombre}** pero la manqueó feo."
        if self.hp[self.rival.id] > 0: self.turno, self.rival = self.rival, self.turno
        await self.actualizar(inter, txt)

@bot.event
async def on_ready():
    await bot.tree.sync()
    # Conexión al nodo de música Lavalink
    node = wavelink.Node(uri='https://mi-lavalink.onrender.com', password='youshallnotpass')
    await wavelink.Pool.connect(nodes=[node], client=bot)
    print(f"🤖 ¡ComboBOT ultra completo online con Música!")

# --- 🚪 MÓDULO BIENVENIDAS Y DESPEDIDAS ---
@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name="bienvenidas")
    if channel:
        embed = discord.Embed(title=f"👋 ¡Bienvenido/a {member.name}!", description="Pasala de diez, escuchá música y jugá a los minijuegos. 🎉", color=discord.Color.purple())
        embed.set_thumbnail(url=member.display_avatar.url)
        await channel.send(embed=embed)

@bot.event
async def on_member_remove(member):
    channel = discord.utils.get(member.guild.text_channels, name="despedidas")
    if channel:
        await channel.send(f"😢 **{member.name}** abandonó el servidor... F.")

# --- 🎶 MÓDULO MÚSICA GRATIS (BEATBOT) ---
async def play_autocomplete(interaction: discord.Interaction, current: str):
    if not current or len(current) < 3: return []
    tracks = await wavelink.Playable.search(current)
    return [app_commands.Choice(name=f"🎵 {t.title}"[:100], value=t.uri) for t in tracks[:5]]

@bot.tree.command(name="play", description="Reproduce música gratis en el canal de voz")
@app_commands.autocomplete(search=play_autocomplete)
async def play(interaction: discord.Interaction, search: str):
    await interaction.response.defer()
    voice_channel = interaction.user.voice.channel if interaction.user.voice else next((ch for ch in interaction.guild.channels if isinstance(ch, discord.VoiceChannel)), None)
    if not voice_channel: return await interaction.followup.send("❌ Metete a un canal de voz primero.")
    
    player: wavelink.Player = interaction.guild.voice_client or await voice_channel.connect(cls=wavelink.Player) # type: ignore
    tracks = await wavelink.Playable.search(search)
    if not tracks: return await interaction.followup.send("❌ No encontré canciones.")
    
    await player.play(tracks[0])
    await interaction.followup.send(f"🎶 Sonando ahora: `{tracks[0].title}`")

@bot.tree.command(name="stop", description="Detiene la música por completo")
async def stop(interaction: discord.Interaction):
    if interaction.guild.voice_client:
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("⏹️ Música apagada.")

# --- 🕹️ COMANDO DE LOS 100 JUEGOS ---
@bot.tree.command(name="juego", description="Lanzá uno de los 100 juegos totalmente personalizados")
async def cmd_juego(inter: discord.Interaction, numero: int, oponente: discord.Member):
    if numero not in JUEGOS_DETALLES:
        return await inter.response.send_message("❌ Poné un número del **1 al 100**.", ephemeral=True)
    
    config = JUEGOS_DETALLES[numero]
    view = JuegoMasivoView(inter.user, oponente, numero, config)
    embed = discord.Embed(title="⚔️ PELEA TOTAL INICIADA ⚔️", description=f"Se va a pudrir todo jugando a: **#{numero} - {config['name']}**\n\n¡Tienen 100 HP cada uno!", color=discord.Color.gold())
    await inter.response.send_message(embed=embed, view=view)

# --- 🤡 MÓDULO DE CREACIÓN DE MEMES PROPIOS ---
@bot.tree.command(name="crearmeme", description="¡Crea tus propios memes personalizados! 🖼️")
@app_commands.choices(plantilla=[
    app_commands.Choice(name="Drake (Sí/No)", value="drake"),
    app_commands.Choice(name="Batman Cachetada", value="buzz"),
    app_commands.Choice(name="Distracted Boyfriend", value="away"),
    app_commands.Choice(name="Change My Mind", value="cmm"),
    app_commands.Choice(name="Two Buttons", value="twobuttons")
])
async def crearmeme(interaction: discord.Interaction, plantilla: app_commands.Choice[str], texto_arriba: str, texto_abajo: str):
    await interaction.response.defer()
    t1 = texto_arriba.replace(" ", "_").replace("?", "~q").replace("%", "~p")
    t2 = texto_abajo.replace(" ", "_").replace("?", "~q").replace("%", "~p")
    url_meme = f"https://api.memegen.link/images/{plantilla.value}/{t1}/{t2}.png"
    
    embed = discord.Embed(title="🤣 ¡Tu meme personalizado está listo!", color=discord.Color.brand_green())
    embed.set_image(url=url_meme)
    await interaction.followup.send(embed=embed)

# EMULADOR DE PUERTO WEB CON OAUTH2 REAL DE DISCORD
if __name__ == "__main__":
    token = os.environ.get("TOKEN")
    
    try:
        from flask import Flask, render_template, request, redirect, session
        import requests
        
        app = Flask('', template_folder='templates')
        app.secret_key = "un_secreto_super_seguro_para_las_cookies" # Cambia esto por lo que quieras
        
        # CONFIGURACIÓN DE TU CLIENTE DISCORD
        CLIENT_ID = "1525280479476060210"
        CLIENT_SECRET = "" # <-- Buscalo en Discord Developer Portal (OAuth2 -> General)
        REDIRECT_URI = "https://tu-app-en-render.onrender.com/callback" # <-- Cambialo por tu URL real de Render + /callback
        
        @app.route('/')
        def home(): 
            return render_template('index.html')

        @app.route('/login')
        def login():
            # Redirige directo a tu url de autorización de Discord
            return redirect(f"https://discord.com/oauth2/authorize?client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}&scope=identify+guilds")

        @app.route('/callback')
        def callback():
            code = request.args.get('code')
            if not code:
                return "Error: No se recibió el código de Discord.", 400
                
            # Intercambiar el código por un Token de Acceso del usuario
            data = {
                'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET,
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': REDIRECT_URI
            }
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            r = requests.post('%s/oauth2/token' % "https://discord.com/api", data=data, headers=headers)
            r.raise_for_status()
            tokens = r.json()
            
            # Guardamos el token del usuario en su sesión del navegador
            session['access_token'] = tokens['access_token']
            return redirect('/server_panel.html')

        @app.route('/server_panel.html')
        def panel():
            access_token = session.get('access_token')
            if not access_token:
                return redirect('/login') # Si no está logueado, lo manda a loguear
                
            # Pedir a la API de Discord los servidores REALES del usuario
            headers = {'Authorization': f'Bearer {access_token}'}
            guilds_res = requests.get('https://discord.com/api/users/@me/guilds', headers=headers)
            
            if guilds_res.status_code != 200:
                return "Error al obtener tus servidores de Discord.", 500
                
            all_guilds = guilds_res.json()
            
            # Filtrar: solo dejamos los servidores donde es DUEÑO (owner=True) o tiene permisos de ADMIN (permissions & 0x8)
            filtered_guilds = []
            for g in all_guilds:
                is_owner = g.get('owner', False)
                perms = int(g.get('permissions', 0))
                is_admin = (perms & 0x8) == 0x8
                
                if is_owner or is_admin:
                    filtered_guilds.append({
                        'id': g['id'],
                        'name': g['name'],
                        'icon': f"https://cdn.discordapp.com/icons/{g['id']}/{g['icon']}.png" if g['icon'] else "https://assets-global.website-files.com/6257adef93867e50d84d30e2/636e0a6a49cf127bf92de1e2_icon_clyde_blurple_RGB.png",
                        'role': 'Dueño 👑' if is_owner else 'Admin 🛠️'
                    })
            
            # Le pasamos los servidores reales al archivo HTML para que los dibuje
            return render_template('server_panel.html', guilds=filtered_guilds)

    def run(): 
    import os
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
        threading.Thread(target=run).start()
    except ImportError:
        pass
    bot.run(token)
