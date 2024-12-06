import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncio
import DB
import traceback
from datetime import datetime
import modals as md
import hellcup as hc

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
        invites_before[guild.id] = {inv.code: inv for inv in invites_before[guild.id]}

    hellcup_guild = bot.get_guild(db.get("hellcup_guild_id"))
    await bot.change_presence(
        activity=discord.Activity(
            name=f"{len(hellcup_guild.members)} gens (trop) cools !",
            type=discord.ActivityType.watching,
        )
    )

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
    # embed.add_field(name="Message d'erreur", value=str(error), inline=False)
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
async def on_command_error(ctx: commands.Context, error: commands.CommandError):
    """Capture les erreurs de commandes"""
    await log_error(error, ctx)

@bot.event
async def on_invite_create(invite: discord.Invite):
    logs_channel_id = db.get("logs_channel_id")
    if not logs_channel_id:
        return

    logs_channel = bot.get_channel(logs_channel_id)
    if logs_channel:
        embed = discord.Embed(
            title="Nouvelle Invitation Créée",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        embed.add_field(name="Créée par", value=invite.inviter.mention, inline=True)
        embed.add_field(name="Code", value=invite.code, inline=True)
        embed.add_field(name="Channel", value=invite.channel.mention, inline=True)
        if invite.max_uses:
            embed.add_field(name="Utilisations max", value=invite.max_uses, inline=True)
        if invite.expires_at:
            embed.add_field(name="Expire le", value=invite.expires_at.strftime("%d/%m/%Y à %H:%M"), inline=True)
        embed.set_footer(text=f"ID: {invite.inviter.id}")
        await logs_channel.send(embed=embed)
    invites_before[invite.guild.id] = await invite.guild.invites()
    invites_before[invite.guild.id] = {inv.code: inv for inv in invites_before[invite.guild.id]}

@bot.event
async def on_message_delete(message: discord.Message):
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
            color=discord.Color.red(),
            timestamp=datetime.now()
        )
        embed.add_field(name="Auteur", value=message.author.mention, inline=False)
        embed.add_field(name="Contenu", value=message.content or "Contenu non disponible", inline=False)
        embed.set_footer(text=f"ID: {message.author.id}")
        await logs_channel.send(embed=embed)

@bot.event
async def on_message_edit(before: discord.Message, after: discord.Message):
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
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        embed.add_field(name="Auteur", value=before.author.mention, inline=False)
        embed.add_field(name="Avant", value=before.content or "Contenu non disponible", inline=False)
        embed.add_field(name="Après", value=after.content or "Contenu non disponible", inline=False)
        embed.add_field(name="Lien", value=f"[Aller au message]({after.jump_url})", inline=False)
        embed.set_footer(text=f"ID: {before.author.id}")
        await logs_channel.send(embed=embed)

