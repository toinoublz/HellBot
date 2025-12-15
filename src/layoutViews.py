import traceback

import discord
from easyDB import DB

import discord_logs as dl
import hellcup as hc

MODE_EMOJIS = {"Move": "🚶‍♂️", "No move": "📍", "NMPZ": "🖼️"}


class TeamInscriptionLayoutView(discord.ui.LayoutView):
    def __init__(self, interaction: discord.Interaction, log: dl.DiscordLog, database: DB):
        super().__init__(timeout=None)
        self.interaction = interaction
        self.firstPlayer = interaction.user
        self.secondPlayer: discord.Member = None
        self.log = log
        self.database = database

        self.firstContainer = discord.ui.Container(accent_color=discord.Color.green())
        self.secondContainer = discord.ui.Container(accent_color=discord.Color.red())
        self.thirdContainer = discord.ui.Container(accent_color=discord.Color.blurple())
        self.fourthContainer = discord.ui.Container(accent_color=discord.Color.orange())

        self.firstMode = None
        self.secondMode = None
        self.thirdMode = None

        self.teamMateSelected = False
        self.firstModeSelected = False
        self.secondModeSelected = False
        self.thirdModeSelected = False

        moveSelectOption = discord.SelectOption(label="Move", emoji=MODE_EMOJIS["Move"])
        noMoveSelectOption = discord.SelectOption(label="No move", emoji=MODE_EMOJIS["No move"])
        nmpzSelectOption = discord.SelectOption(label="NMPZ", emoji=MODE_EMOJIS["NMPZ"])

        self.indexList = ["Move", "No move", "NMPZ"]
        self.allSelectOptions = [moveSelectOption.copy(), noMoveSelectOption.copy(), nmpzSelectOption.copy()]

        self.firstSelectOptions = [moveSelectOption.copy(), noMoveSelectOption.copy(), nmpzSelectOption.copy()]
        self.secondSelectOptions = [moveSelectOption.copy(), noMoveSelectOption.copy(), nmpzSelectOption.copy()]
        self.thirdSelectOptions = [moveSelectOption.copy(), noMoveSelectOption.copy(), nmpzSelectOption.copy()]

        async def update():
            self.firstSelect.options = self.firstSelectOptions
            self.secondSelect.options = self.secondSelectOptions
            self.thirdSelect.options = self.thirdSelectOptions
            await self.interaction.edit_original_response(view=self)

        def check_button():
            if all([self.teamMateSelected, self.firstModeSelected, self.secondModeSelected, self.thirdModeSelected]):
                self.sendButton.disabled = False

        async def team_mate_select_callback(interaction: discord.Interaction):
            await interaction.response.defer(ephemeral=True)
            self.secondPlayer = interaction.guild.get_member(int(interaction.data["values"][0]))
            if self.firstPlayer.id == self.secondPlayer.id:
                await interaction.response.send_message(
                    f":warning: {self.firstPlayer.mention} :warning:\n\nYou can't make a team with yourself !",
                    ephemeral=True,
                )
                return
            self.teamMateSelected = True
            self.firstSelect.disabled = False
            self.secondSelect.disabled = False
            self.thirdSelect.disabled = False
            check_button()
            await update()

        async def first_select_callback(interaction: discord.Interaction):
            await interaction.response.defer(ephemeral=True)
            self.firstMode = interaction.data["values"][0]
            self.firstSelectOptions[self.indexList.index(self.firstMode)].default = True
            self.firstSelect.options = self.firstSelectOptions
            self.firstModeSelected = True
            check_button()
            await update()

        async def second_select_callback(interaction: discord.Interaction):
            await interaction.response.defer(ephemeral=True)
            self.secondMode = interaction.data["values"][0]
            self.secondSelectOptions[self.indexList.index(self.secondMode)].default = True
            self.secondSelect.options = self.secondSelectOptions
            self.secondModeSelected = True
            check_button()
            await update()

        async def third_select_callback(interaction: discord.Interaction):
            await interaction.response.defer(ephemeral=True)
            self.thirdMode = interaction.data["values"][0]
            self.thirdSelectOptions[self.indexList.index(self.thirdMode)].default = True
            self.thirdSelect.options = self.thirdSelectOptions
            self.thirdModeSelected = True
            check_button()
            await update()

        async def close_inscription(interaction: discord.Interaction):
            await interaction.response.defer(ephemeral=True)
            try:
                if self.secondPlayer in interaction.guild.get_role(self.database.get("player_role_id")).members:
                    await interaction.response.send_message(f":warning: {self.firstPlayer.mention} :warning:\n\nThe selected player already has a team, if you think this is an error, please see with an admin.", ephemeral=True)
                elif self.secondPlayer in interaction.guild.get_role(self.database.get("spectator_role_id")).members:
                    await interaction.response.send_message(f":warning: {self.firstPlayer.mention} :warning:\n\nThe selected player is registered as a spectator, to remedy this, tell him to register as a player in the channel {interaction.guild.get_channel(self.database.get('rules_channel_id')).mention} !", ephemeral=True)
                elif self.secondPlayer not in interaction.guild.get_role(self.database.get("registered_role_id")).members:
                    await interaction.response.send_message(f":warning: {self.firstPlayer.mention} :warning:\n\nThe selected player is not yet registered, to remedy this, tell him to register as a player in the channel {interaction.guild.get_channel(self.database.get('rules_channel_id')).mention} !", ephemeral=True)
                teamData = await hc.create_team(
                    self.firstPlayer, self.secondPlayer, self.firstMode, self.secondMode, self.thirdMode
                )
                await self.firstPlayer.add_roles(interaction.guild.get_role(self.database.get("player_role_id")))
                await self.secondPlayer.add_roles(interaction.guild.get_role(self.database.get("player_role_id")))
                teamRole = await interaction.guild.create_role(name=teamData["team_name"])
                await self.firstPlayer.add_roles(teamRole)
                await self.secondPlayer.add_roles(teamRole)
                category = interaction.guild.get_channel(self.database.get("team_text_channels_category_id"))
                adminRole = interaction.guild.get_role(self.database.get("admin_role_id"))
                varRole = interaction.guild.get_role(self.database.get("var_role_id"))

                overwritesText = {
                    interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
                    teamRole: discord.PermissionOverwrite(view_channel=True),
                    adminRole: discord.PermissionOverwrite(view_channel=True),
                }

                overwritesVocal = {
                    interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
                    teamRole: discord.PermissionOverwrite(view_channel=True),
                    varRole: discord.PermissionOverwrite(view_channel=True),
                }
                if len(category.channels) == 50:
                    count = sum(1 for c in category.guild.categories if c.name.lower().startswith("salons d'équipes"))
                    newCategory = await interaction.guild.create_category_channel(f"Salons d'équipes {count + 1}")
                    self.database.modify("team_text_channels_category_id", newCategory.id)
                    category = newCategory
                await category.create_voice_channel(f"team-{teamRole.name}", overwrites=overwritesVocal)
                channel = await category.create_text_channel(f"team-{teamRole.name}", overwrites=overwritesText)
                try:
                    await interaction.followup.send(f":tada: {self.firstPlayer.mention} :tada:\n\nYou are now in a team with {self.secondPlayer.mention} ! Go to the channel {channel.mention} to exchange with your mate !", ephemeral=True)
                except Exception as e:
                    await self.log.send_log_embed(f"Impossible d'envoyer la réponse de l'interaction {self.firstPlayer.name} ({self.firstPlayer.id}) et {self.secondPlayer.name} ({self.secondPlayer.id})", dl.LogLevels.ERROR, e)
                try:
                    await self.firstPlayer.send(f":tada: {self.firstPlayer.mention} :tada:\n\nYou are now in a team with {self.secondPlayer.mention} ! Go to the channel {channel.mention} to exchange with your mate !")
                except Exception as e:
                    await self.log.send_log_embed(f"Impossible d'envoyer le message d'équipe à {self.firstPlayer.name} ({self.firstPlayer.id}) et {self.secondPlayer.name} ({self.secondPlayer.id})", dl.LogLevels.ERROR, e)
                try:
                    await self.secondPlayer.send(f":tada: {self.secondPlayer.mention} :tada:\n\nYou are now in a team with {self.firstPlayer.mention} ! Go to the channel {channel.mention} to exchange with your mate ! If this is an error, please contact an admin.")
                except Exception as e:
                    await self.log.send_log_embed(f"Impossible d'envoyer le message d'équipe à {self.secondPlayer.name} ({self.secondPlayer.id}) et {self.firstPlayer.name} ({self.firstPlayer.id})", dl.LogLevels.ERROR, e)

                teamLayoutview = await TeamLayoutView.create(teamData)

                await interaction.guild.get_channel(self.database.get("registration_channel_id")).send(view=teamLayoutview)
                await interaction.guild.get_channel(self.database.get("new_team_channel_id")).send(view=teamLayoutview)

                await interaction.channel.send(view=teamLayoutview)
            except Exception:
                traceback.print_exc()

        self.teamMateSelect = discord.ui.UserSelect(
            max_values=1, placeholder="Who will be your team mate ?", min_values=1
        )
        self.teamMateSelect.callback = team_mate_select_callback

        self.firstSelect = discord.ui.Select(
            options=self.allSelectOptions,
            placeholder="What is your favorite mode ?",
            min_values=1,
            max_values=1,
            disabled=True,
        )
        self.firstSelect.callback = first_select_callback

        self.secondSelect = discord.ui.Select(
            options=self.allSelectOptions,
            placeholder="What is your second favorite mode ?",
            min_values=1,
            max_values=1,
            disabled=True,
        )
        self.secondSelect.callback = second_select_callback

        self.thirdSelect = discord.ui.Select(
            options=self.allSelectOptions,
            placeholder="What is your least favorite mode ?",
            min_values=1,
            max_values=1,
            disabled=True,
        )
        self.thirdSelect.callback = third_select_callback

        self.firstContainer.add_item(discord.ui.TextDisplay("Who will be your team mate ?"))
        self.firstContainer.add_item(discord.ui.ActionRow(self.teamMateSelect))
        self.secondContainer.add_item(discord.ui.TextDisplay("What is your favorite mode ?"))
        self.secondContainer.add_item(discord.ui.ActionRow(self.firstSelect))
        self.thirdContainer.add_item(discord.ui.TextDisplay("What is your second favorite mode ?"))
        self.thirdContainer.add_item(discord.ui.ActionRow(self.secondSelect))
        self.fourthContainer.add_item(discord.ui.TextDisplay("What is your least favorite mode ?"))
        self.fourthContainer.add_item(discord.ui.ActionRow(self.thirdSelect))

        self.sendButton = discord.ui.Button(label="Send", style=discord.ButtonStyle.primary, disabled=True)
        self.sendButton.callback = close_inscription

        self.add_item(self.firstContainer)
        self.add_item(self.secondContainer)
        self.add_item(self.thirdContainer)
        self.add_item(self.fourthContainer)
        self.add_item(discord.ui.ActionRow(self.sendButton))

        # self.add_item(discord.ui.TextDisplay("Who will be your team mate ?"))
        # self.add_item(discord.ui.ActionRow(self.teamMateSelect))
        # self.add_item(discord.ui.Separator())
        # self.add_item(discord.ui.TextDisplay("What is your favorite mode ?"))
        # self.add_item(discord.ui.ActionRow(self.firstSelect))
        # self.add_item(discord.ui.Separator())
        # self.add_item(discord.ui.TextDisplay("What is your second favorite mode ?"))
        # self.add_item(discord.ui.ActionRow(self.secondSelect))
        # self.add_item(discord.ui.Separator())
        # self.add_item(discord.ui.TextDisplay("What is your least favorite mode ?"))
        # self.add_item(discord.ui.ActionRow(self.thirdSelect))
        # self.add_item(discord.ui.Separator())
        # self.add_item(discord.ui.ActionRow(self.sendButton))


