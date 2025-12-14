import os
import traceback
from datetime import datetime

import discord
from discord.ext import commands
from dotenv import load_dotenv
from easyDB import DB

import discord_logs as dl
import hellcup as hc
import layoutViews as lv
import modals as md

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Créer une instance du bot avec le préfixe '!'
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="/", intents=intents)


database = DB("hellbot")

log = dl.DiscordLog(database.get("logs_channel_id"))
# Variable globale pour stocker les invitations
invitesBefore = {}


@bot.event
async def on_ready():
    """
    Événement appelé lorsque le bot est connecté à Discord.

    Cet événement est appelé lorsque le bot est prêt à recevoir des commandes et des événements.
    Il s'agit d'un événement asynchrone qui est appelé automatiquement par Discord.

    Lorsque cet événement est appelé, le bot charge les invitations existantes pour chaque serveur,
    puis change son statut pour afficher le nombre de membres du serveur HellCup.
    """
    print(f"{bot.user} est connecté à Discord!")
    guild = bot.get_guild(database.get("hellcup_guild_id"))
    log.add_guild(guild)
    # Charger les invitations existantes pour chaque serveur
    for guild in bot.guilds:
        invitesBefore[guild.id] = await guild.invites()
        invitesBefore[guild.id] = {inv.code: inv for inv in invitesBefore[guild.id]}

    await bot.change_presence(
        activity=discord.Activity(
            name=f"{len(guild.members)} gens (trop) cools !",
            type=discord.ActivityType.watching,
        )
    )


async def log_error(error: Exception, ctx=None):
    """Envoie les erreurs dans le canal des super logs"""
    logsChannelId = database.get("logs_channel_id")
    if not logsChannelId:
        return  # Si pas de canal configuré, on ne fait rien

    channel = bot.get_channel(logsChannelId)
    if not channel:
        return

    # Créer un embed pour l'erreur
    embed = discord.Embed(
        title="⚠️ Erreur Détectée",
        description="Une erreur s'est produite lors de l'exécution du bot",
        color=discord.Color.red(),
        timestamp=datetime.now(),
    )

    # Ajouter les détails de l'erreur
    errorDetails = "".join(traceback.format_exception(type(error), error, error.__traceback__))
    if len(errorDetails) > 1024:  # Discord limite la taille des fields
        errorDetails = errorDetails[:1021] + "..."

    embed.add_field(name="Type d'erreur", value=type(error).__name__, inline=False)
    # embed.add_field(name="Message d'erreur", value=str(error), inline=False)
    errorDetails = errorDetails[-1000:] if len(errorDetails) > 1000 else errorDetails
    embed.add_field(name="Traceback", value=f"```python\n{errorDetails}```", inline=False)

    # Ajouter le contexte si disponible
    if ctx:
        embed.add_field(
            name="Contexte",
            value=f"Commande: {ctx.command}\nAuteur: {ctx.author}\nCanal: {ctx.channel}\nMessage: {ctx.message.content}",
            inline=False,
        )

    await channel.send(embed=embed)


@bot.event
async def on_error(event):
    """Capture les erreurs d'événements"""
    error = traceback.format_exc()
    await log_error(Exception(f"Erreur dans l'événement {event}:\n{error}"))


@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError):
    """Capture les erreurs de commandes"""
    await log_error(error, ctx)


@bot.event
async def on_invite_create(invite: discord.Invite):
    """
    Événement appelé lorsque le bot détecte la création d'une nouvelle invitation.
    Envoie un message dans le canal des logs avec les informations sur l'invitation.
    Met à jour la liste des invitations du serveur.
    """
    logsChannelId = database.get("logs_channel_id")
    if not logsChannelId:
        return

    logsChannel = bot.get_channel(logsChannelId)
    if logsChannel:
        embed = discord.Embed(title="Nouvelle Invitation Créée", color=discord.Color.blue(), timestamp=datetime.now())
        embed.add_field(name="Créée par", value=invite.inviter.mention, inline=True)
        embed.add_field(name="Code", value=invite.code, inline=True)
        embed.add_field(name="Channel", value=invite.channel.mention, inline=True)
        if invite.max_uses:
            embed.add_field(name="Utilisations max", value=invite.max_uses, inline=True)
        if invite.expires_at:
            embed.add_field(name="Expire le", value=invite.expires_at.strftime("%d/%m/%Y à %H:%M"), inline=True)
        embed.set_footer(text=f"ID: {invite.inviter.id}")
        await logsChannel.send(embed=embed)
    invitesBefore[invite.guild.id] = await invite.guild.invites()
    invitesBefore[invite.guild.id] = {inv.code: inv for inv in invitesBefore[invite.guild.id]}


