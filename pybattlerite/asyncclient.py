import asyncio
import aiohttp

from .clientbase import ClientBase
from .models import Player, AsyncMatch, AsyncMatchPaginator
from .errors import BRRequestException
from .errors import NotFoundException
from .errors import BRServerException
from .errors import EmptyResponseException


class AsyncClient(ClientBase):
    """
    Top level class for user to interact with the API.

    .. _aiohttp.ClientSession: https://aiohttp.readthedocs.io/en/stable/client_reference.html#client-session

    Parameters
    ----------
    key : str
        The official Battlerite API key.
    session : Optional[aiohttp.ClientSession_]
    lang : str, Default['English']
        The language to localise game specific strings in.\n
        Currently available languages are:\n
        `Brazilian, English, French, German, Italian, Japanese, Korean,
        Polish, Romanian, Russian, SChinese, Spanish, Turkish.`
    """
    def __init__(self, key, session: aiohttp.ClientSession=None, lang: str='English'):
        if lang in self.avl_langs:
            self.lang = lang
        else:
            raise Exception('{0} is not an available language.\nAs of now only'
                            'these languages are available:{1}'.format(lang, ', '.join(self.avl_langs)))
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
        :class:`pybattlerite.models.AsyncMatch`
            A match object representing the requested match.
        """
        data = await self.gen_req("{0}matches/{1}".format(self.base_url, match_id))
        return AsyncMatch(data, self.session)

    async def get_matches(self, offset: int=None, limit: int=None, after=None, before=None, playerids: list=None):
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
        playerids : list
            Filter to only return matches with provided players in them by looking for their player IDs.
        Returns
        -------
        :class:`pybattlerite.models.AsyncMatchPaginator`
            A MatchPaginator instance representing a get_matches request
        """
        # Check compatibility 'after' and 'before' with iso8601
        # Also checks if after isn't greater than before

        params = self.prepare_match_params(offset, limit, after, before, playerids)

        data = await self.gen_req("{}matches".format(self.base_url), params=params)
        matches = []
        for match in data['data']:
            matches.append(AsyncMatch(match, self.session, data['included']))
        return AsyncMatchPaginator(matches, data['links'], self)

    async def player_by_id(self, player_id: int):
        """
        Get a player's info by their ID.

        Parameters
        ----------
        player_id : int

        Returns
        -------
        :class:`pybattlerite.models.Player`
            A Player object representing the requested player.
        """
        data = await self.gen_req("{0}players/{1}".format(self.base_url, player_id))
        return Player(data['data'], self.lang)

    async def _players(self, playerids: list=None, steamids: list=None, usernames: list=None, single=False):
        params = self.prepare_players_params(playerids, steamids, usernames)

        data = await self.gen_req("{0}players".format(self.base_url), params=params)
        if len(data['data']) == 0:
            raise EmptyResponseException("No Players with the specified criteria were found.")
        if not single:
            return [Player(player, self.lang) for player in data['data']]
        else:
            return Player(data['data'][0], self.lang)

    async def get_players(self, playerids: list=None, steamids: list=None, usernames: list=None):
        """
        Get multiple players' info at once.

        .. _here: https://developer.valvesoftware.com/wiki/SteamID

        Parameters
        ----------
        playerids : list
            A list of playerids, either a `list` of strs or a `list` of ints.
            Max list length is 6.
        steamids : list
            A list of steamids, a `list` of ints, this accepts only `SteamID64` specification, check here_ for more
            details.
            Max list length is 6
        usernames : list
            A list of usernames, a `list` of strings, case insensitive.
            Max list length is 6

        Returns
        -------
        list
            A list of :class:`pybattlerite.models.Player`
        """
        return await self._players(playerids, steamids, usernames)

    async def player_by_name(self, username):
        """
        Get a player's info by their ingame name.

        Parameters
        ----------
        username : str
            Case insensitive username

        Returns
        -------
        :class:`pybattlerite.models.Player`
            A Player object representing the requested player.
        """
        return await self._players(usernames=[username], single=True)
