import datetime
from urllib.parse import urlparse
from urllib.parse import parse_qs

from asyncbattlerite.errors import BRPaginationError
from asyncbattlerite.utils import StackableFinder, Localizer


def _get_object(lst, _id):
    """
    Internal function to grab data referenced inside response['included']
    """
    for item in lst:
        if item['id'] == _id:
            return item


class BaseBRObject:
    """
    A base object for most data classes
    
    Attributes
    ----------
    id : int
        A general unique ID for each type of data.
    """
    __slots__ = ['id']

    def __init__(self, data):
        self.id = data['id']


class Player(BaseBRObject):
    """
    A class that holds general user data, if this is through a Match, this will not have
    name, picture and title, only an ID
    
    Attributes
    ----------
    id : int
        A general unique ID for each type of data.
    name : str
        The player's name
    picture : int
        The picture ID for this player
    title : int
        This player's ingame title
    """
    __slots__ = ['id', 'name', 'picture', 'title', 'stats']

    def __init__(self, data, lang: str):
        print('in player')
        super().__init__(data)
        if data.get('attributes'):
            self.name = data['attributes']['name']
            self.picture = data['attributes']['stats'].pop('picture')
            self.title = data['attributes']['stats'].pop('title')
            stackables = StackableFinder()
            localizer = Localizer(lang)
            self.stats = {}
            for key, value in data['attributes']['stats'].items():
                _item = stackables.find(key)
                if _item is not None:
                    try:
                        print(_item['LocalizedName'])
                    except:
                        pass
                    name = localizer.localize(_item['LocalizedName']) if _item['LocalizedName'] else _item['DevName']
                    self.stats[key] = {'localized_name': name,
                                       'xp': value}
                    if _item['LocalizedName']:
                        self.stats[key]['loc_id'] = _item['LocalizedName']

    def __repr__(self):
        return "<Player: id={}>".format(self.id)


class Team(BaseBRObject):
    __slots__ = ['name', 'shard_id']

    def __init__(self, data):
        super().__init__(data)
        self.name = data['name']
        self.shard_id = data['shardId']


class Participant(BaseBRObject):
    """
    A class that holds data about a participant in a match.
        
    Attributes
    ----------
    id : int
        A general unique ID for each type of data.
    actor : int
    shard_id : str
    attachment : int
    emote : int
    mount : int
    outfit : int
    side : int
    ability_uses : Optional[int]
    damage_done : Optional[int]
    damage_received : Optional[int]
    deaths : Optional[int]
    disables_done : Optional[int]
    disables_received : Optional[int]
    energy_gained : Optional[int]
    energy_used : Optional[int]
    healing_done : Optional[int]
    healing_received : Optional[int]
    kills : Optional[int]
    score : Optional[int]
    time_alive : Optional[int]
    user_id : Optional[int]
    player : Optional[:class:`Player`]
    """
    __slots__ = ['actor', 'shard_id', 'attachment', 'emote', 'mount', 'outfit', 'player', 'side', 'ability_uses',
                 'damage_done', 'damage_received', 'deaths', 'disables_done', 'disables_received', 'energy_gained',
                 'energy_used', 'healing_done', 'healing_received', 'kills', 'score', 'time_alive', 'user_id']

    def __init__(self, participant, included):
        super().__init__(participant)
        data = _get_object(included, participant['id'])
        self.actor = data['attributes']['actor']
        self.shard_id = data['attributes']['shardId']
        stats = data['attributes']['stats']
        self.attachment = stats['attachment']
        self.emote = stats['emote']
        self.mount = stats['mount']
        self.outfit = stats['outfit']
        self.side = stats['side']

        # These may or may not exist
        self.ability_uses = stats.get('abilityUses')
        self.damage_done = stats.get('damageDone')
        self.damage_received = stats.get('damageReceived')
        self.deaths = stats.get('deaths')
        self.disables_done = stats.get('disablesDone')
        self.disables_received = stats.get('disablesReceived')
        self.energy_gained = stats.get('energyGained')
        self.energy_used = stats.get('energyUsed')
        self.healing_done = stats.get('healingDone')
        self.healing_received = stats.get('healingReceived')
        self.kills = stats.get('kills')
        self.score = stats.get('score')
        self.time_alive = stats.get('timeAlive')
        self.user_id = stats.get('userID')

        if 'relationships' in data:
            self.player = Player(data['relationships']['player']['data'])
        else:
            self.player = None

    def __repr__(self):
        return "<Participant: id={0} shard_id={1} actor={2} bot={3}>".format(self.id, self.shard_id, self.actor,
                                                                             True if not self.player else False)


