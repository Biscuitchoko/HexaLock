import discord
from discord.ext import commands
import requests
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
KASPERSKY_MAP_URL = os.getenv('KASPERSKY_MAP_URL')
ADMIN_ROLE_ID = int(os.getenv('ADMIN_ROLE_ID'))  # Assure-toi que l'ID est un entier

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Liste des domaines suspects
suspect_domains = [
    # Raccourcisseurs classiques
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
    "shorturl.tg", "shorturl.bf"
]

# Anti-Spam
user_message_count = {}

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    user_id = message.author.id
    content = message.content.lower()

    # Détection de domaines suspects
    found_domains = [domain for domain in suspect_domains if domain in content]
    if found_domains:
        await message.delete()
        admin_mention = f"<@&{ADMIN_ROLE_ID}>"
        alert_msg = (
            f"{admin_mention} 🚨 **Lien suspect détecté !**\n"
            f"Utilisateur: {message.author.mention}\n"
            f"Domaines détectés : ```{', '.join(found_domains)}```\n"
            "⚠️ Le message a été supprimé automatiquement."
        )
        await message.channel.send(alert_msg)
        return

    # Anti-spam : plus de 10 messages rapidement
    user_message_count[user_id] = user_message_count.get(user_id, 0) + 1

    if user_message_count[user_id] > 10:
        admin_mention = f"<@&{ADMIN_ROLE_ID}>"
        await message.channel.send(f"{admin_mention} ⚠️ {message.author.mention} a été expulsé pour spam.")
        await message.guild.kick(message.author, reason="Spam détecté")
        user_message_count[user_id] = 0

    await bot.process_commands(message)

# Supprimer automatiquement les messages contenant des commandes
@bot.before_invoke
async def delete_command_message(ctx):
    try:
        await ctx.message.delete()
    except discord.Forbidden:
        pass  # Si le bot n'a pas la permission de supprimer, ignorer

# Commandes du bot

@bot.command()
async def kasperskymap(ctx):
    if KASPERSKY_MAP_URL:
        await ctx.send(f"Voici la carte Kaspersky : {KASPERSKY_MAP_URL}")
    else:
        await ctx.send("Désolé, la carte Kaspersky n'est pas disponible pour le moment.")

@bot.command()
async def verifylink(ctx, link: str):
    try:
        response = requests.get(link)
        response.raise_for_status()
        await ctx.send(f"✅ Le lien {link} est valide.")
    except requests.exceptions.RequestException as e:
        await ctx.send(f"❌ Le lien {link} est invalide : {e}")

@bot.command()
async def aide(ctx):
    embed = discord.Embed(
        title="Aide du Bot HexaLock",
        description="Voici les commandes disponibles :",
        color=discord.Color.blue()
    )
    embed.add_field(name="!kasperskymap", value="Affiche la carte mondiale des cybermenaces de Kaspersky.", inline=False)
    embed.add_field(name="!verifylink [lien]", value="Vérifie si un lien est valide.", inline=False)
    embed.add_field(name="!lockchannel", value="Verrouille le salon (admin uniquement).", inline=False)
    embed.add_field(name="!unlockchannel", value="Déverrouille le salon (admin uniquement).", inline=False)
    embed.add_field(name="!clearchannel", value="Supprime tous les messages du salon (admin uniquement).", inline=False)
    embed.add_field(name="Détection automatique", value="Détecte et bloque les liens suspects.", inline=False)
    embed.set_footer(text="Bot HexaLock | Protection avancée")
    await ctx.send(embed=embed)

@bot.command()
@commands.has_role(ADMIN_ROLE_ID)
async def lockchannel(ctx):
    overwrites = ctx.channel.overwrites_for(ctx.guild.default_role)
    overwrites.send_messages = False
    await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrites)
    await ctx.channel.edit(name=f"🔒-{ctx.channel.name}")
    await ctx.send("🔒 Ce salon est maintenant verrouillé pour les utilisateurs.")

@bot.command()
@commands.has_role(ADMIN_ROLE_ID)
async def unlockchannel(ctx):
    overwrites = ctx.channel.overwrites_for(ctx.guild.default_role)
    overwrites.send_messages = True
    await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrites)
    if ctx.channel.name.startswith("🔒-"):
        await ctx.channel.edit(name=ctx.channel.name.replace("🔒-", "", 1))
    await ctx.send("🔓 Ce salon est maintenant déverrouillé pour les utilisateurs.")

@bot.command()
@commands.has_role(ADMIN_ROLE_ID)
async def clearchannel(ctx, amount: int = 100):
    await ctx.channel.purge(limit=amount)
    await ctx.send(f"🧹 Salon nettoyé ({amount} messages supprimés).", delete_after=5)

bot.run(DISCORD_TOKEN)
