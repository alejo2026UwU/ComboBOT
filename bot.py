import os
import random
import threading
import asyncio
from flask import Flask, render_template, session, redirect, request
import requests
import discord
from discord.ext import commands
import urllib.parse
import urllib.request
import json
import re
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

# CONFIGURACIÓN DE LOS JUEGOS (1-100) 🥊
JUEGOS_DETALLES = {
    1: {"name": "Duelo de Espadas", "hit": "te encajó una estocada letal", "crit": "¡te decapitó con un crítico medieval!"},
    2: {"name": "Guerra de Nieve", "hit": "te encajó un bochazo helado en la frente", "crit": "¡te metió un hielo por la espalda! 🥶"},
    3: {"name": "Combate Láser", "hit": "te quemó el chaleco con un disparo láser", "crit": "¡te desintegró con un disparo en la cabeza!"},
    4: {"name": "Pelea de Almohadas", "hit": "te dio un almohadazo en la cara llena de plumas", "crit": "¡te noqueó con un golpe de almohada ultrasónico!"},
    5: {"name": "Ring de Boxeo", "hit": "te metió un jab directo al mentón", "crit": "¡te mandó a la lona con un gancho al hígado!"},
    6: {"name": "Fútbol Callejero", "hit": "te barrió de atrás limpiamente", "crit": "¡te metió un pelotazo en la cara y te dejó bizco!"},
    7: {"name": "Duelo de Magos", "hit": "te lanzó un hechizo de chispas", "crit": "¡te lanzó un Avada Kedavra de cotillón!"},
    8: {"name": "Batalla de Bandas", "hit": "te reventó los oídos con un solo de bajo", "crit": "¡te partió la guitarra eléctrica en la cabeza!"},
    9: {"name": "Apocalipsis Zombie", "hit": "te arañó un brazo con fuerza", "crit": "¡te pegó un mordisco voraz en el cuello!"},
    10: {"name": "Guerra de Globos de Agua", "hit": "te empapó la remera", "crit": "¡te explotó un globo gigante en toda la cara!"},
    11: {"name": "Piratas del Caribe", "hit": "te rozó con su sable oxidado", "crit": "¡te mandó a dormir con los peces de un cañonazo!"},
    12: {"name": "Carrera de Karts", "hit": "te tiró un caparazón verde", "crit": "¡te hizo volar por los aires con una bomba azul!"},
    13: {"name": "Olimpiadas de Paintball", "hit": "te manchó la espalda de pintura roja", "crit": "¡te llenó la cara de pintura amarilla a quemarropa!"},
    14: {"name": "Lucha Libre", "hit": "te hizo un candado a la cabeza", "crit": "¡se tiró desde la tercera cuerda y te aplastó!"},
    15: {"name": "Invasión Alienígena", "hit": "te disparó con una pistola de plasma", "crit": "¡te abdujo y te desintegró en su nave espacial!"},
    16: {"name": "Duelo del Lejano Oeste", "hit": "te rozó la oreja de un disparo", "crit": "¡te metió un balazo en el pecho al mediodía!"},
    17: {"name": "Samuráis vs Ninjas", "hit": "te cortó con su katana veloz", "crit": "¡te clavó tres shurikens envenenados en el pecho!"},
    18: {"name": "Batalla de Rap", "hit": "te tiró una rima floja sobre tu vieja", "crit": "¡te humilló con un freestyle épico frente a todos!"},
    19: {"name": "Guerra de Comida", "hit": "te tiró un puré de papas tibio", "crit": "¡te estampó una torta de crema gigante en los ojos!"},
    20: {"name": "Cyberpunk 2077", "hit": "te hackeó el implante del brazo", "crit": "¡te fundió el cerebro con un virus informático!"},
    21: {"name": "Tirachinas de Barrio", "hit": "te pegó con una piedrita en el hombro", "crit": "¡te metió un gomerazo directo en la frente!"},
    22: {"name": "Danza de Espadas", "hit": "te hizo un tajo leve en la pierna", "crit": "¡te atravesó el corazón con un florete!"},
    23: {"name": "Ataque del Dragón", "hit": "te quemó las pestañas con un soplido", "crit": "¡te rostizó por completo con una llamarada de fuego!"},
    24: {"name": "Estación Espacial", "hit": "te empujó al vacío exterior", "crit": "¡te cortó la manguera de oxígeno y moriste flotando!"},
    25: {"name": "Esgrima Láser", "hit": "te quemó el hombro con plasma", "crit": "¡te cortó a la mitad como a un joven Padawan!"},
    26: {"name": "Bolo Humano", "hit": "te empujó con una bola inflable", "crit": "¡te pasó por arriba como un camión gigante!"},
    27: {"name": "Cazadores de Fantasmas", "hit": "te tiró un rayo de protones", "crit": "¡te atrapó en una trampa espectral para siempre!"},
    28: {"name": "Lucha de Sumos", "hit": "te empujó fuera del tatami", "crit": "¡te aplastó con sus 200 kilos de pura pasión!"},
    29: {"name": "Tenis de Mesa Caliente", "hit": "te metió un pelotazo en el estómago", "crit": "¡te reventó la cara de un smash endemoniado!"},
    30: {"name": "Combate de Tanques", "hit": "te rozó con una barra de cañón", "crit": "¡hizo volar tu tanque por los aires de un impacto directo!"},
    31: {"name": "Dinosaurios Hambrientos", "hit": "te mordió un tobillo con saña", "crit": "¡un T-Rex te tragó de un solo bocado!"},
    32: {"name": "Karate Kid", "hit": "te pegó una patada baja en la espinilla", "crit": "¡te noqueó con la mítica patada de la grulla!"},
    33: {"name": "Guerra de Nerfs", "hit": "te pegó un dardo de goma en la frente", "crit": "¡te vació todo el cargador de ráfaga en la cara!"},
    34: {"name": "Carrera de Obstáculos", "hit": "te empujó contra una valla", "crit": "¡te tiró al pozo de barro con cocodrilos inflables!"},
    35: {"name": "Duelo Cósmico", "hit": "te lanzó un meteorito diminuto", "crit": "¡te succionó dentro de un agujero negro supermasivo!"},
    36: {"name": "Derrumbe de Jenga", "hit": "te tiró una madera pesada en el pie", "crit": "¡te tiró toda la torre gigante de madera encima!"},
    37: {"name": "Fútbol de Mesa", "hit": "te metió un gol de carambola", "crit": "¡te hizo molinete y te rompió la muñeca del pelotazo!"},
    38: {"name": "Ataque Tiburón", "hit": "te raspó con su piel de lija", "crit": "¡te arrancó una pierna de una sola dentellada!"},
    39: {"name": "Tornado de Viento", "hit": "te levantó unos metros del suelo", "crit": "¡te mandó volando a otra provincia de un soplido!"},
    40: {"name": "Pelea de Robots", "hit": "te dio un golpe de metal oxidado", "crit": "¡te aplastó con una prensa hidráulica de 50 toneladas!"},
    41: {"name": "Ajedrez Violento", "hit": "te comió un peón de mala manera", "crit": "¡te partió el tablero de madera maciza en la cabeza!"},
    42: {"name": "Gladiadores Romanos", "hit": "te lastimó el brazo con su tridente", "crit": "¡te lanzó a los leones hambrientos del Coliseo!"},
    43: {"name": "Parque de Diversiones", "hit": "te chocó con un autito chocador", "crit": "¡te hizo salir volando de la montaña rusa sin cinturón!"},
    44: {"name": "Arquería Elfica", "hit": "te rozó la mejilla con una flecha", "crit": "¡te clavó una flecha directamente entre ceja y ceja!"},
    45: {"name": "Duelo de Coctelería", "hit": "te tiró un trago fuerte en la camisa", "crit": "¡te emborrachó con un shot flameante ultra potente!"},
    46: {"name": "Guerra de Clanes", "hit": "te tiró una piedra con una catapulta", "crit": "¡te aplastó con un gigante furioso de nivel 10!"},
    47: {"name": "Héroes de Mitología", "hit": "te golpeó con un escudo de bronce", "crit": "¡Zeus te fulminó con un rayo directo desde el Olimpo!"},
    48: {"name": "Granja Loca", "hit": "te picó una gallina rabiosa", "crit": "¡te pasó por encima con un tractor fuera de control!"},
    49: {"name": "Simulador de Vuelo", "hit": "te hizo marear con una maniobra", "crit": "¡se estrelló directo contra tu avión de frente!"},
    50: {"name": "Lucha de Cuerdas", "hit": "te arrastró un metro por el pasto", "crit": "¡te hizo morder el polvo contra el suelo de cemento!"},
    51: {"name": "Minicraft PvP", "hit": "te pegó con una espada de madera", "crit": "¡te tiró un Creeper cargado en los pies!"},
    52: {"name": "Superhéroes", "hit": "te tiró un rayo de hielo leve", "crit": "¡te metió un puñetazo que te mandó al espacio exterior!"},
    53: {"name": "Invasión de Abejas", "hit": "te picó una abeja en la oreja", "crit": "¡te atacó un enjambre furioso y te desfiguró la cara!"},
    54: {"name": "Esquí Extremo", "hit": "te tiró una bola de nieve pesada", "crit": "¡te sepultó bajo una avalancha gigante de nieve!"},
    55: {"name": "Bowling Salvaje", "hit": "te golpeó un pino de madera", "crit": "¡te metió un strike directo en las piernas!"},
    56: {"name": "Pelea de Gatos", "hit": "te metió un rasguño molesto", "crit": "¡te saltó a la cara tirándote del pelo con furia!"},
    57: {"name": "Templo Perdido", "hit": "te rozó un dardo envenenado", "crit": "¡te aplastó una roca esférica gigante de piedra!"},
    58: {"name": "Submarino de Guerra", "hit": "te sacudió con una onda expansiva", "crit": "¡te hundió por completo con un torpedo dirigido!"},
    59: {"name": "Festival de Globos", "hit": "te tiró harina en la remera", "crit": "¡te tiró un baldazo de pintura asfáltica en la cabeza!"},
    60: {"name": "Pesadilla en la Cocina", "hit": "te tiró una sartén caliente", "crit": "¡te tiró aceite hirviendo directo en la cara!"},
    61: {"name": "Duelo de Chistes", "hit": "te contó un chiste bastante malo", "crit": "¡te contó un chiste tan malo que te dio un paro cardíaco!"},
    62: {"name": "Vikingos al Ataque", "hit": "te golpeó con el mango de su hacha", "crit": "¡te partió al medio de un hachazo digno de Odín!"},
    63: {"name": "Guerra de Papel", "hit": "te tiró un bollito de papel mojado", "crit": "¡te cortó el dedo con el borde de una hoja A4 nueva!"},
    64: {"name": "Carrera de Caballos", "hit": "te salpicó barro en la cara", "crit": "¡te pasó por encima con el caballo herrado!"},
    65: {"name": "Volcán Activo", "hit": "te tiró una ceniza ardiente", "crit": "¡te empujó directo al río de lava hirviendo!"},
    66: {"name": "Golf de Choque", "hit": "te rozó con la pelota de golf", "crit": "¡te pegó un palazo de metal directo en los dientes!"},
    67: {"name": "Duelo de Guitarra", "hit": "te desafinó una cuerda", "crit": "¡te reventó el tímpano izquierdo de un acople eléctrico!"},
    68: {"name": "Supermercado Loco", "hit": "te chocó con el changuito de compras", "crit": "¡te aplastó con una pila gigante de latas de conserva!"},
    69: {"name": "Playa de Cangrejos", "hit": "te pellizcó un dedo del pie", "crit": "¡un cangrejo gigante te agarró de la nariz con su pinza!"},
    70: {"name": "Lluvia de Meteoritos", "hit": "te cayó una piedra caliente en el hombro", "crit": "¡te cayó un meteorito del tamaño de una casa encima!"},
    71: {"name": "Duelo de Sombras", "hit": "te asustó con una mueca", "crit": "¡te robó el alma y te dejó como cáscara vacía!"},
    72: {"name": "Caza del Tesoro", "hit": "te empujó en un pozo de arena", "crit": "¡te encerró adentro del cofre del tesoro sin aire!"},
    73: {"name": "Pelea Medieval", "hit": "te golpeó con su mazo de madera", "crit": "¡te aplastó la cabeza con una maza de picos de hierro!"},
    74: {"name": "Karate con Tablas", "hit": "te golpeó con una astilla", "crit": "¡te partió una tabla de pino macizo en la cabeza!"},
    75: {"name": "Tornado de Fuego", "hit": "te chamuscó un mechón de pelo", "crit": "¡te succionó y te rostizó en segundos en el aire!"},
    76: {"name": "Pelea de Canguros", "hit": "te empujó con las manos", "crit": "¡te metió un doble patada voladora en el pecho!"},
    77: {"name": "Duelo de Puntería", "hit": "te pegó un balín en el brazo", "crit": "¡te metió un tiro en todo el centro de la frente!"},
    78: {"name": "Atrapados en el Ascensor", "hit": "te pisó el pie sin querer", "crit": "¡cortó los cables del ascensor y cayeron al vacío!"},
    79: {"name": "Ataque de Abejorros", "hit": "te picó un abejorro molesto", "crit": "¡te persiguió una colmena entera hasta el cansancio!"},
    80: {"name": "Avalancha de Piedras", "hit": "te pegó una piedrita en el casco", "crit": "¡te pasó por encima una roca de 3 toneladas!"},
    81: {"name": "Hockey sobre Hielo", "hit": "te empujó contra la pared de acrílico", "crit": "¡te metió un palazo de hockey directo en la mandíbula!"},
    82: {"name": "Combate Pokémon", "hit": "te atacó con un placaje débil", "crit": "¡te metió un hiperrayo crítico que te debilitó al instante!"},
    83: {"name": "Tiro al Blanco Humano", "hit": "te rozó un dardo metálico", "crit": "¡te clavó un dardo directo en el ojo derecho!"},
    84: {"name": "Guerra de Chupetines", "hit": "te tiró un caramelo duro", "crit": "¡te metió un chupetín entero por la garganta!"},
    85: {"name": "Duelo de Pirómanos", "hit": "te quemó la manga con un encendedor", "crit": "¡te tiró una bomba molotov directa a los pies!"},
    86: {"name": "La Mansión del Terror", "hit": "te dio un susto leve por la espalda", "crit": "¡te mató del susto un fantasma que salió del placard!"},
    87: {"name": "Invasión de Ratas", "hit": "te mordió una bota de goma", "crit": "¡te devoró una horda de ratas de alcantarilla!"},
    88: {"name": "Soga Elástica", "hit": "te tiró un latigazo en la pierna", "crit": "¡se cortó la soga y te pegó en toda la cara con fuerza!"},
    89: {"name": "Duelo de Escobas", "hit": "te pegó un escobazo en los pies", "crit": "¡te partió el palo de madera de la escoba en la espalda!"},
    90: {"name": "Batalla de Tanques de Agua", "hit": "te tiró un chorro leve en el pecho", "crit": "¡te tiró un chorrazo a presión que te tiró al piso!"},
    91: {"name": "Boxeo de Canguros", "hit": "te pegó un gancho débil", "crit": "¡te metió un KO con sus guantes gigantes de cuero!"},
    92: {"name": "Lluvia de Yunque", "hit": "te cayó un tornillo pesado", "crit": "¡te cayó un yunque de 200 kilos estilo Correcaminos!"},
    93: {"name": "Apocalipsis Nuclear", "hit": "te afectó la radiación leve", "crit": "¡te cayó una ojiva nuclear directa en la cabeza!"},
    94: {"name": "Guerra de Naranjas", "hit": "te pegó una naranja ácida", "crit": "¡te reventó una naranja podrida directo en los ojos!"},
    95: {"name": "Duelo de Alquimistas", "hit": "te tiró una poción de humo molesto", "crit": "¡te tiró una poción de ácido que te derritió la armadura!"},
    96: {"name": "Esgrima de Luz", "hit": "te rozó el brazo con plasma", "crit": "¡te cortó en pedacitos con un sable de luz doble!"},
    97: {"name": "Pelea de Osos", "hit": "te dio un zarpazo leve", "crit": "¡un oso grizzly te dio un abrazo mortal rompehuesos!"},
    98: {"name": "Tiroteo de Nieve", "hit": "te tiró una bola de hielo duro", "crit": "¡te sepultó bajo un alud gigante congelado!"},
    99: {"name": "Caza de Dragones", "hit": "te quemó el escudo de madera", "crit": "¡te tragó entero el dragón negro de la montaña!"},
    100: {"name": "Duelo del Fin del Mundo", "hit": "te rozó un rayo apocalíptico", "crit": "¡te borró de la existencia con un Big Bang cuántico!"}
}

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
# 🎮 VISTA INTERACTIVA PARA EL COMANDO /HELP_GAMES
# ==============================================================================
class HelpGamesView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)
        self.pagina_actual = 1
        self.max_paginas = 4

    def generar_embed(self):
        embed = discord.Embed(
            title="🎮 Lista Completa de Juegos (1-100)",
            description="¡Elegí el número perfecto para desafiar a tu rival en `/juego`! 🥊✨\n",
            color=discord.Color.from_rgb(0, 240, 255)
        )
        
        inicio = (self.pagina_actual - 1) * 25 + 1
        fin = self.pagina_actual * 25
        
        texto_juegos = ""
        for i in range(inicio, fin + 1):
            if i in JUEGOS_DETALLES:
                texto_juegos += f"**`#{i:02d}`** — {JUEGOS_DETALLES[i]['name']}\n"
        
        embed.add_field(name=f"📖 Página {self.pagina_actual} de {self.max_paginas}", value=texto_juegos, inline=False)
        embed.set_footer(text="ComboBOT 2026 | Desafía con /juego [numero] [@rival] 🛸")
        return embed

    @discord.ui.button(label="◀️ Anterior", style=discord.ButtonStyle.secondary)
    async def anterior_btn(self, inter: discord.Interaction, button: discord.ui.Button):
        if self.pagina_actual > 1:
            self.pagina_actual -= 1
            await inter.response.edit_message(embed=self.generar_embed(), view=self)
        else:
            await inter.response.send_message("❌ Ya estás en la primera página.", ephemeral=True)

    @discord.ui.button(label="Siguiente ▶️", style=discord.ButtonStyle.primary)
    async def siguiente_btn(self, inter: discord.Interaction, button: discord.ui.Button):
        if self.pagina_actual < self.max_paginas:
            self.pagina_actual += 1
            await inter.response.edit_message(embed=self.generar_embed(), view=self)
        else:
            await inter.response.send_message("❌ Ya estás en la última página.", ephemeral=True)


# ==============================================================================
# 4. EVENTOS Y CONEXIÓN SEGURA A LAVALINK
# ==============================================================================
async def conectar_node():
    """Conecta a Lavalink con reintentos y compatibilidad v4 forzada 🛡️🎵"""
    nodos_config = [
        # Nodo activo reportado hoy 🟢
        {"uri": "ssl://lavalink.derpystuff.net:443", "password": "youshallnotpass"},
        # Nodo secundario alternativo 🪐
        {"uri": "ssl://lavalink-v4.m9dev.ru:443", "password": "youshallnotpass"}
    ]
    
    for config in nodos_config:
        # El resto de tu código del bucle va acá abajo...
        try:
            print(f"🔄 Intentando conectar al nodo: {config['uri']}...", flush=True)
            
            node = wavelink.Node(
                uri=config["uri"], 
                password=config["password"],
                inactive_player_timeout=300
            )
            
            await wavelink.Pool.connect(nodes=[node], client=bot)
            print(f"🎵 [Lavalink] ¡Conectado exitosamente a {config['uri']}! 🎸", flush=True)
            return
        except Exception as e:
            print(f"⚠️ No se pudo conectar a {config['uri']}: {e}", flush=True)
            try:
                wavelink.Pool.close()
            except:
                pass
            await asyncio.sleep(2)

    print("❌ Todos los nodos fallaron. Reintentando ciclo en 15 segundos...", flush=True)
    await asyncio.sleep(15)
    bot.loop.create_task(conectar_node())

