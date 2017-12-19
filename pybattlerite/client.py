import datetime
import requests

from .clientbase import ClientBase
from .models import Player, Match, MatchPaginator
from .errors import BRRequestException
from .errors import NotFoundException
from .errors import BRServerException
from .errors import BRFilterException
from .errors import EmptyResponseException


class Client(ClientBase):
    """
    Top level class for user to interact with the API.

    .. _requests.Session: http://docs.python-requests.org/en/master/api/#request-sessions

    Parameters
    ----------
    key : str
        The official Battlerite API key.
    session : Optional[requests.Session_]
    lang : str, Default['English']
        The language to localise game specific strings in.\n
        Currently available languages are:\n
        `Brazilian, English, French, German, Italian, Japanese, Korean,
        Polish, Romanian, Russian, SChinese, Spanish, Turkish.`
    """
    def __init__(self, key, session: requests.Session=None, lang: str='English'):
        if lang in self.avl_langs:
            self.lang = lang
        else:
            raise Exception('{0} is not an available language.\nAs of now only'
                            'these languages are available:{1}'.format(lang, ', '.join(self.avl_langs)))
        self.session = session or requests.Session()
        self.base_url = "https://api.dc01.gamelockerapp.com/shards/global/"
        self.status_url = "https://api.dc01.gamelockerapp.com/status"
        self.headers = {
            'Authorization': 'Bearer {}'.format(key),
            'Accept': 'application/json'
        }

    def gen_req(self, url, params=None, session=None):
        sess = session or self.session
        with sess.get(url, headers=self.headers,
                      params=params) as req:
            try:
                resp = req.json()
            except (requests.Timeout, requests.ConnectionError):
                raise BRRequestException(req, {})

            if 300 > req.status_code >= 200:
                return resp
            elif req.status_code == 404:
                raise NotFoundException(req, resp)
            elif req.status_code > 500:
                raise BRServerException(req, resp)
            else:
                raise BRRequestException(req, resp)

    def get_status(self):
        """
        Check if the API is up and running

        Returns
        -------
        tuple(createdAt: str, version: str):
        """
        data = self.gen_req(self.status_url)
        return data['data']['attributes']['releasedAt'], data['data']['attributes']['version']

    def match_by_id(self, match_id):
        """
        Get a Match by its ID.

        Parameters
        ----------
        match_id : int or str

        Returns
        -------
        :class:`pybattlerite.models.Match`
            A match object representing the requested match.
        """
        data = self.gen_req("{0}matches/{1}".format(self.base_url, match_id))
        return Match(data, self.session)

    def get_matches(self, offset: int=None, limit: int=None, after=None, before=None, playerids: list=None):
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
        :class:`pybattlerite.models.MatchPaginator`
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
        # # Make sure 'playernames' is a list of 'str's
        # if playernames:
        #     if not all([isinstance(player, str) for player in playernames]):
        #         raise BRFilterException("'playernames' must be a list of 'str's")
        # # Make sure 'teamnames' is a list of 'str's
        # if teamnames:
        #     if not all([isinstance(team, str) for team in teamnames]):
        #         raise BRFilterException("'teamnames' must be a list of 'str's")
        params = {}
        if offset:
            params['page[offset]'] = offset
        if limit:
            params['page[limit]'] = limit
        if after:
            params['filter[createdAt-start]'] = after
        if before:
            params['filter[createdAt-end]'] = before
        # if playernames:
        #     params['filter[playerNames]'] = ','.join(playernames)
        if playerids:
            params['filter[playerIds]'] = ','.join([str(_id) for _id in playerids])
        # if teamnames:
        #     params['filter[teamNames]'] = ','.join(teamnames)

        data = self.gen_req("{}matches".format(self.base_url), params=params)
        matches = []
        for match in data['data']:
            matches.append(Match(match, self.session, data['included']))
        return MatchPaginator(matches, data['links'], self)

    def player_by_id(self, player_id: int):
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
        data = self.gen_req("{0}players/{1}".format(self.base_url, player_id))
        return Player(data['data'], self.lang)

    def _players(self, playerids: list=None, steamids: list=None, usernames: list=None, single=False):
        if not any((playerids, steamids, usernames)):
            raise BRFilterException("One of the filters 'playerids', 'steamids' and 'usernames' is required.")
        try:
            if len(playerids) > 6:
                raise BRFilterException("Only a maximum of 6 playerIDs are allowed for a single"
                                        " request of get_players.")
        except TypeError:
            pass
        try:
            if len(steamids) > 6:
                raise BRFilterException("Only a maximum of 6 steamIDs are allowed for a single"
                                        " request of get_players.")
        except TypeError:
            pass
        try:
            if len(usernames) > 6:
                raise BRFilterException("Only a maximum of 6 steamIDs are allowed for a single"
                                        " request of get_players.")
        except TypeError:
            pass
        params = {}
        if playerids:
            params['filter[playerIds]'] = ','.join([str(_id) for _id in playerids])
        if steamids:
            params['filter[steamIds]'] = ','.join([str(_id) for _id in steamids])
        if usernames:
            params['filter[playerNames]'] = ','.join([str(name) for name in usernames])
        data = self.gen_req("{0}players".format(self.base_url), params=params)
        if len(data['data']) == 0:
            raise EmptyResponseException("No Players with the specified criteria were found.")
        if not single:
            return [Player(player, self.lang) for player in data['data']]
        else:
            return Player(data['data'][0], self.lang)

    def get_players(self, playerids: list=None, steamids: list=None, usernames: list=None):
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
        return self._players(playerids, steamids, usernames)

    def player_by_name(self, username):
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
        return self._players(usernames=[username], single=True)
