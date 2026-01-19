import aiohttp
import discord

from easyDB import DB
import gspread_utilities as gu

async def is_geoguessr_id_correct(geoguessrId: str):
    """
    Checks if the given Geoguessr ID is correct.

    :param geoguessr_id: The Geoguessr ID to check
    :type geoguessr_id: str
    :return: True if the Geoguessr ID is correct, False otherwise
    :rtype: bool
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://www.geoguessr.com/api/v3/users/{geoguessrId}/stats") as response:
            return response.ok


async def inscription(member: dict):
    """
    Adds a new registration to the Google Sheets document.

    The registration is added to the "Inscrits" worksheet.

    The registration is added with the following information:

    - Discord ID
    - Geoguessr ID
    - Surmame
    - Number of games played (defaults to 0)

    Returns nothing.
    """
    await gu.gspread_new_registration(member)
    return


async def create_team(member1: discord.Member, member2: discord.Member, firstMode: str, secondMode: str, thirdMode: str) -> dict[str, str]:
    ### Let's find them in the gsheet list of registered players
    """
    Creates a new team in the Google Sheets document.

    The team is added to the "Teams" worksheet.

    The team is added with the following information:

    - Discord ID of member 1
    - Geoguessr ID of member 1
    - Discord ID of member 2
    - Geoguessr ID of member 2
    - Surmame of member 1
    - Surmame of member 2
    - Team name (member1 surname + "_" + member2 surname)

    Returns a dictionary containing the surmames of the two members of the team.

    :param member1: The first member of the team
    :type member1: discord.Member
    :param member2: The second member of the team
    :type member2: discord.Member
    :param firstMode: The first mode of the team
    :type firstMode: str
    :param secondMode: The second mode of the team
    :type secondMode: str
    :param thirdMode: The third mode of the team
    :type thirdMode: str
    :return: A dictionary containing the surmames of the two members of the team
    :rtype: dict[str, str]
    """
    return await gu.gspread_new_team(member1, member2, firstMode, secondMode, thirdMode)


async def get_qualified_teams_names_if_id_is_able_to_bet(discordId: int):
    """
    Retrieves the list of qualified teams' names from the Google Sheets document.

    Returns a list containing the names of the qualified teams.

    :rtype: List[str]
    """
    return await gu.get_qualified_teams_names_if_id_is_able_to_bet(discordId)


async def place_bet(discordId: int, bet1: str, bet2: str, bet3: str, isAnonymous: bool, discordName: str):
    """
    Places a bet for the Hellcup.

    Args:
        discordId (int): The Discord ID of the player who is placing the bet.
        bet1 (str): The first choice of the player.
        bet2 (str): The second choice of the player.
        bet3 (str): The third choice of the player.
        isAnonymous (bool): Whether or not the player's name should be shown in the bets spreadsheet.
        discordName (str): The name of the player on Discord.

    Returns:
        None
    """
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
        async with session.get(f"https://www.geoguessr.com/api/v4/ranked-system/progress/{geoguessrId}") as r:
            tempRes = await r.json()
        async with session.get(f"https://www.geoguessr.com/api/v3/users/{geoguessrId}") as r:
            tempRes.update(await r.json())
        return tempRes
