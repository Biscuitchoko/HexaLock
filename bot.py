import discord
import json
import requests
import os
from discord.ext import commands
from dotenv import load_dotenv
from web import keep_alive

# Lance le faux serveur web
keep_alive()

# Charger les variables d'environnement
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
KASPERSKY_MAP_URL = os.getenv('KASPERSKY_MAP_URL')

# Charger et sauvegarder config
CONFIG_FILE = 'config.json'

def load_config():
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

config = load_config()
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

def get_prefix(bot, message):
    return load_config().get("prefix", "!")

bot = commands.Bot(command_prefix=get_prefix, intents=intents)

# Liste des domaines suspects
suspect_domains = [
    "bit.ly", "tinyurl.com", "goo.gl", "ow.ly", "t.co", "is.gd", "buff.ly", "cutt.ly", "rebrand.ly",
    "shorte.st", "adf.ly", "linktr.ee", "lnkd.in", "smarturl.it", "snip.ly", "tiny.cc", "v.gd", "tr.im",
    "cli.re", "shorturl.at", "t.ly", "s.id", "qr.ae", "bit.do", "soo.gd", "mcaf.ee", "po.st", "x.co", "j.mp",
    "u.to", "qr.net", "ity.im", "q.gs", "adcrun.ch", "moourl.com", "short.cm", "short.io", "t2m.io",
    "shortly.cc", "shrtfly.com", "clk.im", "cuturl.in", "git.io", "rb.gy", "kutt.it", "bl.ink", "0x0.st",

    # Hébergeurs anonymes / fichiers
    "anonfiles.com", "anonym.to", "file.io", "send.express", "wetransfer.com", "mega.nz", "transfer.sh",
    "zippyshare.com", "upload.ee", "krakenfiles.com", "bayfiles.com", "dl.dropboxusercontent.com",
    "cdn.discordapp.com", "catbox.moe", "pixeldrain.com", "1fichier.com", "filebin.net", "terabox.com",
    "send.cm", "ufile.io", "sendspace.com", "turbobit.net", "nitroflare.com", "rapidgator.net",
    "mixdrop.co", "racaty.io", "fembed.com", "streamtape.com", "upfiles.io", "hxfile.co", "gofile.io",

    # Liens monétisés / redirections
    "ouo.io", "ouo.press", "urle.io", "gplinks.in", "droplink.co", "boost.ink", "bc.vc", "cpmlink.net",
    "fc.lc", "shortest.link", "psu.sh", "clk.sh", "shrinke.me", "tmearn.com", "tmearn.me",
    "shortlinks.co", "tech2link.com", "liiinks.co", "sub2unlock.com", "earnably.com",
    "link-target.net", "linkvertise.com", "linkbucks.com", "linkshrink.net", "shrinkearn.com",
    "cutwin.com", "shortzon.com", "short2win.com", "short.pe", "shorten.sh", "shortlink.st",
    "sh.st", "short.am", "adfoc.us", "viralgyan.in", "easyurl.net", "cashlink.cc", "adshort.co",

    # Domaines géolocalisés / peu connus / à noms complexes
    "location.cyou", "shorturl.link", "shorturl.gg", "shorturl.io", "shorturl.xyz", "shorturl.click",
    "shorturl.site", "shorturl.today", "shorturl.fun", "shorturl.biz", "shorturl.top", "shorturl.club",
    "shorturl.info", "shorturl.pro", "shorturl.store", "shorturl.tech", "shorturl.co", "shorturl.us",
    "shorturl.uk", "shorturl.in", "shorturl.ca", "shorturl.au", "shorturl.eu", "shorturl.de",
    "shorturl.fr", "shorturl.es", "shorturl.it", "shorturl.nl", "shorturl.be", "shorturl.ch",
    "shorturl.se", "shorturl.no", "shorturl.dk", "shorturl.fi", "shorturl.pl", "shorturl.cz",
    "shorturl.sk", "shorturl.hu", "shorturl.ro", "shorturl.bg", "shorturl.gr", "shorturl.tr",
    "shorturl.ru", "shorturl.ua", "shorturl.by", "shorturl.kz", "shorturl.cn", "shorturl.jp",
    "shorturl.kr", "shorturl.sg", "shorturl.my", "shorturl.id", "shorturl.ph", "shorturl.vn",
    "shorturl.th", "shorturl.hk", "shorturl.tw", "shorturl.pk", "shorturl.bd", "shorturl.lk",
    "shorturl.np", "shorturl.af", "shorturl.ir", "shorturl.sa", "shorturl.ae", "shorturl.qa",
    "shorturl.om", "shorturl.kw", "shorturl.bh", "shorturl.jo", "shorturl.lb", "shorturl.sy",
    "shorturl.iq", "shorturl.eg", "shorturl.ma", "shorturl.dz", "shorturl.tn", "shorturl.ly",
    "shorturl.sd", "shorturl.ss", "shorturl.et", "shorturl.ke", "shorturl.ug", "shorturl.tz",
    "shorturl.rw", "shorturl.bi", "shorturl.mw", "shorturl.zm", "shorturl.zw", "shorturl.na",
    "shorturl.bw", "shorturl.mz", "shorturl.ao", "shorturl.cd", "shorturl.cg", "shorturl.ga",
    "shorturl.cm", "shorturl.ng", "shorturl.sn", "shorturl.ml", "shorturl.ci", "shorturl.gh",
    "shorturl.tg", "shorturl.bf", "pornhub.com"
]

