import datetime

from .errors import BRFilterException


class ClientBase:
    avl_langs = ['Brazilian', 'English', 'French', 'German', 'Italian',
                 'Japanese', 'Korean', 'Polish', 'Romanian', 'Russian',
                 'SChinese', 'Spanish', 'Turkish']

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

    def prepare_match_params(self, offset, limit, after, before, playerids):
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
            'tag[season]': season,
            'tag[playerIds]': ','.join([str(_id) for _id in playerids])
        }

        return params

