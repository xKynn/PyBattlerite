import datetime


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
