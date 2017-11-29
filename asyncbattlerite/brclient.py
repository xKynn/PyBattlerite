import asyncio
import aiohttp

from .models import Match
from .errors import BRRequestException, NotFoundException, BRServerException


class BRClient:
    def __init__(self, key, session=None):
        if session is None:
            self.session = aiohttp.ClientSession()
        else:
            self.session = session
        self.base_url = "https://api.dc01.gamelockerapp.com/shards/global/"
        self.headers = {
            'Authorization': f'Bearer {key}',
            'Accept': 'application/json'
        }

    async def _req(self, url):
        async with self.session.get(url, headers=self.headers) as req:
            try:
                resp = await req.json()
            except (asyncio.TimeoutError, aiohttp.ClientResponseError):
                raise BRRequestException(req, dict())

            if 300 > req.status >= 200:
                return resp
            elif req.status == 404:
                raise NotFoundException
            elif req.status > 500:
                raise BRServerException
            else:
                raise BRRequestException(req, resp)

    async def match_by_id(self, match_id):
        data = await self._req("{0}matches/{1}".format(self.base_url, match_id))
        return Match(data, self.session)

