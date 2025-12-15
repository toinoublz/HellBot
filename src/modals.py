from datetime import datetime

import discord
from discord import ui
from easyDB import DB

import hellcup as hc

db = DB("hellbot")


class RegisterModal(ui.Modal):
    def __init__(self):
        """
        Initializes the RegisterModal instance.

        It sets the title of the modal to "Inscription" and adds two text inputs to the modal.
        The first input is labeled "Surname" and is used to enter the user's surname.
        The second input is labeled "Geoguessr ID" and is used to enter the user's Geoguessr ID.
        """
        super().__init__(title="Inscription")

        surname = ui.TextInput(
            label="Username",
            placeholder="Your username",
            style=discord.TextStyle.short,
            min_length=2,
            max_length=32,
        )
        geoguessrLink = ui.TextInput(
            label="Geoguessr ID",
            placeholder="https://www.geoguessr.com/user/x_x_x_x_x_x_x_x_x_x",
            style=discord.TextStyle.short,
        )

        self.add_item(surname)
        self.add_item(geoguessrLink)

        return

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        surname = interaction.data["components"][0]["components"][0]["value"]
        geoguessrLink = interaction.data["components"][1]["components"][0]["value"]
        member = {
            "discordId": str(interaction.user.id),
            "surname": surname,
            "geoguessrId": (
                geoguessrLink if "www.geoguessr.com/user" not in geoguessrLink else geoguessrLink.split("/")[-1]
            ),
        }
        if not await hc.is_geoguessr_id_correct(member["geoguessrId"]):
            await interaction.followup.send(
                f":warning: {interaction.user.mention} :warning:\n\nThe link to your Geoguessr profile seems to be incorrect. To find it, go to https://www.geoguessr.com/me/profile and click on your profile picture) If you think this is a mistake, please contact an admin!",
                ephemeral=True,
            )
        else:
            await hc.inscription(member)
            await interaction.user.add_roles(interaction.guild.get_role(db.get("registered_role_id")))
            await interaction.user.remove_roles(interaction.guild.get_role(db.get("spectator_role_id")))
            await interaction.user.remove_roles(interaction.guild.get_role(db.get("newbie_role_id")))
            await interaction.followup.send(
                f":tada: Welcome on board {interaction.user.mention} ! :tada:\n\nYou are now registered as a player, please create your team with the `/team` command in any text channel.",
                ephemeral=True,
            )
            embed = discord.Embed(
                title="Nouvelle inscription",
                description=f"{interaction.user.mention} is now registered as a player : **{member['surname']}**!",
                color=discord.Color.green(),
                timestamp=datetime.now(),
            )
            embed.set_thumbnail(
                url=interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url
            )
            embed.add_field(name="ID Geoguessr", value=member["geoguessrId"], inline=True)
            embed.add_field(name="Inscription date", value=datetime.now().strftime("%d/%m/%Y à %H:%M"), inline=True)
            await interaction.guild.get_channel(db.get("registration_channel_id")).send(embed=embed)
