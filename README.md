# HellBot - Bot Discord de Modération et Suivi

Un bot Discord complet créé avec discord.py pour la modération et le suivi des activités du serveur.

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

### Système de Logs
- Suivi des messages supprimés
- Suivi des messages édités
- Logs dans un canal dédié

### Gestion des Membres
- Suivi des arrivées de nouveaux membres
- Suivi des départs de membres
- Tracking des invitations utilisées

### Base de Données
- Stockage persistant des données
- Configuration du serveur
- Historique des événements

### Autres Fonctionnalités
- Système de commandes simple
- Configuration sécurisée avec variables d'environnement
- Gestion des erreurs avec logs détaillés
