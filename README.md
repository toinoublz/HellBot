# HellBot - Bot Discord Simple

Un bot Discord simple créé avec discord.py.

## Configuration

1. Créez un environnement virtuel (recommandé) :
```bash
python -m venv venv
```

2. Activez l'environnement virtuel :
- Windows :
```bash
venv\Scripts\activate
```

3. Installez les dépendances :
```bash
pip install -r requirements.txt
```

4. Configurez le token du bot :
- Allez sur le [Discord Developer Portal](https://discord.com/developers/applications)
- Créez une nouvelle application
- Dans la section "Bot", créez un bot et copiez son token
- Collez le token dans le fichier `.env` :
```
DISCORD_TOKEN=votre_token_ici
```

## Lancement du bot

```bash
python bot.py
```

## Commandes disponibles

- `/hello` : Le bot vous salue
- `/ping` : Vérifie la latence du bot

## Fonctionnalités

- Système de commandes simple
- Gestion des événements de base
- Configuration sécurisée avec variables d'environnement
