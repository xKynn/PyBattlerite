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
            'Accept': 'application/vnd.api+json'
        }

    async def _req(self, url):
        with await self.session.get(url, headers=self.headers) as response:
            try:
                resp = await response.json()
            except (asyncio.TimeoutError, aiohttp.ClientResponseError):
                raise BRRequestException(response, dict())

            if 300 > resp.status >= 200:
                return resp
            elif resp.status == 404:
                raise NotFoundException
            elif resp.status > 500:
                raise BRServerException
            else:
                raise BRRequestException(response, resp)

    async def match_by_id(self, match_id):
        data = await self._req("{0}matches/{1}".format(self.base_url, match_id))
        return Match(data['data'], self.session)

