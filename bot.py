import discord
import json
import requests
import os
from discord.ext import commands
from dotenv import load_dotenv
from web import keep_alive
from collections import defaultdict
import asyncio
import random
import string
import io
from PIL import Image, ImageDraw, ImageFont

# Lance le faux serveur web
keep_alive()

bot = commands.Bot(command_prefix=get_prefix, intents=intents)

async def keep_alive_loop():
    await bot.wait_until_ready()
    while not bot.is_closed():
        try:
            async with aiohttp.ClientSession() as session:
                await session.get("http://localhost:8080/keepalive")
        except Exception as e:
            print(f"Erreur keepalive: {e}")
        await asyncio.sleep(300)  # 5 minutes

# Lance la tâche APRÈS avoir défini le bot
bot.loop.create_task(keep_alive_loop())

# Charger les variables d'environnement
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
KASPERSKY_MAP_URL = os.getenv('KASPERSKY_MAP_URL')

# Charger et sauvegarder config
CONFIG_FILE = 'config.json'

def load_config():
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4)

config = load_config()
# Ajout des intents nécessaires
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True  # Pour gérer les salons
intents.guild_messages = True  # Pour gérer les messages dans les salons

def get_prefix(bot, message):
    return load_config().get("prefix", "!")


def generate_captcha_text(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def create_captcha_image(text):
    width, height = 200, 80
    image = Image.new('RGB', (width, height), color=(255, 255, 255))
    try:
        font = ImageFont.truetype("fonts/arial.ttf", 40)
    except:
        font = ImageFont.load_default()

    draw = ImageDraw.Draw(image)
    draw.text((20, 20), text, font=font, fill=(0, 0, 0))

    # Brouillage basique
    for _ in range(10):
        x1, y1 = random.randint(0, width), random.randint(0, height)
        x2, y2 = random.randint(0, width), random.randint(0, height)
        draw.line(((x1, y1), (x2, y2)), fill=(0, 0, 0), width=1)

    output = io.BytesIO()
    image.save(output, format='PNG')
    output.seek(0)
    return output

# Liste des domaines suspects (tous ceux que tu m'as envoyés)
suspect_domains = [
    "bit.ly", "tinyurl.com", "goo.gl", "ow.ly", "t.co", "is.gd", "buff.ly", "cutt.ly", "rebrand.ly",
    "adf.ly", "short.ly", "shorte.st", "sh.st", "clicky.me", "adfoc.us", "linkbucks.com", "linkshrink.net",
    "v.gd", "q.gs", "bc.vc", "u.to", "shortlink.com", "moourl.com", "lnk.vc", "foc.ink", "tiny.cc",
    "ezurl.me", "lnk.gd", "clck.ru", "unbounce.com", "go2l.ink", "bc.vc", "web.st", "t2m.io", "zurl.ws",
    "1url.com", "2url.org", "4url.com", "5url.com", "6url.com", "7url.com", "8url.com", "9url.com", "xurl.com",
    "yurl.com", "linkxtra.com", "hit.ly", "getpocket.com", "short.io", "smarturl.it", "surl.li", "short.cm",
    "lnk.to", "page.link", "nlk.fi", "xr.com", "unfurlr.com", "shortlinks.co", "bit.do", "url4short.com",
    "redire.it", "simpler.link", "bitly.com", "linktree.com", "urlshortner.in", "clkim.com", "fast.link", 
    "linkz.us", "instant.ly", "shrten.com", "shrinkit.com", "shrinkme.io", "links.gd", "surl.me", "spurl.co",
    "linkmink.com", "shortify.link", "fakelink.com", "direct.to", "tru.ly", "sub.link", "shortlink.me"
]

user_message_count = defaultdict(int)
user_last_message_time = {}

@bot.event
async def on_ready():
    print(f"{bot.user} est en ligne.")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    config = load_config()
    prefix = config.get("prefix", "!")
    admin_role_id = config.get("admin_role_id")

    # Détection des domaines suspects
    content = message.content.lower()
    found_domains = [domain for domain in suspect_domains if domain in content]
    if found_domains:
        await message.delete()

        # Message simple sans embed
        admin_mention = f"<@&{admin_role_id}>" if admin_role_id else "🚨"
        await message.channel.send(f"{admin_mention} **Lien suspect détecté** !\n**Utilisateur :** {message.author.mention}\nDomaines détectés : {', '.join(found_domains)}\n⚠️ *Le message a été supprimé automatiquement.*")
        return

    # Anti-spam simple avec temporisation
    user_id = message.author.id
    current_time = asyncio.get_event_loop().time()

    # Limite d'intervalle de messages pour éviter le spam
    if user_id in user_last_message_time:
        time_diff = current_time - user_last_message_time[user_id]
        if time_diff < 2:  # Si un utilisateur envoie trop de messages dans un court laps de temps
            user_message_count[user_id] += 1
        else:
            user_message_count[user_id] = 1
    else:
        user_message_count[user_id] = 1

    user_last_message_time[user_id] = current_time

    if user_message_count[user_id] > 10:  # Si l'utilisateur envoie trop de messages
        await message.channel.send(f"<@&{admin_role_id}> ⚠️ {message.author.mention} a été expulsé pour spam.")
        await message.guild.kick(message.author, reason="Spam détecté")
        user_message_count[user_id] = 0  # Réinitialiser le compteur

    await bot.process_commands(message)

@bot.before_invoke
async def delete_command_message(ctx):
    try:
        await ctx.message.delete()
    except discord.Forbidden:
        pass

# Commandes
@bot.command()
async def kasperskymap(ctx):
    if KASPERSKY_MAP_URL:
        await ctx.send(f"Voici la carte Kaspersky : {KASPERSKY_MAP_URL}")
    else:
        await ctx.send("La carte Kaspersky n’est pas disponible.")

@bot.command()
async def verifylink(ctx, link: str):
    try:
        response = requests.get(link)
        response.raise_for_status()
        await ctx.send(f"✅ Le lien {link} est valide.")
    except requests.exceptions.RequestException as e:
        await ctx.send(f"❌ Lien invalide : {e}")

@bot.command()
async def aide(ctx):
    config = load_config()
    prefix = config.get("prefix", "!")
    embed = discord.Embed(title="Aide du Bot HexaLock", color=discord.Color.blue())
    embed.add_field(name=f"{prefix}kasperskymap", value="Affiche la carte Kaspersky", inline=False)
    embed.add_field(name=f"{prefix}verifylink [lien]", value="Vérifie un lien", inline=False)
    embed.add_field(name=f"{prefix}lockchannel", value="Verrouille le salon", inline=False)
    embed.add_field(name=f"{prefix}unlockchannel", value="Déverrouille le salon", inline=False)
    embed.add_field(name=f"{prefix}clearchannel", value="Nettoie le salon", inline=False)
    embed.add_field(name=f"{prefix}réglages", value="Voir les options de configuration", inline=False)
    embed.add_field(name=f"{prefix}info", value="Brève description du bot", inline=False)
    embed.set_footer(text="Bot HexaLock | Protection avancée")
    await ctx.send(embed=embed)

@bot.command()
async def réglages(ctx):
    config = load_config()
    prefix = config.get("prefix", "!")
    embed = discord.Embed(title="Réglages", color=discord.Color.black())
    embed.add_field(name=f"{prefix}changeprefix <nouveau>", value="Change le préfixe du bot", inline=False)
    embed.add_field(name=f"{prefix}captcha <nouveau>", value="Met en place le système de captcha", inline=False)
    embed.add_field(name=f"{prefix}adminrole <id_du_role>", value="Définit le rôle admin", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def changeprefix(ctx, new_prefix: str):
    config = load_config()
    config["prefix"] = new_prefix
    save_config(config)
    await ctx.send(f"✅ Préfixe changé en {new_prefix}")

@bot.command()
async def adminrole(ctx, role_id: int):
    if ctx.author.id != ctx.guild.owner_id:
        return await ctx.send("❌ Seul le propriétaire du serveur peut définir le rôle admin.")
    
    config = load_config()
    config["admin_role_id"] = role_id
    save_config(config)
    await ctx.send(f"✅ Rôle admin défini sur : <@&{role_id}>")


# Commandes admin
@bot.command()
async def lockchannel(ctx):
    admin_role_id = load_config().get("admin_role_id")
    if not any(role.id == admin_role_id for role in ctx.author.roles):
        return await ctx.send("❌ Tu n’as pas la permission.")
    overwrites = ctx.channel.overwrites_for(ctx.guild.default_role)
    overwrites.send_messages = False
    await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrites)
    await ctx.channel.edit(name=f"🔒-{ctx.channel.name}")
    await ctx.send("🔒 Salon verrouillé.")

@bot.command()
async def unlockchannel(ctx):
    admin_role_id = load_config().get("admin_role_id")
    if not any(role.id == admin_role_id for role in ctx.author.roles):
        return await ctx.send("❌ Tu n’as pas la permission.")
    overwrites = ctx.channel.overwrites_for(ctx.guild.default_role)
    overwrites.send_messages = True
    await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrites)
    if ctx.channel.name.startswith("🔒-"):
        await ctx.channel.edit(name=ctx.channel.name.replace("🔒-", "", 1))
    await ctx.send("🔓 Salon déverrouillé.")

