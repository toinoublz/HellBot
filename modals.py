import discord
from discord import ui
import hellcup as hc
import DB
from datetime import datetime

db = DB.DB("hellbot")

class RegisterModal(ui.Modal):
    def __init__(self):
        super().__init__(title="Inscription")

        surname = ui.TextInput(label="Pseudo / Surname", placeholder="Votre pseudo / Your surname", style=discord.TextStyle.short, min_length=2, max_length=32)
        geoguessrLink = ui.TextInput(label="Geoguessr ID", placeholder="https://www.geoguessr.com/user/x_x_x_x_x_x_x_x_x_x", style=discord.TextStyle.short)

        self.add_item(surname)
        self.add_item(geoguessrLink)

        return

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        surname = interaction.data['components'][0]['components'][0]['value']
        geoguessrLink = interaction.data['components'][1]['components'][0]['value']
        member = {"discordId": str(interaction.user.id), "surname": surname, "geoguessrId": geoguessrLink if "www.geoguessr.com/user" not in geoguessrLink else geoguessrLink.split('/')[-1]}
        if not (await hc.is_geoguessr_id_correct(member["geoguessrId"])):
             await interaction.followup.send(f":warning: {interaction.user.mention} :warning:\n\nLe lien de votre profil Geoguessr semble incorrect, pour le trouver, il faut aller sur https://www.geoguessr.com/me/profile et tout en bas vous avez le lien sous la forme https://www.geoguessr.com/user/xxx). Si vous pensez que c'est une erreur, merci de contacter un admin ! / The link to your Geoguessr profile seems to be incorrect. To find it, go to https://www.geoguessr.com/me/profile and at the very bottom you'll find the link in the form https://www.geoguessr.com/user/xxx.) If you think this is a mistake, please contact an admin!", ephemeral=True)
        else:
            await hc.inscription(member)
            await interaction.user.add_roles(interaction.guild.get_role(db.get("registered_role_id")))
            await interaction.user.remove_roles(interaction.guild.get_role(db.get("spectator_role_id")))
            await interaction.user.remove_roles(interaction.guild.get_role(db.get("newbie_role_id")))
            await interaction.followup.send(f":tada: Bienvenue dans le tournoi {interaction.user.mention} ! :tada:\n\nVous êtes bien inscrit en tant que joueur, pensez maintenant à créer votre équipe avec la commande `/team` dans n'importe quel channel textuel. / You are now registered as a player, please create your team with the `/team` command in any text channel.", ephemeral=True)
            embed = discord.Embed(
                title="Nouvelle inscription",
                description=f"{interaction.user.mention} est maintenant inscrit(e) avec le surnom **{member['surname']}**!",
                color=discord.Color.green(),
                timestamp=datetime.now()
            )
            embed.set_thumbnail(url=interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url)
            embed.add_field(name="ID Geoguessr", value=member["geoguessrId"], inline=True)
            embed.add_field(name="Date d'inscription", value=datetime.now().strftime("%d/%m/%Y à %H:%M"), inline=True)
            await interaction.guild.get_channel(db.get("registration_channel_id")).send(embed=embed)

