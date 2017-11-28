class BRRequestException(Exception):
    def __init__(self, response, data):
        self.reason = response.reason
        self.status = response.status
        self.error = data.get("errors")
        if self.error is not None:
            self.error = self.error[0]['title']
        super().__init__("{0.status}: {0.reason} - {0.error}".format(self))


class NotFoundException(BRRequestException):
    pass


class BRServerException(BRRequestException):
    pass
