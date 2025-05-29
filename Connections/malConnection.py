import aiohttp
import asyncio
import os

class MALConnection:
    def __init__(self):
        self.base_url = os.getenv("mal_base_url", "")
        self.anime_lookup_endpoint = os.getenv("mal_anime_endpoint", "")
        self.anime_fields = os.getenv("mal_anime_fields", "")
        self.client_id = os.getenv("mal_oauth_client_id", "")
        self.headers = {
            "Content-Type": "application/json",
            "X-MAL-CLIENT-ID": self.client_id,
            }

    async def get(self, endpoint: str, params: dict = None, headers: dict = None):
        url = f"{self.base_url}{endpoint}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers) as response:
                return await response.json()
            
    async def get_anime_details(self, anime_id: int):
        url = f"{self.base_url}{self.anime_lookup_endpoint}{anime_id}"
        params = {"fields": self.anime_fields}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=self.headers) as response:
                return await response.json()

    async def post(self, endpoint: str, data: dict = None, headers: dict = None):
        url = f"{self.base_url}{endpoint}"
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data, headers=headers) as response:
                return await response.json()
            