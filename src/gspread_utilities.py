import asyncio

import discord
import gspread_asyncio
import gspread_formatting
from google.oauth2.service_account import Credentials
from oauth2client.service_account import ServiceAccountCredentials


def get_creds():
    # To obtain a service account JSON file, follow these steps:
    # https://gspread.readthedocs.io/en/latest/oauth2.html#for-bots-using-service-account
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
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive",
    ]

    agcm = gspread_asyncio.AsyncioGspreadClientManager(get_creds)
    clientg = await agcm.authorize()
    return clientg


async def gspread_new_registration(member: dict):
    clientg = await connect_gsheet_api()
    spreadsheet = await clientg.open("[ORGA] Hell Cup Inscriptions ")
    worksheet = await spreadsheet.worksheet("Inscrits")
    await worksheet.append_row([member["discordId"], member["geoguessrId"], member["surname"], 0])
    return


async def gspread_new_team(member1: discord.Member, member2: discord.Member):
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
    clientg = await connect_gsheet_api()
    spreadsheet = await clientg.open("[ORGA] Hell Cup Inscriptions ")
    worksheet = await spreadsheet.worksheet("Qualifiés")
    data = await worksheet.get_all_records()
    qualified_teams_names = [team["Nom d'équipe"] for team in data]
    return qualified_teams_names


async def get_bets_discordIds():
    clientg = await connect_gsheet_api()
    spreadsheet = await clientg.open("[ORGA] Hell Cup Inscriptions ")
    worksheet = await spreadsheet.worksheet("Bets")
    data = await worksheet.get_all_records()
    bet_discordIds = [int(bet["DiscordId"]) for bet in data]
    return bet_discordIds


async def place_bet(discordId: int, bet1: str, bet2: str, bet3: str, isAnonymous: bool, discordName: str):
    clientg = await connect_gsheet_api()
    spreadsheet = await clientg.open("[ORGA] Hell Cup Inscriptions ")
    worksheet = await spreadsheet.worksheet("Bets")
    await worksheet.append_row([str(discordId), bet1, bet2, bet3, isAnonymous, discordName])


if __name__ == "__main__":
    print(asyncio.run(get_qualified_teams_names()))
