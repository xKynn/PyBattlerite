from setuptools import setup


setup(
    name = "pybattlerite",
    packages = ['pybattlerite'],
    version = "0.5.13",
    description= "A wrapper for the madglory Battlerite API, complete with synchronous and asynchronous client implementations.",
    author = "xKynn",
    author_email = "xkynn@github.com",
    url = "https://github.com/xKynn/PyBattlerite",
    download_url = "https://github.com/xKynn/PyBattlerite/archive/0.5.14.tar.gz",
    keywords = ['battlerite', 'asyncbattlerite', 'async-battlerite', 'async_battlerite'],
    classifiers = [],
    install_requires=[
        "aiohttp",
        "requests"
    ]
)