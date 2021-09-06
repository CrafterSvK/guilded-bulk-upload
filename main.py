import os

import aiohttp
import asyncio

MEDIA_API = 'https://media.guilded.gg'
API = 'https://www.guilded.gg/api'
PACK = "./dir"
TEAM_ID = ""
EMAIL = ""
PASSWORD = ""


async def upload_files(filename: str):
    async with aiohttp.ClientSession() as session:
        while True:
            file = open(f'{PACK}/{filename}', 'rb')

            response = await session.post(f'{MEDIA_API}/media/upload',
                                          data={'file': file},
                                          params={'dynamicMediaTypeId': 'CustomReaction'}
                                          )
            data = await response.json()

            try:
                print(f'Uploaded: {filename}')
                return data['url']
            except KeyError:
                if response.status == 429:
                    retry_after = response.headers.get('Retry-After')
                    if retry_after:
                        await asyncio.sleep(int(retry_after))
                    else:
                        await asyncio.sleep(0.5)


async def add_emojis_to_team(emojis, team_id: str, session: aiohttp.ClientSession):
    response = await session.post(f'{API}/teams/{team_id}/bulkCustomReactions', json=dict(urls=emojis))

    if response.status == 200:
        print(f'Successfully added all emotes to server with id: {team_id}')
    else:
        print(await response.json())


async def login(email: str, password: str, session: aiohttp.ClientSession):
    await session.post(f'{API}/login', json={
        'email': email,
        'password': password
    })


async def main():
    session: aiohttp.ClientSession
    async with aiohttp.ClientSession() as session:
        await login(EMAIL, PASSWORD, session)

        emojis = []

        for file in os.listdir(PACK):
            emojis.append({
                'name': file.split('.')[0],
                'url': await upload_files(file)
            })

        await add_emojis_to_team(emojis, TEAM_ID, session)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