class PlayerContainer(discord.ui.Container):
    def __init__(self, intraData: dict):
        super().__init__()
        titleTextDisplay = discord.ui.TextDisplay(f"## {intraData['name']}")
        playersData = intraData["playersData"]
        countryTextDisplay = discord.ui.TextDisplay(f"Country : :flag_{playersData['countryCode'].lower()}:")
        eloTextDisplay = discord.ui.TextDisplay(f"Current ELO : {playersData['competitive']['rating']}")
        profileButton = discord.ui.Button(
            label="Geoguessr profile",
            url=f"https://www.geoguessr.com/user/{intraData['geoguessrId']}",
            style=discord.ButtonStyle.link,
        )
        self.add_item(
            discord.ui.Section(
                titleTextDisplay,
                countryTextDisplay,
                eloTextDisplay,
                accessory=discord.ui.Thumbnail(f"https://www.geoguessr.com/images/plain/{playersData['pin']['url']}"),
            )
        )
        self.add_item(discord.ui.ActionRow(profileButton))

    @classmethod
    async def create(cls, geoguessrId: str, name: str):
        """
        Creates a new PlayerContainer instance with the given geoguessrId and name.

        This method first calls `hc.get_player_datas` to retrieve the player's data from their Geoguessr ID.
        It then creates a dictionary containing the player's data and passes it to the PlayerContainer constructor.

        :param geoguessrId: The Geoguessr ID of the player
        :type geoguessrId: str
        :param name: The name of the player
        :type name: str
        :return: A new PlayerContainer instance
        :rtype: PlayerContainer
        """
        playersData = await hc.get_player_datas(geoguessrId)
        intraData = {"geoguessrId": geoguessrId, "name": name, "playersData": playersData}
        return cls(intraData)


