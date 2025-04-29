import threading
import web  # <- nouveau fichier que tu viens de créer
import os
from bot import client

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

threading.Thread(target=web.start).start()  # Lance le mini-serveur web
client.run(DISCORD_TOKEN)
