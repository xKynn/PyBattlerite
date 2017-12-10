from distutils.core import setup


setup(
    name = "asyncbattlerite",
    packages = ['asyncbattlerite'],
    version = "0.5.11",
    description= "A non-blocking async wrapper for the madglory Battlerite API",
    author = "xKynn",
    author_email = "xkynn@github.com",
    url = "https://github.com/xKynn/AsyncBattlerite",
    download_url = "https://github.com/xKynn/AsyncBattlerite/archive/0.5.11.tar.gz",
    keywords = ['battlerite', 'asyncbattlerite', 'async-battlerite', 'async_battlerite'],
    classifiers = [],
    install_requires=[
        "aiohttp"
    ]
)