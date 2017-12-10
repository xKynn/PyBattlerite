class BRRequestException(Exception):
    """
    General purpose exception, base class for other request related exceptions.

    .. _aiohttp.ClientResponse : https://aiohttp.readthedocs.io/en/stable/client_reference.html#aiohttp.ClientResponse

    Parameters
    ----------
    response : aiohttp.ClientResponse_
    data : dict
        The json response from the API
    """
    def __init__(self, response, data):
        self.reason = response.reason
        self.status = response.status
        self.error = data.get("errors")
        if self.error is not None:
            self.error = self.error[0]['title']
        super().__init__("{0.status}: {0.reason} - {0.error}".format(self))


class NotFoundException(BRRequestException):
    """
    For the 404s
    """
    pass


class BRServerException(BRRequestException):
    """
    Exception that signifies that the server failed to respond with valid data.
    """
    pass


class BRFilterException(Exception):
    """
    Raised when an invalid filter value is supplied.
    """
    def __init__(self, error):
        super().__init__(error)


class BRPaginationError(Exception):
    """
    Raised when :meth:`asyncbattlerite.models.MatchPaginator.next` or :meth:`asyncbattlerite.models.MatchPaginator.prev`
    are called when the paginator is on the last or first page respectively.
    """
    def __init__(self, error):
        super().__init__(error)