@bot.event
async def on_wavelink_node_ready(payload: wavelink.NodeReadyEvent):
    print(f"✅ Nodo de Wavelink listo: {payload.node.identifier}", flush=True)

@bot.event
async def on_ready():
    print(f"📡 Enlace cuántico establecido. {bot.user.name} online! 🌌", flush=True)
    try:
        sincronizados = await bot.tree.sync()
        print(f"🔄 Sincronizados {len(sincronizados)} comandos de barra.", flush=True)
    except Exception as e:
        print(f"❌ Error al sincronizar: {e}", flush=True)
    
    activity = discord.Activity(
        type=discord.ActivityType.watching, 
        name="¡ComboBOT Premium! 🚀 | /help 🛸"
    )
    await bot.change_presence(activity=activity)
    await conectar_node()


# ==============================================================================
# 🎮 VISTA DE BOTONES PARA EL REPRODUCTOR (ESTILO UZOX IDÉNTICO)
# ==============================================================================
class ReproductorView(discord.ui.View):
    def __init__(self, player: wavelink.Player):
        super().__init__(timeout=None)
        self.player = player

    # Fila 1: Control de reproducción
    @discord.ui.button(emoji="⏮️", style=discord.ButtonStyle.secondary, row=0)
    async def prev_btn(self, inter: discord.Interaction, button: discord.ui.Button):
        if not self.player.playing:
            return await inter.response.send_message("❌ No hay nada sonando.", ephemeral=True)
        await self.player.seek(0)
        await inter.response.send_message("⏮️ Pista reiniciada.", ephemeral=True)

    @discord.ui.button(emoji="⏸️", style=discord.ButtonStyle.primary, row=0)
    async def pause_btn(self, inter: discord.Interaction, button: discord.ui.Button):
        if not self.player.playing:
            return await inter.response.send_message("❌ No hay música sonando.", ephemeral=True)
        
        if self.player.paused:
            await self.player.pause(False)
            button.emoji = "⏸️"
            button.style = discord.ButtonStyle.primary
            await inter.response.edit_message(view=self)
            await inter.followup.send("▶️ Música reanudada.", ephemeral=True)
        else:
            await self.player.pause(True)
            button.emoji = "▶️"
            button.style = discord.ButtonStyle.success
            await inter.response.edit_message(view=self)
            await inter.followup.send("⏸️ Música pausada.", ephemeral=True)

    @discord.ui.button(emoji="⏭️", style=discord.ButtonStyle.secondary, row=0)
    async def skip_btn(self, inter: discord.Interaction, button: discord.ui.Button):
        if not self.player.playing:
            return await inter.response.send_message("❌ No hay nada en la lista.", ephemeral=True)
        await self.player.skip()
        await inter.response.send_message("⏭️ Siguiente canción.", ephemeral=True)

    # Fila 2: Control de volumen
    @discord.ui.button(emoji="🔇", style=discord.ButtonStyle.secondary, row=1)
    async def mute_btn(self, inter: discord.Interaction, button: discord.ui.Button):
        if self.player.volume > 0:
            self.player.old_volume = self.player.volume
            await self.player.set_volume(0)
            button.emoji = "🔊"
            await inter.response.edit_message(view=self)
            await inter.followup.send("🔇 Bot silenciado.", ephemeral=True)
        else:
            old_vol = getattr(self.player, 'old_volume', 50)
            await self.player.set_volume(old_vol)
            button.emoji = "🔇"
            await inter.response.edit_message(view=self)
            await inter.followup.send(f"🔊 Volumen restablecido a {old_vol}%.", ephemeral=True)

    @discord.ui.button(emoji="🔉", style=discord.ButtonStyle.secondary, row=1)
    async def vol_down_btn(self, inter: discord.Interaction, button: discord.ui.Button):
        nuevo_vol = max(self.player.volume - 15, 0)
        await self.player.set_volume(nuevo_vol)
        await inter.response.send_message(f"🔉 Volumen bajado a: {nuevo_vol}%", ephemeral=True)

    @discord.ui.button(emoji="🔊", style=discord.ButtonStyle.secondary, row=1)
    async def vol_up_btn(self, inter: discord.Interaction, button: discord.ui.Button):
        nuevo_vol = min(self.player.volume + 15, 100)
        await self.player.set_volume(nuevo_vol)
        await inter.response.send_message(f"🔊 Volumen subido a: {nuevo_vol}%", ephemeral=True)

    # Fila 3: Utilidades
    @discord.ui.button(emoji="📄", style=discord.ButtonStyle.secondary, row=2)
    async def lyrics_btn(self, inter: discord.Interaction, button: discord.ui.Button):
        await inter.response.send_message("📄 Buscando la letra de la canción...", ephemeral=True)

    @discord.ui.button(emoji="💾", style=discord.ButtonStyle.secondary, row=2)
    async def save_btn(self, inter: discord.Interaction, button: discord.ui.Button):
        await inter.response.send_message("💾 ¡Canción guardada en tus favoritos!", ephemeral=True)

    @discord.ui.button(emoji="♾️", style=discord.ButtonStyle.secondary, row=2)
    async def loop_btn(self, inter: discord.Interaction, button: discord.ui.Button):
        loop_state = getattr(self.player, 'loop_track', False)
        self.player.loop_track = not loop_state
        estado = "ACTIVADO" if not loop_state else "DESACTIVADO"
        await inter.response.send_message(f"♾️ Bucle de pista {estado}.", ephemeral=True)

    # Fila 4: Bucle / Apagar / Shuffle
    @discord.ui.button(emoji="🔁", style=discord.ButtonStyle.secondary, row=3)
    async def loop_queue_btn(self, inter: discord.Interaction, button: discord.ui.Button):
        loop_q = getattr(self.player, 'loop_queue', False)
        self.player.loop_queue = not loop_q
        estado = "ACTIVADA" if not loop_q else "DESACTIVADA"
        await inter.response.send_message(f"🔁 Repetición de la lista {estado}.", ephemeral=True)

    @discord.ui.button(emoji="⏹️", style=discord.ButtonStyle.danger, row=3)
    async def stop_btn(self, inter: discord.Interaction, button: discord.ui.Button):
        await self.player.disconnect()
        for child in self.children:
            child.disabled = True
        await inter.response.edit_message(view=self)
        await inter.followup.send("⏹️ Sesión de música finalizada.", ephemeral=True)

    @discord.ui.button(emoji="🔀", style=discord.ButtonStyle.secondary, row=3)
    async def shuffle_btn(self, inter: discord.Interaction, button: discord.ui.Button):
        if len(self.player.queue) > 1:
            lista_temp = list(self.player.queue)
            random.shuffle(lista_temp)
            self.player.queue.clear()
            for track in lista_temp:
                await self.player.queue.put(track)
            await inter.response.send_message("🔀 ¡Lista de reproducción mezclada!", ephemeral=True)
        else:
            await inter.response.send_message("❌ No hay suficientes canciones para mezclar.", ephemeral=True)