class Round(BaseBRObject):
    """
    A class that holds general data about a round.

    Attributes
    ----------
    id : int
        A general unique ID for each type of data.
    duration : int
        Duration in seconds of this round.
    ordinal : int
        The round number this round was in a match.
    winning_team : int
        Signifies which of the teams/rosters won the round.
    """
    __slots__ = ['duration', 'ordinal', 'winning_team', 'participants']

    def __init__(self, _round, included):
        super().__init__(_round)
        data = _get_object(included, _round['id'])
        self.duration = data['attributes']['duration']
        self.ordinal = data['attributes']['ordinal']
        self.winning_team = data['attributes']['stats']['winningTeam']

    def __repr__(self):
        return "<Round: id={} duration={} ordinal={}>".format(self.id, self.duration, self.ordinal)


class Roster(BaseBRObject):
    """
    A class that holds data about one of the two teams in a match.

    Attributes
    ----------
    id : int
        A general unique ID for each type of data.
    shard_id : str
        The shard on which this roster data resides, only `global` is available at the moment.
    score : int
        The roster's overall score for a match.
    won : bool
        Signifies if the roster won a match.
    participants : list
       A list of :class:`Participant` representing players that are part of the roster.
    """
    __slots__ = ['shard_id', 'score', 'won', 'participants', 'team']

    def __init__(self, roster, included):
        super().__init__(roster)
        data = _get_object(included, roster['id'])
        self.shard_id = data['attributes']['shardId']
        self.score = data['attributes']['stats']['score']
        self.won = True if data['attributes']['won'] == 'true' else False

        self.participants = []
        for participant in data['relationships']['participants']['data']:
            self.participants.append(Participant(participant, included))

    def __repr__(self):
        return "<Roster: id={0} shard_id={1} won={2}>".format(self.id, self.shard_id, self.won)


class Match(BaseBRObject):
    """
    A class that holds data for a match.

    .. _datetime.datetime: https://docs.python.org/3.6/library/datetime.html#datetime-objects
    .. _aiohttp.ClientSession: https://aiohttp.readthedocs.io/en/stable/client_reference.html#client-session

    Attributes
    ----------
    id : int
        A general unique ID for each type of data.
    created_at : datetime.datetime_
        Time when the match was created.
    duration : int
        The match's duration in seconds.
    game_mode : str
        The gamemode this match was of.
    patch : str
        The Battlerite patch version this match was played on.
    shard_id : str
        The shard on which this match data resides, only `global` is available at the moment.
    map_id : int
        The match's map's ID.
    type : str
        The match type, ex: `QUICK2V2 `.
    rosters : list
        A list of :class:`Roster` objects representing rosters taking part in the match.
    rounds : list
        A list of :class:`Round` objects representing each round in the match.
    spectators : list
        A list of :class:`Participant` objects representing spectators, this seems unimplemented in the game as of now.
    telemetry_url : str
        URL for the telemetry file for this match
    session : Optional[aiohttp.ClientSession_]
        Optional session to use to request match data.
    """
    __slots__ = ['created_at', 'duration', 'game_mode', 'patch', 'shard_id', 'map_id', 'type', 'telemetry_url',
                 'rosters', 'rounds', 'spectators', 'session']

    def __init__(self, data, session, included=None):
        included = included or data['included']
        data = data if included else data['data']
        super().__init__(data)
        self.created_at = datetime.datetime.strptime(data['attributes']['createdAt'], "%Y-%m-%dT%H:%M:%SZ")
        self.duration = data['attributes']['duration']
        self.game_mode = data['attributes']['gameMode']
        self.patch = data['attributes']['patchVersion']
        self.shard_id = data['attributes']['shardId']
        self.map_id = data['attributes']['stats']['mapID']
        self.type = data['attributes']['stats']['type']
        self.rosters = []
        for roster in data['relationships']['rosters']['data']:
            self.rosters.append(Roster(roster, included))
        self.rounds = []
        for _round in data['relationships']['rounds']['data']:
            self.rounds.append(Round(_round, included))
        self.spectators = []
        for participant in data['relationships']['spectators']['data']:
            self.spectators.append(Participant(participant, included))
        self.telemetry_url = _get_object(included,
                                         data['relationships']['assets']['data'][0]['id'])['attributes']['URL']
        self.session = session

    def __repr__(self):
        return "<Match: id={0} shard_id={1}>".format(self.id, self.shard_id)

    async def get_telemetry(self, session=None):
        """
        Get telemetry data for a match.

        .. _aiohttp.ClientSession: https://aiohttp.readthedocs.io/en/stable/client_reference.html#client-session

        Parameters
        ----------
        session : Optional[aiohttp.ClientSession_]
            Optional session to use to request telemetry data.

        Returns
        -------
        `dict`
            Match telemetry data
        """
        sess = session or self.session
        async with sess.get(self.telemetry_url, headers={'Accept': 'application/json'}) as resp:
            data = await resp.json()

        # After understanding the telemetry structure, to provide it as usable data is going to be a tough ordeal,
        # but one that can be looked into later
        return data


