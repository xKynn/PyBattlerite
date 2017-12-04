# <a href="https://pypi.python.org/pypi/asyncbattlerite">AsyncBattlerite</a>

An asynchronous python wrapper for madglory's [Battlerite API](http://battlerite-docs.readthedocs.io/en/master/introduction.html)

```
pip install asyncbattlerite
```

## Basic Usage

```py
import aiohttp
import asyncio
import asyncbattlerite

loop = asyncio.get_event_loop()
brc = asyncbattlerite.BRClient('your-api-key')

# You can also provide an aiohttp.ClientSession to the BRClient constructor
session = aiohttp.ClientSession()
brc_a = asyncbattlerite.BRClient('your-api-key', session)

# Get 3 matches after specified time
# after and before can also be datetime.datetime objects
matches = loop.run_until_complete(brc.get_matches(limit=3, after="2017-11-22T20:34:58Z"))

# Go to the next pages of matches
loop.run_until_complete(matches.next())

# Get telemetry data for one of the matches
telemetry = loop.run_until_complete(matches.matches[0].get_telemetry())
```
## Methods and Filters
### *coroutine* `BRClient.get_matches(filters)`
Get matches meeting the filter specifications.
Filters:
* **offset: int** - The nth number of match to start the page from.
* **limit: int** - Number of matches to return.
* **after: str or datetime.datetime** - Filter to return matches after provided time period, if an str is provided it should follow the `iso8601` format.
* **before: str or datetime.datetime** - Filter to return matches before provided time period, if an str is provided it should follow the `iso8601` format.
* **playernames: list of strings** - Filter to only return matches with provided players in them by looking for their player names.
* **playerids: list** - Filter to only return matches with provided players in them by looking for their player IDs.
* **teamnames: list of strings** - Filter to only return matches where provided team names are playing
`returns` - *MatchPaginator*

### *coroutine* `BRClient.match_by_id(match_id)`
Return a match by its ID.<br />
`returns` - *Match*

### *coroutine* `BRClient.get_status()`
Check if the API is up and running.<br />
`returns` - *tuple(createdAt: str(), version: str())*<br />
`raises` - *BRServerExceptioin* if the API is down.

## Classes
### Match
* **created_at** - *datetime.datetime* object representing when the match was created.
* **duration** - The match's duration in seconds.
* **game_mode** - The match's game mode.
* **patch** - The Battlerite patch version this match was played on.
* **shard_id** - The shard on which this match data resides, only `global` is available at the moment.
* **map_id** - The match's map's ID.
* **type** - The match type, ex: `QUICK2V2 `.
* **rosters: list()** - A list of *Roster* objects representing rosters taking part in the match.
* **rounds: list()** - A list of *Round* objects representing each round in the match.
* **spectators: list()** - A list of *Participant* objects representing spectators, this seems unimplemented in the game as of now.
* **telemetry_url** - URL for the telemetry file for this match
* **session** - BRClient's own session or the session provided while initializing BRClient
* *coroutine* `Match.get_telemetry(optional session: aiohttp.ClientSession)`<br />
Get a match's telemetry data, `session` is an optional parameter that defaults to None, use this in case the ClientSession
you provided to the BRClient constructor is no longer active or you want this request to be made from another session.<br />
`returns` - *dict()*

### MatchPaginator
This allows for accessing pagination of data by the API.
* **matches: list() of Match** - A list that holds the current page's matches as *Match* objects.
* *coroutine* **next()** - A coroutine that will take the MatchPaginator to the next page if it exists.<br />
*raises* - `BRPaginationError` - If there is no next page after the current one.
* *coroutine* **prev()** - A coroutine that will take the MatchPaginator to the previous page if it exists.<br />
*raises* - `BRPaginationError` - If the current page is the first page.
* *coroutine* **first()** - A coroutine that will take the MatchPaginator to the first page.

### Roster
* **shard_id** - The shard on which this roster data resides, only `global` is available at the moment.
* **score** - The roster's overall score for a match.
* **won: boolean()** - Signifies if the roster won a match.
* **participants: list()** - A list of *Participant* objects representing players that are part of the roster.

### Round
* **duration** - Duration in seconds of this round.
* **ordinal: int()** - The round number this round was in a match.
* **winning_team: int()** - Signifies which of the teams/rosters won the round.

### Participant
Fields marked with `optional` will not exist in every *Participant* object, these are also all of **int()** type.
* **actor** - ID associated with a Battlerite champ.
* **shard_id** - The shard on which this participant data resides, only `global` is available at the moment.
* **attachment int()** - No clue.
* **emote int()** - The emote ID tied to an emote in Battlerite.
* **mount int()** - The mount ID tied to a mount in Battlerite.
* **outfit int()** - The outfit ID tied to an outfit in Battlerite.
* **side: int()** - Signifies on which side of the match this participant played from.
* `optional` **ability_uses** - Total number of abilities used by this Participant.
* `optional` **damage_done** - Total damage dealt by this Participant.
* `optional` **damage_received**
* `optional` **deaths)**
* `optional` **disables_done**
* `optional` **energy_gained**
* `optional` **energy_used**
* `optional` **healing_done**
* `optional` **healing_received**
* `optional` **kills**
* `optional` **score**
* `optional` **time_alive**
* `optional` **user_id**
* `optional` **player: Player** - Refers to a *Player* object if the Participant was not a bot, in which case it is `None`.

### Player
* **id** - The Player's unique ID

### BaseBRObject
All model classes extend this class, its only attribute is `id`
* **id** - Represents the unique identifier of any Battlerite Data object

## Exceptions
* **BRRequestException** - Base Request Exception that hold's the API's response/reason for the error.
* **NotFoundExceptiom** - Raised for 404, extends *BRRequestException*.
* **BRServerException** - Raised when the server fails to communicate, extends *BRRequestException*.
* **BRFilterException** - Raised when filters don't match the requested format.
* **BRPaginationError** - Raised when *next()* or *prev()* are called in *MatchPaginator* even when they're not available.

## A Request
Please do not bulk scrape data from this API, Stunlock have specified that they would not like users misusing the API
in such a way

### Contact
Demo#9465 on Discord
[@Craft_Eternal36](https://twitter.com/Craft_Eternal36) on Twitter