@bot.event
async def on_message_delete(message: discord.Message):
    """
    Événement appelé lorsque le bot détecte la suppression d'un message.

    Envoie un message dans le canal des logs avec les informations sur le message supprimé.

    Si le canal des logs n'est pas configuré, cet événement ne fait rien.

    Si le message a été envoyé par un bot, cet événement ne fait rien.
    """
    logsChannelId = database.get("logs_channel_id")
    if not logsChannelId:
        return

    # Ignorer les messages des bots
    if message.author.bot:
        return

    logsChannel = bot.get_channel(logsChannelId)
    if logsChannel:
        embed = discord.Embed(
            title="Message Supprimé",
            description=f"Un message a été supprimé dans {message.channel.mention}",
            color=discord.Color.red(),
            timestamp=datetime.now(),
        )
        embed.add_field(name="Auteur", value=message.author.mention, inline=False)
        embed.add_field(name="Contenu", value=message.content or "Contenu non disponible", inline=False)
        embed.set_footer(text=f"ID: {message.author.id}")
        await logsChannel.send(embed=embed)


@bot.event
async def on_message_edit(before: discord.Message, after: discord.Message):
    """Événement appelé lorsque le bot détecte la modification d'un message.

    Envoie un message dans le canal des logs avec les informations sur le message modifié.

    Si le canal des logs n'est pas configuré, cet événement ne fait rien.

    Si le message a été envoyé par un bot, cet événement ne fait rien.

    Si le contenu n'a pas changé (par exemple, uniquement un embed ajouté), cet événement ne fait rien.

    """

    logsChannelId = database.get("logs_channel_id")
    if not logsChannelId:
        return

    # Ignorer les messages des bots
    if before.author.bot:
        return

    # Ignorer si le contenu n'a pas changé (par exemple, uniquement un embed ajouté)
    if before.content == after.content:
        return

    logsChannel = bot.get_channel(logsChannelId)
    if logsChannel:
        embed = discord.Embed(
            title="Message Modifié",
            description=f"Un message a été modifié dans {before.channel.mention}",
            color=discord.Color.blue(),
            timestamp=datetime.now(),
        )
        embed.add_field(name="Auteur", value=before.author.mention, inline=False)
        embed.add_field(name="Avant", value=before.content or "Contenu non disponible", inline=False)
        embed.add_field(name="Après", value=after.content or "Contenu non disponible", inline=False)
        embed.add_field(name="Lien", value=f"[Aller au message]({after.jump_url})", inline=False)
        embed.set_footer(text=f"ID: {before.author.id}")
        await logsChannel.send(embed=embed)


