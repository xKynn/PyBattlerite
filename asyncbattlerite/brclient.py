import asyncio
import aiohttp
import datetime

from .models import Match
from .errors import BRRequestException, NotFoundException, BRServerException, BRFilterException


class BRClient:
    def __init__(self, key, session=None):
        self.session = session or aiohttp.ClientSession()
        self.base_url = "https://api.dc01.gamelockerapp.com/shards/global/"
        self.headers = {
            'Authorization': f'Bearer {key}',
            'Accept': 'application/json'
        }

    async def _req(self, url, params=None):
        """General request handler"""
        async with self.session.get(url, headers=self.headers,
                                    params=params) as req:
            try:
                resp = await req.json()
            except (asyncio.TimeoutError, aiohttp.ClientResponseError):
                raise BRRequestException(req, {})

            if 300 > req.status >= 200:
                return resp
            elif req.status == 404:
                raise NotFoundException
            elif req.status > 500:
                raise BRServerException
            else:
                raise BRRequestException(req, resp)

    async def match_by_id(self, match_id):
        """Get a Match by its ID"""
        data = await self._req("{0}matches/{1}".format(self.base_url, match_id))
        return Match(data, self.session)

    @staticmethod
    def _isocheck(time):
        """Check if a time string is compatible with iso8601"""
        try:
            datetime.datetime.strptime(time, "%Y-%m-%dT%H:%M:%SZ")
            return True
        except ValueError:
            return False

    async def get_matches(self, offset: int=None, limit: int=None, after=None, before=None, playernames: list=None,
                          playerids: list=None, teamnames: list=None, gamemode: str=None):
        """Access the /matches endpoint and grab a list of matches"""

        # Check compatibility 'after' and 'before' with iso8601
        # Also checks if after isn't greater than before
        if all((after, before)):
            if all((isinstance(after, datetime.datetime), isinstance(before, datetime.datetime))):
                if before <= after:
                    raise BRFilterException("'after' must occur at a time before 'before'")
                else:
                    after = after.strftime("%Y-%m-%dT%H:%M:%SZ")
                    before = before.strftime("%Y-%m-%dT%H:%M:%SZ")
            elif all((isinstance(after, str), isinstance(before, str))):
                if not all(map(self._isocheck, (after, before))):
                    raise BRFilterException("'after' or 'before', if instances of 'str', should follow the "
                                            "'iso8601' format '%Y-%m-%dT%H:%M:%SZ'")
                t_after = datetime.datetime.strptime(after, "%Y-%m-%dT%H:%M:%SZ")
                t_before = datetime.datetime.strptime(before, "%Y-%m-%dT%H:%M:%SZ")
                if t_before <= t_after:
                    raise BRFilterException("'after' must occur at a time before 'before'")
            else:
                raise BRFilterException("'after' and 'before' should both be instances "
                                        "of either 'str' or 'datetime.datetime'")
        else:
            if after:
                if isinstance(after, datetime.datetime):
                    after = after.strftime("%Y-%m-%dT%H:%M:%SZ")
                elif not self._isocheck(after):
                    raise BRFilterException("'after', if instance of 'str', should follow the 'iso8601' format "
                                            "'%Y-%m-%dT%H:%M:%SZ'")
            elif before:
                if isinstance(before, datetime.datetime):
                    before = before.strftime("%Y-%m-%dT%H:%M:%SZ")
                elif not self._isocheck(before):
                    raise BRFilterException("'before', if instance of 'str', should follow the 'iso8601' format "
                                            "'%Y-%m-%dT%H:%M:%SZ'")
        # Make sure 'playernames' is a list of 'str's
        if playernames:
            if not all([isinstance(player, str) for player in playernames]):
                raise BRFilterException("'playernames' must be a list of 'str's")
        # Make sure 'teamnames' is a list of 'str's
        if teamnames:
            if not all([isinstance(team, str) for team in teamnames]):
                raise BRFilterException("'teamnames' must be a list of 'str's")
        params = {}
        if offset:
            params['page[offset]'] = offset
        if limit:
            params['page[limit]'] = limit
        if after:
            params['filter[createdAt-start]'] = after
        if before:
            params['filter[createdAt-end]'] = before
        if playernames:
            params['filter[playerNames]'] = ','.join(playernames)
        if playerids:
            params['filter[playerIds]'] = ','.join(str(playerids))
        if teamnames:
            params['filter[teamNames]'] = ','.join(teamnames)

        data = await self._req("{0}matches".format(self.base_url), params=params)
        matches = []
        for match in data['data']:
            matches.append(Match(match, self.session, data['included']))
        return matches

