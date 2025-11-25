import platform
from datetime import datetime
from enum import Enum
from typing import Optional

import discord


class LogLevels(Enum):
    DEBUG = discord.Color.blue()
    INFO = discord.Color.yellow()
    WARNING = discord.Color.orange()
    ERROR = discord.Color.red()


class DiscordLog:
    def __init__(self, logChannelId: int):
        """
        Initialize a DiscordLog object.

        Args:
            logChannelId (int): The ID of the channel to send logs to
        """
        self.logChannelId = logChannelId
        self.guild = None

    def add_guild(self, guild: discord.Guild):
        """
        Set the guild for the DiscordLog instance.

        Args:
            guild (discord.Guild): The Discord guild to associate with the log instance.
        """

        self.guild = guild

    async def send_log_embed(
        self, logMessage: str, logLevel: LogLevels = LogLevels.INFO, extraInfo: Optional[str] = None
    ):
        """
        Send a log message as an embed to the super-logs channel.

        Args:
            guild (discord.Guild): The guild to send the log to
            title (str): The title of the embed (e.g. "Message Deleted", "Error Detected")
            description (str): The description/content of the log message
            color (int, optional): The color of the embed. Defaults to None.
        """
        logMessage, extraInfo = str(logMessage), str(extraInfo) if extraInfo else None
        embed = discord.Embed(
            title=f"Evenement {logLevel.name} [{platform.system()}]",
            description=logMessage[-900:] if extraInfo else logMessage[-1800:],
            color=logLevel.value or discord.Color.blue(),
            timestamp=datetime.now(),
        )
        if extraInfo is not None:
            embed.add_field(name="Extra Info", value=extraInfo[-900:], inline=False)
        await self.guild.get_channel(self.logChannelId).send(embed=embed)
