class Error(Exception):
    pass


class WrongParametersPassedToEntity(Error, ValueError):
    pass


class CampaignError(Error, ValueError):
    pass


class ApiThrottlingError(Error):
    pass


class ResponseNotOkError(Error):
    pass


class ParameterMissingError(Error, ValueError):
    pass


class DeletingNonExistentError(Error, ValueError):
    pass


class AccessingNonExistentError(Error):
    pass
