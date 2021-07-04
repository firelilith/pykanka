class Error(Exception):
    pass


class WrongParametersPassedToEntity(Error, ValueError):
    pass
