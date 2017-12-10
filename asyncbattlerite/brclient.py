import asyncio
import aiohttp
import datetime

from asyncbattlerite.models import Player, Match, MatchPaginator
from asyncbattlerite.errors import BRRequestException, NotFoundException, BRServerException, BRFilterException


class BRClient:
    """
    Top level class for user to interact with the API.

    .. _aiohttp.ClientSession: https://aiohttp.readthedocs.io/en/stable/client_reference.html#client-session

    Parameters
    ----------
    key : str
        The official Battlerite API key
    session : Optional[aiohttp.ClientSession_]
    """
    def __init__(self, key, session: aiohttp.ClientSession=None):
        self.session = session or aiohttp.ClientSession()
        self.base_url = "https://api.dc01.gamelockerapp.com/shards/global/"
        self.status_url = "https://api.dc01.gamelockerapp.com/status"
        self.headers = {
            'Authorization': 'Bearer {}'.format(key),
            'Accept': 'application/json'
        }

    async def gen_req(self, url, params=None, session=None):
        sess = session or self.session
        async with sess.get(url, headers=self.headers,
                            params=params) as req:
            try:
                resp = await req.json()
            except (asyncio.TimeoutError, aiohttp.ClientResponseError):
                raise BRRequestException(req, {})

            if 300 > req.status >= 200:
                return resp
            elif req.status == 404:
                raise NotFoundException(req, resp)
            elif req.status > 500:
                raise BRServerException(req, resp)
            else:
                raise BRRequestException(req, resp)

    async def get_status(self):
        """
        Check if the API is up and running

        Returns
        -------
        tuple(createdAt: str, version: str):
        """
        data = await self.gen_req(self.status_url)
        return data['data']['attributes']['releasedAt'], data['data']['attributes']['version']

    async def match_by_id(self, match_id):
        """
        Get a Match by its ID.

        Parameters
        ----------
        match_id : int or str

        Returns
        -------
        :class:`asyncbattlerite.models.Match`
            A match object representing the requested match.
        """
        data = await self.gen_req("{0}matches/{1}".format(self.base_url, match_id))
        return Match(data, self.session)

    @staticmethod
    def _isocheck(time):
        """
        Check if a time string is compatible with iso8601
        """
        try:
            datetime.datetime.strptime(time, "%Y-%m-%dT%H:%M:%SZ")
            return True
        except ValueError:
            return False

    async def get_matches(self, offset: int=None, limit: int=None, after=None, before=None, playernames: list=None,
                          playerids: list=None, teamnames: list=None, gamemode: str=None):
        """
        Access the /matches endpoint and grab a list of matches

        .. _datetime.datetime: https://docs.python.org/3.6/library/datetime.html#datetime-objects

        Parameters
        ----------
        offset : Optional[int]
            The nth number of match to start the page from.
        limit : Optional[int]
            Number of matches to return.
        after : Optional[str or datetime.datetime_]
            Filter to return matches after provided time period, if an str is provided it should follow the **iso8601** format.
        before :  Optional[str or datetime.datetime_]
            Filter to return matches before provided time period, if an str is provided it should follow the **iso8601** format.
        playernames : list
            Filter to only return matches with provided players in them by looking for their player names.
        playerids : list
            Filter to only return matches with provided players in them by looking for their player IDs.
        teamnames : list
            Filter to only return matches where provided team names are playing.
        gamemode : str

        Returns
        -------
        :class:`asyncbattlerite.models.MatchPaginator`
            A MatchPaginator instance representing a get_matches request
        """
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

        data = await self.gen_req("{}matches".format(self.base_url), params=params)
        matches = []
        for match in data['data']:
            matches.append(Match(match, self.session, data['included']))
        return MatchPaginator(matches, data['links'], self)

    async def player_by_id(self, player_id: int):
        """
        Get a player's info by their ID.

        Parameters
        ----------
        player_id : int

        Returns
        -------
        :class:`asyncbattlerite.models.Player`
            A Player object representing the requested player
        """
        data = await self.gen_req("{0}players/{1}".format(self.base_url, player_id))
        return Player(data['data'])

    async def get_players(self, playerids: list):
        """
        Get multiple players' info at once.

        Parameters
        ----------
        playerids : list
            A list of playerids, either a `list` of strs or a `list` of ints.
            Max list length is 6.

        Returns
        -------
        list
            A list of :class:`asyncbattlerite.models.Player`
        """
        if not len(playerids) <= 6:
            raise BRFilterException("Only a maximum of 6 playerIDs are allowed for a single request of get_players.")
        params = {'filter[playerIds]': ','.join(playerids)}
        data = await self.gen_req("{0}players", params=params)
        return [Player(player) for player in data['data']]