# ==============================================================================
# 🎮 MOTOR DE REPRODUCCIÓN (ESTILO VISUAL UZOX CON BORDE AZUL)
# ==============================================================================
async def reproducir_tema(interaction: discord.Interaction, busqueda: str, source):
    """Función interna para buscar de inmediato, conectar y reproducir con estilo Uzox en azul 🛠️🎶"""
    if not interaction.user.voice:
        return await interaction.followup.send("❌ ¡Tenés que estar en un canal de voz! 🎤")
    
    player: wavelink.Player = interaction.guild.voice_client

    if not player:
        try:
            player = await interaction.user.voice.channel.connect(cls=wavelink.Player)
        except Exception as e:
            return await interaction.followup.send(f"❌ Error al conectar al canal: {e}")

    query = busqueda
    if not (busqueda.startswith("http://") or busqueda.startswith("https://")):
        if source == wavelink.TrackSource.YouTube:
            query = f"ytsearch:{busqueda}"
        elif source == wavelink.TrackSource.Spotify:
            query = f"spsearch:{busqueda}"
        elif source == wavelink.TrackSource.SoundCloud:
            query = f"scsearch:{busqueda}"

    # 🔄 SISTEMA DE BÚSQUEDA CON MULTI-PLAN DE RESPALDO ANTI-BLOQUEOS 🛡️
    tracks = None
    try:
        # Plan A: Intenta la búsqueda configurada originalmente (o enlace directo)
        print(f"🔍 Intentando búsqueda principal: {query}", flush=True)
        tracks = await wavelink.Playable.search(query)
    except Exception as e:
        print(f"⚠️ Falló Plan A ({e}). Intentando alternativa en Spotify...", flush=True)
        try:
            # Plan B: Si falla (por bloqueo de IP), forzamos Spotify
            query_spotify = f"spsearch:{busqueda}"
            tracks = await wavelink.Playable.search(query_spotify)
        except Exception as e2:
            print(f"⚠️ Falló Plan B ({e2}). Intentando alternativa en SoundCloud...", flush=True)
            try:
                # Plan C: Si todo lo demás muere, SoundCloud salva las papas
                query_sc = f"scsearch:{busqueda}"
                tracks = await wavelink.Playable.search(query_sc)
            except Exception as e3:
                print(f"❌ Error total en todas las plataformas: {e3}", flush=True)
                return await interaction.followup.send("⚠️ No se pudo procesar la búsqueda en ninguna plataforma. ¡Probá con el enlace directo! 🔗")

    if not tracks:
        return await interaction.followup.send("⚠️ No se encontraron resultados para tu búsqueda.")

    track = tracks[0]
    player.queue.put(track)
    
    segundos = int(track.length / 1000)
    minutos, segundos = divmod(segundos, 60)
    duracion_formateada = f"{minutos:02d}:{segundos:02d}"

    # Embed con borde AZUL brillante 🎨🔵
    embed = discord.Embed(title="🎶 Now Playing", color=discord.Color.from_rgb(0, 240, 255))
    embed.add_field(name="**Track:**", value=f"`{track.title}`", inline=False)
    embed.add_field(name="**Requested By:**", value=interaction.user.mention, inline=False)
    embed.add_field(name="**Duration:**", value=f"`{duracion_formateada}`", inline=False)
    
    if track.artwork:
        embed.set_thumbnail(url=track.artwork)

    embed.set_footer(text="~ /equalizer for custom track control ~")

    if not player.playing:
        await player.play(player.queue.get())
        await interaction.followup.send(embed=embed, view=ReproductorView(player))
    else:
        embed_queue = discord.Embed(
            title="📝 Añadida a la lista",
            description=f"**{track.title}** en cola.",
            color=discord.Color.from_rgb(0, 240, 255)
        )
        await interaction.followup.send(embed=embed_queue)