@bot.command()
async def clearchannel(ctx, amount: int = 100):
    admin_role_id = load_config().get("admin_role_id")
    if not any(role.id == admin_role_id for role in ctx.author.roles):
        return await ctx.send("❌ Tu n’as pas la permission.")
    await ctx.channel.purge(limit=amount)
    await ctx.send(f"🧹 {amount} messages supprimés.", delete_after=5)

@bot.command()
async def info(ctx):
    await ctx.send("🤖 Je suis HexaLock, un bot conçu pour vous assister sur Discord et sécuriser ce serveur. **Pour commencer, tapez** `!aide` **ou** `!réglages.`")


@bot.event
async def on_guild_join(guild):
    if guild.owner:
        try:
            await guild.owner.send(
                "👋 Merci de m'avoir ajouté sur votre serveur !\n\n"
                "🔧 Vous pouvez me configurer avec la commande `!réglages` 🔑 - n'oubliez pas de reconfiguet le role admin à chaque M.A.J !\n"
                "📖 Et découvrir toutes mes commandes avec `!aide`\n\n"
                "🤖 – HexaLock, votre assistant de sécurité Discord"
            )
        except discord.Forbidden:
            print(f"Impossible d'envoyer un message à {guild.owner}. Permission refusée.")


@bot.command()
async def captcha(ctx, channel: discord.TextChannel, role: discord.Role):
    config = load_config()
    config["captcha_channel_id"] = channel.id
    config["captcha_role_id"] = role.id
    save_config(config)
    await ctx.send(f"✅ Captcha activé dans {channel.mention}, rôle attribué : {role.mention}")


