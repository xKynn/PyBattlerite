import aiohttp


class BaseBRObject:
    __slots__ = ['id']

    def __init__(self, data):
        self.id = data['id']


class Player(BaseBRObject):
    __slots__ = ['id']

    def __init__(self, data):
        super().__init__(data)


class Team(BaseBRObject):
    __slots__ = ['name', 'shard_id']

    def __init__(self, data):
        super().__init__(data)
        self.name = data['name']
        self.shard_id = data['shard_id']


class Participant(BaseBRObject):
    __slots__ = ['actor', 'shard_id', 'attachment', 'emote', 'mount', 'outfit', 'player']

    def __init__(self, data):
        super().__init__(data)
        self.actor = data['attributes']['actor']
        self.shard_id = data['attributes']['shardId']
        self.attachment = data['attributes']['stats']['attachment']
        self.emote = data['attributes']['stats']['emote']
        self.mount = data['attributes']['stats']['mount']
        self.outfit = data['attributes']['stats']['outfit']

        if 'relationships' in data:
            self.player = Player(data['relationships']['player']['data'])


class Round(BaseBRObject):
    __slots__ = ['duration', 'ordinal', 'winning_team', 'participants']

    def __init__(self, data):
        super().__init__(data)
        self.duration = data['attributes']['duration']
        self.ordinal = data['attributes']['ordinal']
        self.winning_team = data['attributes']['stats']['winningTeam']

        self.participants = list()
        for participant in data['relationships']['participants']['data']:
            self.participants.append(Participant(participant))


class Rosters(BaseBRObject):
    __slots__ = ['shard_id', 'score', 'side', 'won', 'participants', 'team']

    def __init__(self, data):
        super().__init__(data)
        self.shard_id = data['attributes']['shard_id']
        self.score = data['attributes']['score']
        self.side = data['attributes']['side']
        self.won = data['won']

        self.participants = list()
        for participant in data['relationships']['participants']['data']:
            self.participants.append(Participant(participant))

        if 'team' in data['relationships']:
            self.team = Team(data['relationships']['team'])

# class MatchTelemetry(BaseBRObject):
#     __slots__ = ['time', 'userId']
#
#     def __init__(self, data):
#         super().__init__(data)


class Match(BaseBRObject):
    __slots__ = ['created_at', 'duration', 'game_mode', 'patch', 'shard_id', 'map_id', 'type', 'telemetry_url', 'rosters',
                 'rounds', 'spectators']

    def __init__(self, data):
        super().__init__(data)
        self.created_at = data['attributes']['createdAt']
        self.duration = data['attributes']['duration']
        self.game_mode = data['attributes']['gameMode']
        self.patch = data['attributes']['patchVersion']
        self.shard_id = data['attributes']['shardId']
        self.map_id = data['attributes']['stats']['mapID']
        self.type = data['attributes']['stats']['type']
        self.rosters = list()
        for roster in data['relationships']['rosters']['data']:
            self.rosters.append(Rosters(roster))
        self.rounds = list()
        for _round in data['relationships']['rounds']['data']:
            self.rounds.append(Round(_round))
        self.spectators = list()
        for participant in data['relationships']['spectators']['data']:
            self.spectators.append(Participant(participant))
        self.telemetry_url = data['relationships']['assets']['data'][0]['attributes']['URL']

    async def get_telemetry(self, session=None):
        if session is None:
            session = aiohttp.ClientSession()

        async with session.get(self.telemetry_url, headers={'Accept': 'application/vnd.api+json'}) as resp:
            data = await resp.json()

        return data
        # TODO: Understand the Telemetry structure and make a usable object

