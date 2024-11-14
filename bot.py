import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncio
import DB
import traceback
from datetime import datetime

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Créer une instance du bot avec le préfixe '!'
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="/", intents=intents)

db = DB.DB("hellbot")

# Variable globale pour stocker les invitations
invites_before = {}

@bot.event
async def on_ready():
    print(f'{bot.user} est connecté à Discord!')
    # Charger les invitations existantes pour chaque serveur
    for guild in bot.guilds:
        invites_before[guild.id] = await guild.invites()

async def log_error(error: Exception, ctx = None):
    """Envoie les erreurs dans le canal des super logs"""
    logs_channel_id = db.get("logs_channel_id")
    if not logs_channel_id:
        return  # Si pas de canal configuré, on ne fait rien
    
    channel = bot.get_channel(logs_channel_id)
    if not channel:
        return
    
    # Créer un embed pour l'erreur
    embed = discord.Embed(
        title="⚠️ Erreur Détectée",
        description="Une erreur s'est produite lors de l'exécution du bot",
        color=discord.Color.red(),
        timestamp=datetime.now()
    )
    
    # Ajouter les détails de l'erreur
    error_details = "".join(traceback.format_exception(type(error), error, error.__traceback__))
    if len(error_details) > 1024:  # Discord limite la taille des fields
        error_details = error_details[:1021] + "..."
    
    embed.add_field(name="Type d'erreur", value=type(error).__name__, inline=False)
    embed.add_field(name="Message d'erreur", value=str(error), inline=False)
    embed.add_field(name="Traceback", value=f"```python\n{error_details}```", inline=False)
    
    # Ajouter le contexte si disponible
    if ctx:
        embed.add_field(
            name="Contexte",
            value=f"Commande: {ctx.command}\nAuteur: {ctx.author}\nCanal: {ctx.channel}\nMessage: {ctx.message.content}",
            inline=False
        )
    
    await channel.send(embed=embed)

@bot.event
async def on_error(event, *args, **kwargs):
    """Capture les erreurs d'événements"""
    error = traceback.format_exc()
    await log_error(Exception(f"Erreur dans l'événement {event}:\n{error}"))

@bot.event
async def on_command_error(ctx, error):
    """Capture les erreurs de commandes"""
    await log_error(error, ctx)

@bot.event
async def on_invite_create(invite):
    logs_channel_id = db.get("logs_channel_id")
    if not logs_channel_id:
        return

    logs_channel = bot.get_channel(logs_channel_id)
    if logs_channel:
        embed = discord.Embed(
            title="Nouvelle Invitation Créée",
            color=discord.Color.blue()
        )
        embed.add_field(name="Créée par", value=invite.inviter.mention, inline=True)
        embed.add_field(name="Code", value=invite.code, inline=True)
        embed.add_field(name="Channel", value=invite.channel.mention, inline=True)
        if invite.max_uses:
            embed.add_field(name="Utilisations max", value=invite.max_uses, inline=True)
        if invite.expires_at:
            embed.add_field(name="Expire le", value=invite.expires_at.strftime("%d/%m/%Y à %H:%M"), inline=True)
        await logs_channel.send(embed=embed)

@bot.event
async def on_message_delete(message):
    logs_channel_id = db.get("logs_channel_id")
    if not logs_channel_id:
        return
    
    # Ignorer les messages des bots
    if message.author.bot:
        return

    logs_channel = bot.get_channel(logs_channel_id)
    if logs_channel:
        embed = discord.Embed(
            title="Message Supprimé",
            description=f"Un message a été supprimé dans {message.channel.mention}",
            color=discord.Color.red()
        )
        embed.add_field(name="Auteur", value=message.author.mention, inline=False)
        embed.add_field(name="Contenu", value=message.content or "Contenu non disponible", inline=False)
        await logs_channel.send(embed=embed)