# ==============================================================================
# 🎮 COMANDOS DE BARRA (MÚSICA, JUEGOS Y SOPORTE)
# ==============================================================================
@bot.tree.command(name="play", description="Busca y reproduce música de YouTube, Spotify o SoundCloud 🎵")
@discord.app_commands.describe(
    busqueda="Nombre de la canción o enlace directo 🔗",
    plataforma="Elegí dónde buscar (opcional, por defecto YouTube) 💿"
)
@discord.app_commands.choices(plataforma=[
    discord.app_commands.Choice(name="🔴 YouTube", value="youtube"),
    discord.app_commands.Choice(name="🟢 Spotify", value="spotify"),
    discord.app_commands.Choice(name="🟠 SoundCloud", value="soundcloud")
])
async def play(interaction: discord.Interaction, busqueda: str, plataforma: str = "youtube"):
    await interaction.response.defer()
    
    source = wavelink.TrackSource.YouTube
    if plataforma == "spotify":
        source = wavelink.TrackSource.Spotify
    elif plataforma == "soundcloud":
        source = wavelink.TrackSource.SoundCloud
        
    await reproducir_tema(interaction, busqueda, source)

@play.autocomplete("busqueda")
async def play_autocomplete(interaction: discord.Interaction, current: str):
    if not current or len(current) < 2:
        return []
    try:
        node = wavelink.Pool.get_node()
        if not node:
            return [discord.app_commands.Choice(name=f"🔍 Buscar: {current}", value=current)]
            
        tracks = await asyncio.wait_for(
            wavelink.Playable.search(f"ytsearch:{current}"),
            timeout=1.2
        )
        if tracks:
            return [discord.app_commands.Choice(name=f"🎵 {t.title[:80]}", value=t.uri) for t in tracks[:5]]
    except Exception:
        pass
    
    return [discord.app_commands.Choice(name=f"🔍 Buscar: {current}", value=current)]
    

