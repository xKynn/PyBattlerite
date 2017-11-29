import datetime


def _get_object(lst, _id):
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
        self.side = stats['outfit']

        if 'score' in stats:
            self.ability_uses = stats['abilityUses']
            self.damage_done = stats['damageDone']
            self.damage_received = stats['damageReceived']
            self.deaths = stats['deaths']
            self.disables_done = stats['disablesDone']
            self.disables_received = stats['disablesReceived']
            self.energy_gained = stats['energyGained']
            self.energy_used = stats['energyUsed']
            self.healing_done = stats['healingDone']
            self.healing_received = stats['healingReceived']
            self.kills = stats['kills']
            self.score = stats['score']
            self.time_alive = stats['timeAlive']
            self.user_id = stats['userID']

        if 'relationships' in data:
            self.player = Player(data['relationships']['player']['data'])


class Round(BaseBRObject):
    __slots__ = ['duration', 'ordinal', 'winning_team', 'participants']

    def __init__(self, _round, included):
        super().__init__(_round)
        data = _get_object(included, _round['id'])
        self.duration = data['attributes']['duration']
        self.ordinal = data['attributes']['ordinal']
        self.winning_team = data['attributes']['stats']['winningTeam']

        # self.participants = list()
        # for participant in data['relationships']['participants']['data']:
        #     self.participants.append(Participant(participant, included))


class Rosters(BaseBRObject):
    __slots__ = ['shard_id', 'score', 'won', 'participants', 'team']

    def __init__(self, roster, included):
        super().__init__(roster)
        data = _get_object(included, roster['id'])
        self.shard_id = data['attributes']['shardId']
        self.score = data['attributes']['stats']['score']
        self.won = data['attributes']['won']

        self.participants = list()
        for participant in data['relationships']['participants']['data']:
            self.participants.append(Participant(participant, included))

        # if 'team' in data['relationships']:
        #     self.team = Team(data['relationships']['team'])

# class MatchTelemetry(BaseBRObject):
#     __slots__ = ['time', 'userId']
#
#     def __init__(self, data):
#         super().__init__(data)


class Match(BaseBRObject):
    __slots__ = ['created_at', 'duration', 'game_mode', 'patch', 'shard_id', 'map_id', 'type', 'telemetry_url',
                 'rosters', 'rounds', 'spectators', 'session']

    def __init__(self, data, session):
        included = data['included']
        data = data['data']
        super().__init__(data)
        self.created_at = datetime.datetime.strptime(data['attributes']['createdAt'], "%Y-%m-%dT%H:%M:%SZ")
        self.duration = data['attributes']['duration']
        self.game_mode = data['attributes']['gameMode']
        self.patch = data['attributes']['patchVersion']
        self.shard_id = data['attributes']['shardId']
        self.map_id = data['attributes']['stats']['mapID']
        self.type = data['attributes']['stats']['type']
        self.rosters = list()
        for roster in data['relationships']['rosters']['data']:
            self.rosters.append(Rosters(roster, included))
        self.rounds = list()
        for _round in data['relationships']['rounds']['data']:
            self.rounds.append(Round(_round, included))
        self.spectators = list()
        for participant in data['relationships']['spectators']['data']:
            self.spectators.append(Participant(participant, included))
        self.telemetry_url = _get_object(included,
                                         data['relationships']['assets']['data'][0]['id'])['attributes']['URL']
        self.session = session

    async def get_telemetry(self, session=None):
        sess = session or self.session
        async with sess.get(self.telemetry_url, headers={'Accept': 'application/json'}) as resp:
            data = await resp.json()

        # After understanding the telemetry structure, to provide it as usable data is going to be a tough ordeal,
        # but one that can be looked into later
        return data

