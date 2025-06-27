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
    spreadsheet = await clientg.open("[ORGA] Guess and Give Inscriptions")
    worksheet = await spreadsheet.worksheet("Inscrits")
    await worksheet.append_row(
        [member["discordId"], member["geoguessrId"], member["surname"], member["flag"]]
    )
    return

async def gspread_new_team(team: list[dict]):
    clientg = await connect_gsheet_api()
    spreadsheet = await clientg.open("[ORGA] Guess and Give Inscriptions")
    worksheet = await spreadsheet.worksheet("Teams")
    await worksheet.append_row(
        [team[0]["discordId"], team[0]["geoguessrId"], team[0]["surname"], team[0]["flag"],
         team[1]["discordId"], team[1]["geoguessrId"], team[1]["surname"], team[1]["flag"]]
    )
    return

