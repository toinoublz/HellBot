import discord
import gspread_asyncio
from google.oauth2.service_account import Credentials


def get_creds():
    # To obtain a service account JSON file, follow these steps:
    # https://gspread.readthedocs.io/en/latest/oauth2.html#for-bots-using-service-account
    """
    Returns a service account credentials object with the necessary scopes
    for gspread_asyncio to work.

    The credentials object is obtained from a JSON file named "creds.json".
    To obtain this file, follow the instructions in the link below:

    https://gspread.readthedocs.io/en/latest/oauth2.html#for-bots-using-service-account

    The scopes used are:

    - https://spreadsheets.google.com/feeds
    - https://www.googleapis.com/auth/spreadsheets
    - https://www.googleapis.com/auth/drive.file
    - https://www.googleapis.com/auth/drive

    These scopes are required for the gspread_asyncio library to work.
    """
    creds = Credentials.from_service_account_file("creds.json")
    scoped = creds.with_scopes(
        [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/drive",
        ]
    )
    return scoped


async def connect_gsheet_api() -> gspread_asyncio.AsyncioGspreadClient:
    """
    Connect to the Google Sheets API using the credentials from the "creds.json" file.

    The scopes used are:

    - https://spreadsheets.google.com/feeds
    - https://www.googleapis.com/auth/spreadsheets
    - https://www.googleapis.com/auth/drive.file
    - https://www.googleapis.com/auth/drive

    These scopes are required for the gspread_asyncio library to work.

    Returns a gspread_asyncio.AsyncioGspreadClient object.
    """
    agcm = gspread_asyncio.AsyncioGspreadClientManager(get_creds)
    clientg = await agcm.authorize()
    return clientg


async def gspread_new_registration(member: dict):
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
    clientg = await connect_gsheet_api()
    spreadsheet = await clientg.open("[ORGA] Hell Cup Inscriptions ")
    worksheet = await spreadsheet.worksheet("Inscrits")
    await worksheet.append_row([member["discordId"], member["geoguessrId"], member["surname"], 0])
    return


async def gspread_new_team(member1: discord.Member, member2: discord.Member):
    """
    Adds a new team to the Google Sheets document.

    The team is added to the "Teams" worksheet.

    The team is added with the following information:

    - Discord ID of member 1
    - GeoGuessr ID of member 1
    - Discord ID of member 2
    - GeoGuessr ID of member 2
    - Surmame of member 1
    - Surmame of member 2
    - Team name (member1 surname + "_" + member2 surname)

    Returns a list containing the surmames of the two members of the team.

    :param member1: The first member of the team
    :type member1: discord.Member
    :param member2: The second member of the team
    :type member2: discord.Member
    :return: A list containing the surmames of the two members of the team
    :rtype: List[str]
    """
    clientg = await connect_gsheet_api()
    spreadsheet = await clientg.open("[ORGA] Hell Cup Inscriptions ")
    worksheet = await spreadsheet.worksheet("Inscrits")
    lines = await worksheet.get_all_records()
    player1Updated = player2Updated = False
    team = {"member1_discordId": str(member1.id), "member2_discordId": str(member2.id)}
    for lineNumber, line in enumerate(lines):
        if str(line["ID Discord"]) == team["member1_discordId"]:
            await worksheet.update_cell(lineNumber + 2, 4, 1)
            team["member1_geoguessrId"] = line["ID GeoGuessr"]
            team["member1_surname"] = line["Pseudo/surnom"]
            player1Updated = True
        if str(line["ID Discord"]) == team["member2_discordId"]:
            await worksheet.update_cell(lineNumber + 2, 4, 1)
            team["member2_geoguessrId"] = line["ID GeoGuessr"]
            team["member2_surname"] = line["Pseudo/surnom"]
            player2Updated = True
        if player1Updated and player2Updated:
            break
    worksheet = await spreadsheet.worksheet("Teams")
    await worksheet.append_row(
        [
            team["member1_discordId"],
            team["member1_geoguessrId"],
            team["member2_discordId"],
            team["member2_geoguessrId"],
            team["member1_surname"],
            team["member2_surname"],
            team["member1_surname"] + "_" + team["member2_surname"],
        ]
    )

    return [team["member1_surname"], team["member2_surname"]]


async def get_qualified_teams_names():
    """
    Récupère la liste des noms des équipes qualifiées pour la Hellcup.

    Returns:
        list: Une liste contenant les noms des équipes qualifiées.
    """
    clientg = await connect_gsheet_api()
    spreadsheet = await clientg.open("[ORGA] Hell Cup Inscriptions ")
    worksheet = await spreadsheet.worksheet("Qualifiés")
    data = await worksheet.get_all_records()
    qualifiedTeamsNames = [team["Nom d'équipe"] for team in data]
    return qualifiedTeamsNames


async def get_bets_discord_ids():
    """
    Récupère la liste des Discord ID des joueurs qui ont déjà parié pour la Hellcup.

    Returns:
        list: Une liste contenant les Discord ID des joueurs qui ont déjà parié.
    """
    clientg = await connect_gsheet_api()
    spreadsheet = await clientg.open("[ORGA] Hell Cup Inscriptions ")
    worksheet = await spreadsheet.worksheet("Bets")
    data = await worksheet.get_all_records()
    betDiscordIds = [int(bet["DiscordId"]) for bet in data]
    return betDiscordIds


async def place_bet(discordId: int, bet1: str, bet2: str, bet3: str, isAnonymous: bool, discordName: str):
    """
    Place a bet for the Hellcup.

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
    clientg = await connect_gsheet_api()
    spreadsheet = await clientg.open("[ORGA] Hell Cup Inscriptions ")
    worksheet = await spreadsheet.worksheet("Bets")
    await worksheet.append_row([str(discordId), bet1, bet2, bet3, isAnonymous, discordName])