@bot.tree.command(name="stop", description="Detiene la música y desconecta al bot ⏹️")
async def stop(interaction: discord.Interaction):
    player: wavelink.Player = interaction.guild.voice_client
    if not player:
        return await interaction.response.send_message("❌ El bot no está en ningún canal de voz. 💨", ephemeral=True)
    
    await player.disconnect()
    await interaction.response.send_message("⏹️ Música detenida. ComboBOT fuera del canal. 🛸")


# --- COMANDO /JUEGO NATIVO 🥊 ---
@bot.tree.command(name="juego", description="Desafía a un amigo a un juego interactivo de la lista 🥊")
@discord.app_commands.describe(
    numero="Elegí un número de juego de la lista (1-100) 🕹️",
    rival="Mencioná a tu oponente para el duelo 🎯"
)
async def juego(interaction: discord.Interaction, numero: int, rival: discord.User):
    if rival.bot:
        return await interaction.response.send_message("❌ No podés desafiar a un bot. ¡Buscate un rival de verdad! 🤖", ephemeral=True)
    
    if rival.id == interaction.user.id:
        return await interaction.response.send_message("❌ No podés jugar contra vos mismo... Sería muy triste. 😢", ephemeral=True)

    if numero not in JUEGOS_DETALLES:
        return await interaction.response.send_message("❌ Ese número de juego no existe. ¡Usa `/help_games` para ver todos! 🎮", ephemeral=True)

    config = JUEGOS_DETALLES[numero]
    view = JuegoMasivoView(interaction.user, rival, numero, config)
    
    embed = discord.Embed(
        title=f"🕹️ JUEGO #{numero}: {config['name']}", 
        description=f"⚔️ **{interaction.user.mention}** acaba de desafiar a **{rival.mention}**.\n\n**Turno de atacar:** {interaction.user.mention}",
        color=discord.Color.red()
    )
    embed.add_field(name=f"🥊 {interaction.user.name}", value="❤️ **HP:** `100/100`", inline=True)
    embed.add_field(name=f"🥊 {rival.name}", value="❤️ **HP:** `100/100`", inline=True)
    embed.set_footer(text="¡Que gane el mejor! 💥")

    await interaction.response.send_message(embed=embed, view=view)


