import discord
from discord import ui
import hellcup as hc

class RegisterModal(ui.Modal):
    def __init__(self):
        super().__init__(title="Inscription")

        surname = ui.TextInput(label="Surnom", placeholder="Quel surnom voulez-vous utiliser pour le tournoi ?", style=discord.TextStyle.short, min_length=2, max_length=32)
        geoguessrLink = ui.TextInput(label="Lien Geoguessr (allez sur https://www.geoguessr.com/me/profile et tout en bas vous avez le lien sous la forme https://www.geoguessr.com/user/xxx)", placeholder="Lien de votre profil sur Geoguessr", style=discord.TextStyle.short)

        self.add_item(surname)
        self.add_item(geoguessrLink)

        return

    async def on_submit(self, interaction: discord.Interaction):
        surname = interaction.data['components'][0]['components'][0]['value']
        geoguessrLink = interaction.data['components'][1]['components'][0]['value']
        member = {"discordId": interaction.user.id, "surname": surname, "geoguessrId": geoguessrLink if "www.geoguessr.com/user" not in geoguessrLink else geoguessrLink.split('/')[-1]}
        ret = await hc.inscription(member)
        await interaction.response.send_message(f"Bienvenue dans le tournoi {ret['surname']} ! Vous êtes bien inscrit en tant que joueur, pensez maintenant à créer votre équipe avec la commande `/equipe`", ephemeral=True)
