class Error(Exception):
    pass


class WrongParametersPassedToEntity(Error, ValueError):
    pass


class CampaignError(Error, ValueError):
    pass