class TeamLayoutView(discord.ui.LayoutView):

    def __init__(self, teamData: dict, player1Container: discord.ui.Container, player2Container: discord.ui.Container):
        super().__init__(timeout=None)

        self.player1GeoguessrId = teamData["member1_geoguessrId"]
        self.player1Name = teamData["member1_surname"]
        self.player2GeoguessrId = teamData["member2_geoguessrId"]
        self.player2Name = teamData["member2_surname"]
        self.teamName = teamData["team_name"]
        self.modes = [teamData["firstMode"], teamData["secondMode"], teamData["thirdMode"]]

        self.add_item(discord.ui.TextDisplay("# A new team has just landed !"))
        self.add_item(discord.ui.TextDisplay(self.teamName.replace("_", " & ")))
        self.add_item(discord.ui.Separator())
        self.add_item(
            discord.ui.TextDisplay(
                f"Favorite modes : {' >> '.join([MODE_EMOJIS[mode] + ' ' + mode for mode in self.modes])}"
            )
        )
        self.add_item(discord.ui.Separator())
        self.add_item(player1Container)
        self.add_item(discord.ui.Separator())
        self.add_item(player2Container)

    @classmethod
    async def create(cls, teamData: dict):
        """
        Creates a new TeamLayoutView instance with the given teamData.

        This method first creates two PlayerContainer instances with the given member1 and member2 data.
        It then creates a new TeamLayoutView instance with the given teamData and the two PlayerContainer instances.

        :param teamData: A dictionary containing the team's data
        :type teamData: dict
        :return: A new TeamLayoutView instance
        :rtype: TeamLayoutView
        """
        player1Container = await PlayerContainer.create(teamData["member1_geoguessrId"], teamData["member1_surname"])
        player2Container = await PlayerContainer.create(teamData["member2_geoguessrId"], teamData["member2_surname"])
        return cls(teamData, player1Container, player2Container)
