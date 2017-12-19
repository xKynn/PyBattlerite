Welcome to PyBattlerite's documentation!
===========================================

Basic Usage::

   import pybattlerite
   import requests

   brc = pybattlerite.Client('your-api-key')

   # You can also provide an aiohttp.ClientSession to the BRClient constructor
   session = requests.Session()
   brc_a = pybattlerite.Client('your-api-key', session)

   # Get 3 matches after specified time
   # after and before can also be datetime.datetime objects
   matches = brc.get_matches(limit=3, after="2017-11-22T20:34:58Z")

   # Go to the next pages of matches
   matches.next()

   # Get telemetry data for one of the matches
   telemetry = matches.matches[0].get_telemetry()

Async Usage::

   import aiohttp
   import asyncio
   import pybattlerite

   brc = pybattlerite.AsyncClient('your-api-key')

   # You can also provide an aiohttp.ClientSession to the BRClient constructor
   session = aiohttp.ClientSession()
   brc_a = pybattlerite.AsyncClient('your-api-key', session)

   # Get 3 matches after specified time
   # after and before can also be datetime.datetime objects
   matches = await brc.get_matches(limit=3, after="2017-11-22T20:34:58Z")

   # Go to the next pages of matches
   await matches.next()

   # Get telemetry data for one of the matches
   telemetry = await matches.matches[0].get_telemetry()


pybattlerite.Client
------------------------

.. automodule:: pybattlerite.client
    :members:
    :show-inheritance:

pybattlerite.AsyncClient
------------------------

.. automodule:: pybattlerite.asyncclient
    :members:
    :show-inheritance:

pybattlerite.models
----------------------

.. automodule:: pybattlerite.models
    :members:
    :show-inheritance:

pybattlerite.utils
---------------------

.. automodule:: pybattlerite.utils
     :members:
     :show-inheritance:

pybattlerite.errors
----------------------

.. automodule:: pybattlerite.errors
    :members:
    :show-inheritance: