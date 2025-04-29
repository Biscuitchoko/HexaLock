# HexaLock Bot - Guide de démarrage

## Prérequis
1. Un compte **Discord** avec un bot créé.  
2. Une **clé API** de **VirusTotal**.  
3. Python 3.x installé sur ta machine.

## Installation
1. Clone ou télécharge ce projet.
2. Installe les dépendances :  
```bash
pip install discord.py requests python-dotenv
```
3. Crée un fichier `.env` à partir de `.env.example` et remplis-le avec ton `DISCORD_TOKEN`, `VIRUSTOTAL_API_KEY` et l'ID du rôle admin.

## Lancer le bot
Exécute le fichier `bot.py` :  
```bash
python bot.py
```

## Hébergement 24/7 (optionnel)
1. Crée un compte sur [Railway.app](https://railway.app).
2. Crée un nouveau projet, sélectionne **"Deploy from GitHub"**.
3. Connecte ton dépôt GitHub contenant ce projet et suis les instructions pour l’hébergement.



Bonne chance avec HexaLock !  