user_message_count = {}

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

        admin_mention = f"<@&{admin_role_id}>" if admin_role_id else "🚨"
        embed = discord.Embed(title="Lien suspect détecté !", color=discord.Color.red())
        embed.add_field(name="Utilisateur", value=message.author.mention, inline=False)
        embed.add_field(name="Domaines détectés", value=", ".join(found_domains), inline=False)
        embed.set_footer(text="⚠️ Le message a été supprimé automatiquement.")

        await message.channel.send(content=admin_mention, embed=embed)
        return

    # Anti-spam simple
    user_id = message.author.id
    user_message_count[user_id] = user_message_count.get(user_id, 0) + 1

    if user_message_count[user_id] > 10 and admin_role_id:
        await message.channel.send(f"<@&{admin_role_id}> ⚠️ {message.author.mention} a été expulsé pour spam.")
        await message.guild.kick(message.author, reason="Spam détecté")
        user_message_count[user_id] = 0

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
    embed = discord.Embed(title="Réglages", color=discord.Color.green())
    embed.add_field(name=f"{prefix}changeprefix <nouveau>", value="Change le préfixe du bot", inline=False)
    embed.add_field(name=f"{prefix}adminrole <id_du_role>", value="Définit le rôle admin", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def changeprefix(ctx, new_prefix: str):
    config = load_config()
    config["prefix"] = new_prefix
    save_config(config)
    await ctx.send(f"✅ Préfixe changé en `{new_prefix}`")

@bot.command()
async def adminrole(ctx, role_id: int):
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
    await ctx.send("🤖 Je suis HexaLock, un bot conçu pour vous assister sur Discord et sécuriser ce serveur. **Pour commencer, tapez** `!aide` **ou** `!réglages`.")


@bot.event
async def on_guild_join(guild):
    if guild.owner:
        try:
            await guild.owner.send(
                "👋 Merci de m'avoir ajouté sur votre serveur !\n\n"
                "🔧 Vous pouvez me configurer avec la commande `!réglages`\n"
                "📖 Et découvrir toutes mes commandes avec `!aide`\n\n"
                "🤖 – HexaLock, votre assistant de sécurité Discord"
            )
        except discord.Forbidden:
            print(f"Impossible d'envoyer un message à {guild.owner}. Permission refusée.")


bot.run(DISCORD_TOKEN)

