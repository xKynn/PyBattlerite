import datetime
from urllib.parse import urlparse
from urllib.parse import parse_qs

from .errors import BRPaginationError


def _get_object(lst, _id):
    """Internal function to grab data referenced inside response['included']"""
    for item in lst:
        if item['id'] == _id:
            return item


class BaseBRObject:
    __slots__ = ['id']

    def __init__(self, data):
        self.id = data['id']


class Player(BaseBRObject):
    __slots__ = ['id']

    def __init__(self, data):
        super().__init__(data)

    def __repr__(self):
        return "<Player: id={}>".format(self.id)


class Team(BaseBRObject):
    __slots__ = ['name', 'shard_id']

    def __init__(self, data):
        super().__init__(data)
        self.name = data['name']
        self.shard_id = data['shardId']


class Participant(BaseBRObject):
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
    __slots__ = ['shard_id', 'score', 'won', 'participants', 'team']

    def __init__(self, roster, included):
        super().__init__(roster)
        data = _get_object(included, roster['id'])
        self.shard_id = data['attributes']['shardId']
        self.score = data['attributes']['stats']['score']
        self.won = data['attributes']['won']

        self.participants = []
        for participant in data['relationships']['participants']['data']:
            self.participants.append(Participant(participant, included))

    def __repr__(self):
        return "<Roster: id={0} shard_id={1} won={2}>".format(self.id, self.shard_id, self.won)


class Match(BaseBRObject):
    __slots__ = ['created_at', 'duration', 'game_mode', 'patch', 'shard_id', 'map_id', 'type', 'telemetry_url',
                 'rosters', 'rounds', 'spectators', 'session']

    def __init__(self, data, session, included=None):
        included = included or data['included']
        data = data['data'] if included else data
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
        sess = session or self.session
        async with sess.get(self.telemetry_url, headers={'Accept': 'application/json'}) as resp:
            data = await resp.json()

        # After understanding the telemetry structure, to provide it as usable data is going to be a tough ordeal,
        # but one that can be looked into later
        return data


class MatchPaginator:
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
        if self.next_url:
            matches = await self._matchmaker(self.next_url, session)
            return matches
        else:
            raise BRPaginationError("This is the last page")

    async def first(self, session=None):
        matches = await self._matchmaker(self.first_url, session)
        return matches

    async def prev(self, session=None):
        if self.prev_url:
            matches = await self._matchmaker(self.prev_url, session)
            return matches
        else:
            raise BRPaginationError("This is the first page")