@bot.event
async def on_member_join(member: discord.Member):
    """Événement appelé lorsque le bot détecte l'arrivée d'un nouveau membre.

    Ajoute le rôle de newbie au membre.
    Récupère les invitations du serveur.
    Met à jour la liste des invitations.
    Crée un message de bienvenue avec les informations sur l'invitation si trouvée.
    Envoie le message de bienvenue dans le canal des logs.
    Si le canal des logs n'est pas configuré, cet événement ne fait rien.
    """
    logsChannelId = database.get("logs_channel_id")
    if not logsChannelId:
        return

    await member.add_roles(member.guild.get_role(database.get("newbie_role_id")))

    try:
        await hc.refresh_invites_message(member.guild, database)
    except Exception as e:
        await log.send_log_embed(
            "Une erreur s'est produite lors de la mise à jour des invitations", dl.LogLevels.ERROR, e
        )

    await bot.change_presence(
        activity=discord.Activity(
            name=f"{len(member.guild.members)} gens (trop) cools !",
            type=discord.ActivityType.watching,
        )
    )

    logsChannel = bot.get_channel(logsChannelId)
    if logsChannel:
        # Récupérer les invitations après l'arrivée du membre
        invitesAfter = await member.guild.invites()
        invitesAfter = {inv.code: inv for inv in invitesAfter}

        # Trouver quelle invitation a été utilisée
        usedInvite = None
        for inviteAfterCode, inviteAfter in invitesAfter.items():
            if (
                inviteAfterCode in invitesBefore[member.guild.id]
                and inviteAfter.uses > invitesBefore[member.guild.id][inviteAfterCode].uses
            ):
                usedInvite = inviteAfter
                break

        # Mettre à jour la liste des invitations
        invitesBefore[member.guild.id] = await member.guild.invites()
        invitesBefore[member.guild.id] = {inv.code: inv for inv in invitesBefore[member.guild.id]}

        # Créer l'embed de base pour le nouveau membre
        embed = discord.Embed(
            title="Nouveau Membre",
            description=f"{member.mention} a rejoint le serveur!",
            color=discord.Color.green(),
            timestamp=datetime.now(),
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed.add_field(name="Compte créé le", value=member.created_at.strftime("%d/%m/%Y à %H:%M"), inline=False)

        # Ajouter les informations sur l'invitation si trouvée
        if usedInvite:
            embed.add_field(name="Invité par", value=usedInvite.inviter.mention, inline=True)
            embed.add_field(name="Code d'invitation", value=usedInvite.code, inline=True)
            embed.add_field(
                name="Utilisations",
                value=f"{usedInvite.uses}/{usedInvite.max_uses if usedInvite.max_uses else '∞'}",
                inline=True,
            )
        else:
            embed.add_field(name="Invitation", value="Non trouvée", inline=True)

        embed.set_footer(text=f"ID: {member.id}")
        await logsChannel.send(embed=embed)


@bot.event
async def on_member_remove(member: discord.Member):
    """
    Événement appelé lorsque le bot détecte le départ d'un membre.

    Envoie un message dans le canal des logs avec les informations sur le membre parti.
    Si le canal des logs n'est pas configuré, cet événement ne fait rien.
    """
    logsChannelId = database.get("logs_channel_id")
    if not logsChannelId:
        return

    logsChannel = bot.get_channel(logsChannelId)
    if logsChannel:
        embed = discord.Embed(
            title="Membre Parti",
            description=f"{member.display_name} a quitté le serveur",
            color=discord.Color.red(),
            timestamp=datetime.now(),
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed.add_field(name="Avait rejoint le", value=member.joined_at.strftime("%d/%m/%Y à %H:%M"), inline=False)
        embed.set_footer(text=f"ID: {member.id}")
        await logsChannel.send(embed=embed)


@bot.event
async def on_member_update(before: discord.Member, after: discord.Member):
    # Vérifier si le nom a changé
    """
    Événement appelé lorsque le bot détecte un changement de pseudo d'un membre.

    Si le pseudo a changé, le bot envoie un message dans le canal des logs avec les informations sur le membre et son changement de pseudo.
    Si le canal des logs n'est pas configuré, cet événement ne fait rien.
    """
    if before.display_name != after.display_name:
        logsChannelId = database.get("logs_channel_id")
        if not logsChannelId:
            return

        logsChannel = bot.get_channel(logsChannelId)
        if logsChannel:
            embed = discord.Embed(
                title="Changement de Pseudo",
                description="Un membre a changé son pseudo",
                color=discord.Color.blue(),
                timestamp=datetime.now(),
            )
            embed.add_field(name="Membre", value=after.mention, inline=False)
            embed.add_field(name="Ancien pseudo", value=before.display_name, inline=True)
            embed.add_field(name="Nouveau pseudo", value=after.display_name, inline=True)
            embed.set_thumbnail(url=after.avatar.url if after.avatar else after.default_avatar.url)
            embed.set_footer(text=f"ID: {after.id}")
            await logsChannel.send(embed=embed)


@bot.event
async def on_voice_state_update(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
    """
    Événement appelé lorsque le bot détecte un changement d'état vocal d'un membre.

    Si le membre rejoint le channel vocal spécifique pour créer un channel vocal, le bot crée
    un nouveau channel vocal avec le nom du membre et le déplace dedans ce nouveau channel.
    Si le membre quitte un channel vocal créé par le bot et qu'il n'y a plus personne dedans ce
    channel, le bot le supprime.
    """

    if after.channel and after.channel.id == database.get("voc_create_channel_id"):
        createdVocal = await after.channel.category.create_voice_channel(f"{member.display_name}")
        tempVocalsChannelsId = database.get("temp_vocals_channel_id")
        tempVocalsChannelsId.append(createdVocal.id)
        database.modify("temp_vocals_channel_id", tempVocalsChannelsId)
        await member.move_to(createdVocal)
    if (
        before.channel
        and before.channel.id in database.get("temp_vocals_channel_id")
        and len(before.channel.members) == 0
    ):
        tempVocalsChannelsId = database.get("temp_vocals_channel_id")
        tempVocalsChannelsId.remove(before.channel.id)
        database.modify("temp_vocals_channel_id", tempVocalsChannelsId)
        await before.channel.delete()


@bot.event
async def on_interaction(interaction: discord.Interaction):
    """
    Événement appelé lorsque le bot détecte une interaction avec un bouton custom.

    Si l'interaction est une commande de pari, le bot envoie un message pour demander à l'utilisateur de choisir la 1ère équipe, puis la 2e, puis la 3e.
    Si l'interaction est un bouton de pari, le bot enregistre le pari et envoie un message pour demander à l'utilisateur de choisir le nom sous lequel le pari sera affiché.

    Si l'interaction est un bouton d'affichage du nom du pari, le bot enregistre si le pari est anonyme ou non, et envoie un message pour confirmer le pari.
    Si l'interaction est un bouton de placement de pari, le bot place le pari et envoie un message pour afficher le pari.
    """
    if "custom_id" in interaction.data.keys():
        if interaction.data["custom_id"] == "init_spectator":
            if interaction.guild.get_role(database.get("registered_role_id")) not in interaction.user.roles:
                await interaction.user.add_roles(interaction.guild.get_role(database.get("spectator_role_id")))
                await interaction.user.remove_roles(interaction.guild.get_role(database.get("newbie_role_id")))
                await interaction.response.send_message(
                    ":popcorn: Prepare your popcorns, you are now a spectator of the tournament !", ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    f":warning: {interaction.user.mention} :warning:\n\nYou are already registered, if you want to modify your registration, please contact an admin.",
                    ephemeral=True,
                )
        elif interaction.data["custom_id"] == "init_player":
            if interaction.guild.get_role(database.get("registered_role_id")) in interaction.user.roles:
                await interaction.response.send_message(
                    f":warning: {interaction.user.mention} :warning:\n\nYou are already registered, if you want to modify your registration, please contact an admin.",
                    ephemeral=True,
                )
            else:
                await interaction.response.send_modal(md.RegisterModal())
        elif "bet1" in interaction.data["custom_id"]:
            bet1 = interaction.data["custom_id"].split(".")[1]
            buttons = []
            for component in interaction.message.components:
                buttons.extend([child for child in component.children])
            view = discord.ui.View()
            for button in buttons:
                if button.label == bet1:
                    view.add_item(
                        discord.ui.Button(label=button.label + " (1st)", style=discord.ButtonStyle.green, disabled=True)
                    )
                else:
                    view.add_item(
                        discord.ui.Button(
                            label=button.label,
                            custom_id=f"bet2.{bet1}.{button.label}",
                            style=button.style,
                            disabled=True if button.style == discord.ButtonStyle.green else False,
                        )
                    )
            await interaction.response.edit_message(content="Which team will finish 2nd of this Hellcup ?", view=view)
        elif "bet2" in interaction.data["custom_id"]:
            bet1 = interaction.data["custom_id"].split(".")[1]
            bet2 = interaction.data["custom_id"].split(".")[2]
            buttons = []
            for component in interaction.message.components:
                buttons.extend([child for child in component.children])
            view = discord.ui.View()
            for button in buttons:
                if button.label == bet2:
                    view.add_item(
                        discord.ui.Button(label=button.label + " (2nd)", style=discord.ButtonStyle.green, disabled=True)
                    )
                else:
                    view.add_item(
                        discord.ui.Button(
                            label=button.label,
                            custom_id=f"bet3.{bet1}.{bet2}.{button.label}",
                            style=button.style,
                            disabled=True if button.style == discord.ButtonStyle.green else False,
                        )
                    )
            await interaction.response.edit_message(content="Which team will finish 3rd of this Hellcup ?", view=view)
        elif "bet3" in interaction.data["custom_id"]:
            bet1 = interaction.data["custom_id"].split(".")[1]
            bet2 = interaction.data["custom_id"].split(".")[2]
            bet3 = interaction.data["custom_id"].split(".")[3]
            betsMessage = f"Here's the recap of your bets !\n\n- :first_place: : {bet1}\n- :second_place: : {bet2}\n- :third_place: : {bet3}\n\nUnder what name do you want the bet to be displayed ?\n"
            view = discord.ui.View()
            view.add_item(
                discord.ui.Button(
                    label=interaction.user.display_name,
                    custom_id=f"anonymous.no.{bet1}.{bet2}.{bet3}",
                    style=discord.ButtonStyle.primary,
                )
            )
            view.add_item(
                discord.ui.Button(
                    label="Anonymous",
                    custom_id=f"anonymous.yes.{bet1}.{bet2}.{bet3}",
                    style=discord.ButtonStyle.primary,
                )
            )
            await interaction.response.edit_message(content=betsMessage, view=view)
        elif "anonymous" in interaction.data["custom_id"]:
            bet1 = interaction.data["custom_id"].split(".")[2]
            bet2 = interaction.data["custom_id"].split(".")[3]
            bet3 = interaction.data["custom_id"].split(".")[4]
            anonymous = True if interaction.data["custom_id"].split(".")[1] == "yes" else False
            await interaction.response.edit_message(
                content="Perfect !\n\nThank you for your bet, stay tuned to get the results !", view=None
            )
            messageToSend = f"{'Anonymous' if anonymous else interaction.user.mention} has placed a bet : \n\n- :first_place: : {bet1}\n- :second_place: : {bet2}\n- :third_place: : {bet3}\n\nPlace your own bet using the `/bet` command !"
            await hc.place_bet(interaction.user.id, bet1, bet2, bet3, anonymous, interaction.user.display_name)
            await interaction.guild.get_channel(database.get("bets_channel_id")).send(messageToSend)


@bot.tree.command(name="team", description="Create your team !")
async def team(interaction: discord.Interaction):
    """
    Create your team !

    Si vous êtes deja inscrit en tant que joueur, vous ne pouvez pas utiliser cette commande.
    Si vous êtes inscrit en tant que spectateur, vous ne pouvez pas utiliser cette commande, si vous voulez jouer, rdv dans le channel {interaction.guild.get_channel(db.get('rules_channel_id')).mention} !
    """
    if interaction.user in interaction.guild.get_role(database.get("player_role_id")).members:
        await interaction.response.send_message(
            f":warning: {interaction.user.mention} :warning:\n\nYou already have a team !", ephemeral=True
        )
    elif interaction.user in interaction.guild.get_role(database.get("spectator_role_id")).members:
        await interaction.response.send_message(
            f":warning: {interaction.user.mention} :warning:\n\nYou are registered as a spectator, if you want to play, go to the channel {interaction.guild.get_channel(database.get('rules_channel_id')).mention} !",
            ephemeral=True,
        )
    else:
        # view = discord.ui.View()
        # view.add_item(discord.ui.UserSelect(custom_id="team_select", max_values=1, placeholder="Who will be your team mate ?", min_values=1))
        # await interaction.response.send_message("Indicate your team mate", view=view, ephemeral=True)
        layoutView = lv.TeamInscriptionLayoutView(interaction, log, database)
        await interaction.response.send_message(view=layoutView, ephemeral=True)
    return


@bot.tree.command(name="bet", description="Bet on the Hellcup's podium")
async def bet(interaction: discord.Interaction):
    """
    Pari sur le podium de la Hellcup.

    Si vous avez déjà parié pour cette édition, vous ne pouvez pas utiliser cette commande.
    Sinon, vous pouvez choisir l'une des équipes qualifiées pour cette édition en cliquant sur le bouton correspondant.
    """
    await interaction.response.defer(ephemeral=True)
    if interaction.user.id in await hc.get_bets_discord_ids():
        await interaction.followup.send(":x: You have already bet for this edition.", ephemeral=True)
    else:
        teamsList = await hc.get_qualified_teams()
        view = discord.ui.View()
        for teamTemp in teamsList:
            view.add_item(
                discord.ui.Button(label=teamTemp, custom_id=f"bet1.{teamTemp}", style=discord.ButtonStyle.primary)
            )
        await interaction.followup.send("Which team will win this Hellcup ?", view=view, ephemeral=True)


@bot.event
async def on_message(message: discord.Message):
    # Ignorer les messages du bot
    """
    Ignorer les messages du bot.

    Si l'utilisateur a la permission d'administrateur, il peut utiliser certaines commandes spéciales.
    La commande $sync synchronise les commandes du bot avec le serveur Discord.
    La commande $send <message> envoie le message <message> sur le channel actuel.
    La commande $stop_inscription désactive le bouton d'inscription.
    La commande $start_inscription réactive le bouton d'inscription.
    La commande $add_invite <link> <name> ajoute l'invitation <link> au dictionnaire des invitations avec le nom <name>.
    La commande $refresh_invites_message met à jour le message des invitations.
    La commande $test vérifie si le serveur a plus de 48 catégories de salons d'équipes et créé une nouvelle si c'est le cas.
    La commande $initmessagebienvenue envoie un message de bienvenue sur le serveur avec un embed et deux boutons pour s'inscrire en tant que joueur ou spectateur.

    """

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
                syncMessage = await message.channel.send("🔄 Synchronisation des commandes en cours...")
                syncRet = await bot.tree.sync()
                await syncMessage.edit(
                    content="✅ Commandes synchronisées avec succès! " + str(syncRet), delete_after=5
                )
            except Exception as e:
                await syncMessage.edit(content=f"❌ Erreur lors de la synchronisation: {str(e)}")

        elif message.content.startswith("$send"):
            try:
                messageContent = message.content.split("$send ", 1)[1]
                await message.channel.send(messageContent)
            except Exception as e:
                await log.send_log_embed("Impossible d'envoyer le message", dl.LogLevels.ERROR, e)
            await message.delete()

        elif message.content == "$stop_inscription":
            messageToModify = await message.guild.get_channel(database.get("rules_channel_id")).fetch_message(
                database.get("signup_message_id")
            )
            view = discord.ui.View(timeout=None)
            view.add_item(
                discord.ui.Button(
                    label=messageToModify.components[0].children[0].label,
                    custom_id=messageToModify.components[0].children[0].custom_id,
                    style=discord.ButtonStyle.secondary,
                    disabled=True,
                )
            )
            view.add_item(
                discord.ui.Button(
                    label=messageToModify.components[0].children[1].label,
                    custom_id=messageToModify.components[0].children[1].custom_id,
                    style=messageToModify.components[0].children[1].style,
                )
            )
            await messageToModify.edit(content=messageToModify.content, embed=messageToModify.embeds[0], view=view)

        elif message.content == "$start_inscription":
            messageToModify = await message.guild.get_channel(database.get("rules_channel_id")).fetch_message(
                database.get("signup_message_id")
            )
            view = discord.ui.View(timeout=None)
            view.add_item(
                discord.ui.Button(
                    label=messageToModify.components[0].children[0].label,
                    custom_id=messageToModify.components[0].children[0].custom_id,
                    style=discord.ButtonStyle.primary,
                    disabled=False,
                )
            )
            view.add_item(
                discord.ui.Button(
                    label=messageToModify.components[0].children[1].label,
                    custom_id=messageToModify.components[0].children[1].custom_id,
                    style=messageToModify.components[0].children[1].style,
                )
            )
            await messageToModify.edit(content=messageToModify.content, embed=messageToModify.embeds[0], view=view)

        elif message.content.startswith("$add_invite"):
            _, link, name = message.content.split(" ", 2)
            invitDict = database.get("invit_to_check")
            invitDict[link.split("/")[-1]] = name
            database.modify("invit_to_check", invitDict)

        elif message.content == "$refresh_invites_message":
            await hc.refresh_invites_message(message.guild, database)

        elif message.content == "$test":
            category = message.guild.get_channel(database.get("team_text_channels_category_id"))
            print(category.position)
            print(len(category.channels))
            if len(category.channels) > 48:
                count = sum([1 for c in category.guild.categories if c.name.lower().startswith("salons d'équipes")])
                newCategory = await message.guild.create_category_channel(f"Salons d'équipes {count + 1}")
                database.modify("team_text_channels_category_id", newCategory.id)
            else:
                print(category.name)

        elif message.content.startswith("$initmessagebienvenue"):
            view = discord.ui.View(timeout=None)
            player = discord.ui.Button(style=discord.ButtonStyle.primary, label="Player !", custom_id="init_player")
            spectator = discord.ui.Button(
                style=discord.ButtonStyle.primary, label="Spectator !", custom_id="init_spectator"
            )
            view.add_item(player)
            view.add_item(spectator)
            e = discord.Embed(title="Welcome on the server ! :wave:", color=discord.Color.green())
            e.add_field(
                name="What are you doing on the server ?",
                value='If you are here to play, click on the "Player !" button, if you are here to spectate the tournament, click on the "Spectator !" button.',
                inline=False,
            )
            e.set_footer(text="©HellBot")
            await message.guild.get_channel(database.get("rules_channel_id")).send(embed=e, view=view)
            database.modify("signup_message_id", message.id)


# @bot.command(name='hello')
# async def hello(ctx):
#     """Répond avec un message de salutation"""
#     await ctx.send(f'👋 Bonjour {ctx.author.name}!')


@bot.command(name="ping")
async def ping(ctx):
    """Vérifie la latence du bot"""
    await ctx.send(f"Pong! Latence: {round(bot.latency * 1000)}ms")


# Lancer le bot
if __name__ == "__main__":
    bot.run(TOKEN, log_handler=None)
