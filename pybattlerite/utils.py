import json
import os

from configparser import ConfigParser


class StackableFinder:
    def __init__(self):
        _dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data', 'stackables.json')
        with open(_dir) as f:
            self.data = json.load(f)

    def find(self, _id):
        for item in self.data["Mappings"]:
            if item["StackableId"] == int(_id):
                return item
        return None


class LocParser(ConfigParser):

    def to_dict(self):
        d = dict(self._sections)
        for k in d:
            d[k] = dict(self._defaults, **d[k])
            d[k].pop('__name__', None)
        return d


class Localizer:
    """
    Use this to manually localize any data with an available `loc_id`.
    
    Parameters
    ----------
    lang : str
        The language to localise game specific strings in.\n
        Currently available languages are:\n
        `Brazilian, English, French, German, Italian, Japanese, Korean,
        Polish, Romanian, Russian, SChinese, Spanish, Turkish.`
    """
    def __init__(self, lang):
        parser = LocParser()
        _dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data', 'localization',
                            '{}.ini'.format(lang))
        with open(_dir) as fp:
            parser.readfp(fp)
        self.data = parser.to_dict()['Loc']

    def localize(self, _id):
        """
        Call to return a localized string for your id.
        
        Parameters
        ----------
        _id : str
            An id that refers to the name of an object in multiple languages.\n
            Example: '035ad4c27697469e8163040ae0a4f796'
        
        Returns
        -------
        str
            A localized string in the :class:`Localizer`'s set language.
        """
        return self.data[_id]

