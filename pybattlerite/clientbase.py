import datetime

from .errors import BRFilterException


class ClientBase:
    avl_langs = ['Brazilian', 'English', 'French', 'German', 'Italian',
                 'Japanese', 'Korean', 'Polish', 'Romanian', 'Russian',
                 'SChinese', 'Spanish', 'Turkish']
    server_types = ['QUICK2V2', 'QUICK3V3', 'PRIVATE']
    ranking_types = ['RANKED', 'UNRANKED', 'NONE']

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

    def prepare_match_params(self, offset, limit, after, before, playerids, server_type, ranking_type, patch_version):
        if after and before:
            if isinstance(after, datetime.datetime) and isinstance(before, datetime.datetime):
                if before <= after:
                    raise BRFilterException("'after' must occur at a time before 'before'")
                else:
                    after = after.strftime("%Y-%m-%dT%H:%M:%SZ")
                    before = before.strftime("%Y-%m-%dT%H:%M:%SZ")
            elif isinstance(after, str) and isinstance(before, str):
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

        if limit and limit not in range(1, 6):
            raise BRFilterException("'limit' can only range from 1-5")
        if server_type and all(map(lambda d: isinstance(d, str), server_type))\
                and all(map(lambda d: d.upper() in self.server_types, server_type)):
            raise BRFilterException("'server_type' can only have 'QUICK2V2', 'QUICK3V3' or 'PRIVATE'")
        if ranking_type and all(map(lambda d: isinstance(d, str), ranking_type))\
                and all(map(lambda d: d.upper() in self.ranking_types, ranking_type)):
            raise BRFilterException("'ranking_type' can only have 'RANKED', 'UNRANKED' or 'NONE'")

        params = {}
        if offset:
            params['page[offset]'] = offset
        if limit:
            params['page[limit]'] = limit
        if after:
            params['filter[createdAt-start]'] = after
        if before:
            params['filter[createdAt-end]'] = before
        if server_type:
            params['filter[serverType]'] = ','.join([svt.upper() for svt in server_type])
        if playerids:
            params['filter[playerIds]'] = ','.join([str(_id) for _id in playerids])
        if ranking_type:
            params['filter[rankingType]'] = ','.join([rkt.upper() for rkt in ranking_type])
        if patch_version:
            params['filter[patchVersion]'] = ','.join([str(ver) for ver in patch_version])

        return params

    @staticmethod
    def prepare_players_params(playerids, steamids, usernames):
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

        return params

    @staticmethod
    def prepare_teams_params(playerids, season):
        if not all((playerids, season)):
            raise BRFilterException("Both the filters, 'playerids' and 'season' are required.")
        params = {
            'filter[season]': season,
            'filter[playerIds]': ','.join([str(_id) for _id in playerids])
        }

        return params