@bot.event
async def on_member_join(member: discord.Member):
    logs_channel_id = db.get("logs_channel_id")
    if not logs_channel_id:
        return

    await member.add_roles(member.guild.get_role(db.get("newbie_role_id")))

    await bot.change_presence(
        activity=discord.Activity(
            name=f"{len(member.guild.members)} gens (trop) cools !",
            type=discord.ActivityType.watching,
        )
    )

    logs_channel = bot.get_channel(logs_channel_id)
    if logs_channel:
        # Récupérer les invitations après l'arrivée du membre
        invites_after = await member.guild.invites()
        invites_after = {inv.code: inv for inv in invites_after}

        # Trouver quelle invitation a été utilisée
        used_invite = None
        for invite_after_code, invite_after in invites_after.items():
            if invite_after_code in invites_before[member.guild.id] and invite_after.uses > invites_before[member.guild.id][invite_after_code].uses:
                used_invite = invite_after
                break

        # Mettre à jour la liste des invitations
        invites_before[member.guild.id] = await member.guild.invites()
        invites_before[member.guild.id] = {inv.code: inv for inv in invites_before[member.guild.id]}

        # Créer l'embed de base pour le nouveau membre
        embed = discord.Embed(
            title="Nouveau Membre",
            description=f"{member.mention} a rejoint le serveur!",
            color=discord.Color.green(),
            timestamp=datetime.now()
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
async def on_member_remove(member: discord.Member):
    logs_channel_id = db.get("logs_channel_id")
    if not logs_channel_id:
        return

    logs_channel = bot.get_channel(logs_channel_id)
    if logs_channel:
        embed = discord.Embed(
            title="Membre Parti",
            description=f"{member.display_name} a quitté le serveur",
            color=discord.Color.red(),
            timestamp=datetime.now()
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed.add_field(name="Avait rejoint le", value=member.joined_at.strftime("%d/%m/%Y à %H:%M"), inline=False)
        embed.set_footer(text=f"ID: {member.id}")
        await logs_channel.send(embed=embed)

@bot.event
async def on_member_update(before: discord.Member, after: discord.Member):
    # Vérifier si le nom a changé
    if before.display_name != after.display_name:
        logs_channel_id = db.get("logs_channel_id")
        if not logs_channel_id:
            return

        logs_channel = bot.get_channel(logs_channel_id)
        if logs_channel:
            embed = discord.Embed(
                title="Changement de Pseudo",
                description=f"Un membre a changé son pseudo",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            embed.add_field(name="Membre", value=after.mention, inline=False)
            embed.add_field(name="Ancien pseudo", value=before.display_name, inline=True)
            embed.add_field(name="Nouveau pseudo", value=after.display_name, inline=True)
            embed.set_thumbnail(url=after.avatar.url if after.avatar else after.default_avatar.url)
            embed.set_footer(text=f"ID: {after.id}")
            await logs_channel.send(embed=embed)


@bot.event
async def on_interaction(interaction: discord.Interaction):
    if 'custom_id' in interaction.data:
        if interaction.data['custom_id'] == "init_spectator":
            if interaction.guild.get_role(db.get("registered_role_id")) not in interaction.user.roles:
                await interaction.user.add_roles(interaction.guild.get_role(db.get("spectator_role_id")))
                await interaction.response.send_message(":popcorn: Préparez vos popcorns, vous voici spectateur du tournoi !", ephemeral=True)
            else:
                await interaction.response.send_message(f":warning: {interaction.user.mention} :warning:\n\nVous êtes déjà inscrit, si vous voulez modifier votre inscription, merci de contacter un admin.", ephemeral=True)
        elif interaction.data['custom_id'] == "init_player":
            if interaction.guild.get_role(db.get("registered_role_id")) in interaction.user.roles:
                await interaction.response.send_message(f":warning: {interaction.user.mention} :warning:\n\nVous êtes déjà inscrit, si vous voulez modifier votre inscription, merci de contacter un admin.", ephemeral=True)
            else:
                await interaction.response.send_modal(md.RegisterModal())
        elif interaction.data['custom_id'] == "team_select":
            userMentionned = interaction.guild.get_member(int(interaction.data['values'][0]))
            if userMentionned == interaction.user:
                await interaction.response.send_message(f":warning: {interaction.user.mention} :warning:\n\nVous ne pouvez pas faire équipe avec vous-meme !", ephemeral=True)
            if userMentionned in interaction.guild.get_role(db.get("player_role_id")).members:
                await interaction.response.send_message(f":warning: {interaction.user.mention} :warning:\n\nLe joueur selectionné à déjà une équipe, si vous pensez que c'est une erreur, merci de voir avec un admin.", ephemeral=True)
            elif userMentionned in interaction.guild.get_role(db.get("spectator_role_id")).members:
                await interaction.response.send_message(f":warning: {interaction.user.mention} :warning:\n\nLe joueur selectionné est inscrit en tant que spectateur, pour y remédier, dites lui d'aller s'inscrire en tant que joueur dans le channel {interaction.guild.get_channel(db.get('rules_channel_id')).mention} !", ephemeral=True)
            elif userMentionned not in interaction.guild.get_role(db.get("registered_role_id")).members:
                await interaction.response.send_message(f":warning: {interaction.user.mention} :warning:\n\nLe joueur selectionné n'est pas encore inscrit, pour y remédier, dites lui d'aller s'inscrire en tant que joueur dans le channel {interaction.guild.get_channel(db.get('rules_channel_id')).mention} !", ephemeral=True)
            else:
                await interaction.response.defer()
                nicknames = await hc.create_team(interaction.user, userMentionned)
                await interaction.user.add_roles(interaction.guild.get_role(db.get("player_role_id")))
                await userMentionned.add_roles(interaction.guild.get_role(db.get("player_role_id")))
                teamRole = await interaction.guild.create_role(name='_'.join(nicknames))
                await interaction.user.add_roles(teamRole)
                await userMentionned.add_roles(teamRole)
                category = interaction.guild.get_channel(db.get("team_text_channels_category_id"))
                adminRole = interaction.guild.get_role(db.get("admin_role_id"))

                overwrites = {
                    interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    teamRole: discord.PermissionOverwrite(read_messages=True)
                    adminRole: discord.PermissionOverwrite(read_messages=True)
                }

                channel = await category.create_text_channel(f"team-{teamRole.name}", overwrites=overwrites)

                await interaction.followup.send(f":tada: {interaction.user.mention} :tada:\n\nVous faites maintenant équipe avec {userMentionned.mention} ! RDV dans le channel {channel.mention} pour échanger avec votre mate !", ephemeral=True)
                await userMentionned.send(f":tada: {interaction.user.mention} :tada:\n\nVous faites maintenant équipe avec {interaction.user.mention} ! RDV dans le channel {channel.mention} pour échanger avec votre mate ! Si jamais c'est une erreur, merci de contacter un admin.")
                embed = discord.Embed(
                    title="Nouvelle équipe",
                    description=f"{interaction.user.mention} et {userMentionned.mention} font maintenant équipe !",
                    color=discord.Color.green(),
                    timestamp=datetime.now()
                )
                embed.add_field(name="Nom de l'équipe", value=teamRole.name, inline=False)
                embed.add_field(name="Membres", value=f"{interaction.user.mention}\n{userMentionned.mention}", inline=False)
                await interaction.guild.get_channel(db.get("registration_channel_id")).send(embed=embed)


@bot.tree.command(name='team', description="Créer votre équipe pour finaliser votre inscription !")
async def team(interaction: discord.Interaction):
    if interaction.user in interaction.guild.get_role(db.get("player_role_id")).members:
        await interaction.response.send_message(f":warning: {interaction.user.mention} :warning:\n\nVous avez deja une equipe !", ephemeral=True)
    elif interaction.user in interaction.guild.get_role(db.get("spectator_role_id")).members:
        await interaction.response.send_message(f":warning: {interaction.user.mention} :warning:\n\nVous êtes inscrit en tant que spectateur, si jamais vous voulez jouer, rdv dans le channel {interaction.guild.get_channel(db.get('rules_channel_id')).mention} !", ephemeral=True)
    else:
        view = discord.ui.View()
        view.add_item(discord.ui.UserSelect(custom_id="team_select", max_values=1, placeholder="Qui sera votre binome ?", min_values=1))
        await interaction.response.send_message("Indiquez votre binôme", view=view, ephemeral=True)
    return



@bot.event
async def on_message(message: discord.Message):
    # Ignorer les messages du bot
    if message.author.bot:
        return

    # Continuer le traitement des autres commandes
    await bot.process_commands(message)

    if message.author.guild_permissions.administrator:

        # Vérifier si c'est la commande $sync
        if message.content == "$sync":
            # Vérifier si l'auteur est un administrateur
                try:
                    await message.delete()  # Supprimer la commande $sync
                    sync_message = await message.channel.send("🔄 Synchronisation des commandes en cours...")
                    syncRet = await bot.tree.sync()
                    await sync_message.edit(content="✅ Commandes synchronisées avec succès! " + str(syncRet), delete_after=5)
                except Exception as e:
                    await sync_message.edit(f"❌ Erreur lors de la synchronisation: {str(e)}")

        elif message.content.startswith("$initmessagebienvenue"):
            view = discord.ui.View(timeout=None)
            player = discord.ui.Button(style=discord.ButtonStyle.primary, label="Joueur !", custom_id="init_player")
            spectator = discord.ui.Button(style=discord.ButtonStyle.primary, label="Spectateur !", custom_id="init_spectator")
            view.add_item(player)
            view.add_item(spectator)
            e = discord.Embed(title="Bienvenue sur le serveur ! :wave:", color=discord.Color.green())
            e.add_field(name="Que venez vous faire sur le serveur ?", value="Si vous venez pour vous battre, cliquez sur le bouton \"Joueur !\", si vous venez pour observer le tournoi, cliquez sur le bouton \"Spectateur !\".", inline=False)
            e.set_footer(text=f"©HellBot")
            await message.guild.get_channel(db.get('rules_channel_id')).send(embed=e, view=view)

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
    bot.run(TOKEN, log_handler=None)
