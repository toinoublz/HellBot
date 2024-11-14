import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Créer une instance du bot avec le préfixe '!'
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="/", intents=intents)

# ID du salon pour les logs (à remplacer par votre ID de salon)
LOGS_CHANNEL_ID = 1306683155260117133

@bot.event
async def on_ready():
    print(f'{bot.user} est connecté à Discord!')

@bot.event
async def on_message_delete(message):
    if LOGS_CHANNEL_ID is None:
        return
    
    # Ignorer les messages des bots
    if message.author.bot:
        return

    logs_channel = bot.get_channel(LOGS_CHANNEL_ID)
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
    if LOGS_CHANNEL_ID is None:
        return
    
    # Ignorer les messages des bots
    if before.author.bot:
        return
    
    # Ignorer si le contenu n'a pas changé (par exemple, uniquement un embed ajouté)
    if before.content == after.content:
        return

    logs_channel = bot.get_channel(LOGS_CHANNEL_ID)
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
    if LOGS_CHANNEL_ID is None:
        return

    logs_channel = bot.get_channel(LOGS_CHANNEL_ID)
    if logs_channel:
        embed = discord.Embed(
            title="Nouveau Membre",
            description=f"{member.mention} a rejoint le serveur!",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed.add_field(name="Compte créé le", value=member.created_at.strftime("%d/%m/%Y à %H:%M"), inline=False)
        embed.set_footer(text=f"ID: {member.id}")
        await logs_channel.send(embed=embed)

@bot.event
async def on_member_remove(member):
    if LOGS_CHANNEL_ID is None:
        return

    logs_channel = bot.get_channel(LOGS_CHANNEL_ID)
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

@bot.command(name='hello')
async def hello(ctx):
    """Répond avec un message de salutation"""
    await ctx.send(f'👋 Bonjour {ctx.author.name}!')

@bot.command(name='ping')
async def ping(ctx):
    """Vérifie la latence du bot"""
    await ctx.send(f'Pong! Latence: {round(bot.latency * 1000)}ms')

@bot.command(name='setlogschannel')
@commands.has_permissions(administrator=True)
async def set_logs_channel(ctx):
    """Définit le salon actuel comme salon de logs"""
    global LOGS_CHANNEL_ID
    LOGS_CHANNEL_ID = ctx.channel.id
    await ctx.send(f"Ce salon a été défini comme salon de logs! ID: {LOGS_CHANNEL_ID}")

# Lancer le bot
if __name__ == '__main__':
    bot.run(TOKEN)