@bot.event
async def on_message_edit(before, after):
    logs_channel_id = db.get("logs_channel_id")
    if not logs_channel_id:
        return
    
    # Ignorer les messages des bots
    if before.author.bot:
        return
    
    # Ignorer si le contenu n'a pas changé (par exemple, uniquement un embed ajouté)
    if before.content == after.content:
        return

    logs_channel = bot.get_channel(logs_channel_id)
    if logs_channel:
        embed = discord.Embed(
            title="Message Modifié",
            description=f"Un message a été modifié dans {before.channel.mention}",
            color=discord.Color.blue()
        )
        embed.add_field(name="Auteur", value=before.author.mention, inline=False)
        embed.add_field(name="Avant", value=before.content or "Contenu non disponible", inline=False)
        embed.add_field(name="Après", value=after.content or "Contenu non disponible", inline=False)
        embed.add_field(name="Lien", value=f"[Aller au message]({after.jump_url})", inline=False)
        await logs_channel.send(embed=embed)

@bot.event
async def on_member_join(member):
    logs_channel_id = db.get("logs_channel_id")
    if not logs_channel_id:
        return

    logs_channel = bot.get_channel(logs_channel_id)
    if logs_channel:
        # Récupérer les invitations après l'arrivée du membre
        invites_after = await member.guild.invites()
        
        # Trouver quelle invitation a été utilisée
        used_invite = None
        for invite_after in invites_after:
            invite_before = next((inv for inv in invites_before[member.guild.id] if inv.code == invite_after.code), None)
            if invite_before and invite_after.uses > invite_before.uses:
                used_invite = invite_after
                break

        # Mettre à jour la liste des invitations
        invites_before[member.guild.id] = invites_after

        # Créer l'embed de base pour le nouveau membre
        embed = discord.Embed(
            title="Nouveau Membre",
            description=f"{member.mention} a rejoint le serveur!",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed.add_field(name="Compte créé le", value=member.created_at.strftime("%d/%m/%Y à %H:%M"), inline=False)
        
        # Ajouter les informations sur l'invitation si trouvée
        if used_invite:
            embed.add_field(name="Invité par", value=used_invite.inviter.mention, inline=True)
            embed.add_field(name="Code d'invitation", value=used_invite.code, inline=True)
            embed.add_field(name="Utilisations", value=f"{used_invite.uses}/{used_invite.max_uses if used_invite.max_uses else '∞'}", inline=True)
        else:
            embed.add_field(name="Invitation", value="Non trouvée", inline=True)
        
        embed.set_footer(text=f"ID: {member.id}")
        await logs_channel.send(embed=embed)

@bot.event
async def on_member_remove(member):
    logs_channel_id = db.get("logs_channel_id")
    if not logs_channel_id:
        return

    logs_channel = bot.get_channel(logs_channel_id)
    if logs_channel:
        embed = discord.Embed(
            title="Membre Parti",
            description=f"{member.name}#{member.discriminator} a quitté le serveur",
            color=discord.Color.red()
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed.add_field(name="Avait rejoint le", value=member.joined_at.strftime("%d/%m/%Y à %H:%M"), inline=False)
        embed.set_footer(text=f"ID: {member.id}")
        await logs_channel.send(embed=embed)

@bot.event
async def on_message(message):
    # Ignorer les messages du bot
    if message.author.bot:
        return
    
    # Continuer le traitement des autres commandes
    await bot.process_commands(message)

    # Vérifier si c'est la commande $sync
    if message.content == "$sync":
        # Vérifier si l'auteur est un administrateur
        if message.author.guild_permissions.administrator:
            try:
                await bot.tree.sync()
                sync_message = await message.channel.send("🔄 Synchronisation des commandes en cours...")
                await message.delete()  # Supprimer la commande $sync
                await sync_message.edit(content="✅ Commandes synchronisées avec succès!", delete_after=5)
            except Exception as e:
                error_message = await message.channel.send(f"❌ Erreur lors de la synchronisation: {str(e)}", delete_after=5)
                await message.delete()
        else:
            # Si l'utilisateur n'est pas admin, supprimer sa commande et envoyer un message d'erreur temporaire
            warning = await message.channel.send("❌ Vous n'avez pas la permission d'utiliser cette commande.", delete_after=5)
            await message.delete()

@bot.command(name='hello')
async def hello(ctx):
    """Répond avec un message de salutation"""
    await ctx.send(f'👋 Bonjour {ctx.author.name}!')

@bot.command(name='ping')
async def ping(ctx):
    """Vérifie la latence du bot"""
    await ctx.send(f'Pong! Latence: {round(bot.latency * 1000)}ms')

# Lancer le bot
if __name__ == '__main__':
    bot.run(TOKEN)
