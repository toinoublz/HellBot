import aiohttp

async def is_geoguessr_id_correct(geoguessr_id: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://www.geoguessr.com/user/{geoguessr_id}/stats') as response:
            print(response)
            if response.status == 200:
                return True
            else:
                return False


async def inscription(member: dict):
    return member