@bot.event
async def on_member_join(member):
    config = load_config()
    channel_id = config.get("captcha_channel_id")
    role_id = config.get("captcha_role_id")
    
    if not channel_id or not role_id:
        return

    channel = member.guild.get_channel(channel_id)
    role = member.guild.get_role(role_id)

    if not channel or not role:
        return

    attempts = 3
    captcha_text = generate_captcha_text()
    image = create_captcha_image(captcha_text)

    embed = discord.Embed(title="Vérification Captcha",
                          description="Merci de confirmer que tu n'es pas un robot.\nTape **exactement** ce que tu vois dans l'image ci-dessous.",
                          color=discord.Color.orange())
    file = discord.File(image, filename="captcha.png")
    embed.set_image(url="attachment://captcha.png")

    msg = await channel.send(f"{member.mention}", embed=embed, file=file)

    def check(m):
        return m.author == member and m.channel == channel

    while attempts > 0:
        try:
            response = await bot.wait_for("message", check=check, timeout=60)
        except:
            break  # Timeout

        if response.content.strip().upper() == captcha_text:
            await member.add_roles(role, reason="Captcha réussi")
            await channel.send(f"✅ Bienvenue {member.mention}, tu as passé le captcha !", delete_after=10)
            await msg.delete()
            await response.delete()
            return
        else:
            attempts -= 1
            await channel.send(f"❌ Mauvais captcha. Tentatives restantes : {attempts}", delete_after=5)
            await response.delete()

    await channel.send(f"❌ {member.mention} a échoué le captcha. Expulsion...")
    await member.kick(reason="Échec captcha")
    await msg.delete()


bot.run(DISCORD_TOKEN)