class MatchPaginator:
    """
    Returned only by BRClient.get_matches
    """
    __slots__ = ['matches', 'next_url', 'first_url', 'client', 'prev_url', 'offset']

    def __init__(self, matches, data, client):
        self.matches = matches
        self.next_url = data.get('next')
        self.first_url = data.get('first')
        self_params = parse_qs(urlparse(data['self'])[4])
        self.offset = self_params.get('page[offset]', 0)
        if self.offset:
            self.offset = self.offset[0]
        self.prev_url = data.get('prev')
        self.client = client

    def __getitem__(self, item):
        return self.matches[item]

    def __iter__(self):
        return iter(self.matches)

    def __repr__(self):
        return "<MatchPaginator: offset={0} next={1} prev={2}>".format(self.offset, True if self.next_url else False,
                                                                        True if self.prev_url else False)

    async def _matchmaker(self, url, sess=None):
        data = await self.client.gen_req("{}matches".format(url), session=sess)
        matches = []
        for match in data['data']:
            matches.append(Match(match, self.client.session, data['included']))
        print(matches)
        self.__init__(matches, data['links'], self.client)
        return matches

    async def next(self, session=None):
        """
        Move to the next page of matches.

        .. _aiohttp.ClientSession: https://aiohttp.readthedocs.io/en/stable/client_reference.html#client-session

        Parameters
        ----------
        session : Optional[aiohttp.ClientSession_]
            Optional session to use to make this request.

        Returns
        -------
        `list`
            A list of :class:`Match`.

        Raises
        ------
        BRPaginationError
            The current page is the last page of results
        """
        if self.next_url:
            matches = await self._matchmaker(self.next_url, session)
            return matches
        else:
            raise BRPaginationError("This is the last page")

    async def first(self, session=None):
        """
        Move to the first page of matches.

        .. _aiohttp.ClientSession: https://aiohttp.readthedocs.io/en/stable/client_reference.html#client-session

        Parameters
        ----------
        session : Optional[aiohttp.ClientSession_]
            Optional session to use to make this request.

        Returns
        -------
        `list`
            A list of :class:`Match`.

        """
        matches = await self._matchmaker(self.first_url, session)
        return matches

    async def prev(self, session=None):
        """
        Move to the previous page of matches.

        .. _aiohttp.ClientSession: https://aiohttp.readthedocs.io/en/stable/client_reference.html#client-session

        Parameters
        ----------
        session : Optional[aiohttp.ClientSession_]
            Optional session to use to make this request.

        Returns
        -------
        `list`
            A list of :class:`Match`.

        Raises
        ------
        BRPaginationError
            The current page is the first page of results
        """
        if self.prev_url:
            matches = await self._matchmaker(self.prev_url, session)
            return matches
        else:
            raise BRPaginationError("This is the first page")
