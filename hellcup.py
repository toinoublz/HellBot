import aiohttp
import gspread_utilities as gu

async def is_geoguessr_id_correct(geoguessr_id: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://www.geoguessr.com/api/v3/users/{geoguessr_id}/stats') as response:
            if response.ok:
                return True
            else:
                return False


async def inscription(member: dict):
    await gu.gspread_new_registered(member)
    return member