# --- COMANDO /HELP_GAMES NATIVO 🎮 ---
@bot.tree.command(name="help_games", description="Muestra la lista interactiva de los 100 juegos disponibles 🕹️")
async def help_games(interaction: discord.Interaction):
    view = HelpGamesView()
    await interaction.response.send_message(embed=view.generar_embed(), view=view)


# ==============================================================================
# 🛸 COMANDOS DE AYUDA Y SOPORTE
# ==============================================================================
class HelpButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
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
        name="🎵 Música", 
        value=(
            "• `/play [canción]` - Busca y reproduce música 🔴🟢🟠\n"
            "• `/stop` - Detiene la música por completo ⏹"
        ), 
        inline=False
    )
    
    embed.add_field(
        name="🎮 Entretenimiento e Interacción", 
        value=(
            "• `/juego [1-100] [@rival]` - Desafía a un amigo a un juego interactivo 🥊\n"
            "• `/help_games` - Mira el catálogo de los 100 juegos 🕹️\n"
            "• `/mine` - Minería espacial para conseguir StarChips 🌌\n"
            "• `/cyber_roulette` - Probá tu suerte en el azar cuántico 🎰"
        ), 
        inline=False
    )
    
    embed.set_footer(text="ComboBOT 2026 | Desarrollado con ❤️")
    await interaction.response.send_message(embed=embed, view=HelpButtons())

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
    
    embed.add_field(name="🎮 Juegos Multijugador", value="`/juego [1-100] [@rival]`, `/help_games`, `/mine`, `/cyber_roulette` 🥊", inline=False)
    embed.add_field(name="🎵 Sistema de Música", value="`/play`, `/stop` 🎶", inline=False)
    embed.set_footer(text="ComboBOT 2026 | Desarrollado con ❤️")
    
    await interaction.response.send_message(embed=embed)


# ==============================================================================
# --- COMANDOS EXTRAS DE ECONOMÍA ---
# ==============================================================================
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
