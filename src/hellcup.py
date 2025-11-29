import aiohttp
import discord
from easyDB import DB

import gspread_utilities as gu


async def is_geoguessr_id_correct(geoguessr_id: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://www.geoguessr.com/api/v3/users/{geoguessr_id}/stats") as response:
            if response.ok:
                return True
            else:
                return False


async def inscription(member: dict):
    await gu.gspread_new_registration(member)
    return


async def create_team(
    member1: discord.Member, member2: discord.Member, firstMode: str, secondMode: str, thirdMode: str
) -> dict[str, str]:
    ### Let's find them in the gsheet list of registered players
    return await gu.gspread_new_team(member1, member2, firstMode, secondMode, thirdMode)


async def refresh_invites_message(guild: discord.Guild, db: DB):
    message = await guild.get_channel(db.get("registration_channel_id")).fetch_message(db.get("invit_message_id"))
    invitesToCheck = db.get("invit_to_check")
    guildInvites = await guild.invites()
    invites = {invite.code: invite.uses for invite in guildInvites if invite.code in invitesToCheck.keys()}
    content = "Liste des invitations sauvegardées actuelles :\n- "
    content += "\n- ".join(
        [
            f"{invitesToCheck[key]} ({key}) : {value} utilisation{'' if value == 1 else 's'}"
            for key, value in invites.items()
        ]
    )
    await message.edit(content=content)


async def get_qualified_teams():
    return await gu.get_qualified_teams_names()


async def get_bets_discordIds():
    return await gu.get_bets_discord_ids()


async def place_bet(discordId: int, bet1: str, bet2: str, bet3: str, isAnonymous: bool, discordName: str):
    await gu.place_bet(discordId, bet1, bet2, bet3, isAnonymous, discordName)


async def get_player_datas(geoguessrId: str) -> dict:
    """
    Retrieves data about a player from the GeoGuessr API.

    Args:
        geoguessrId (str): The GeoGuessr ID of the player.

    Returns:
        dict: A dictionary containing the player's data.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://www.geoguessr.com/api/v3/users/{geoguessrId}") as r:
            return await r.json()
