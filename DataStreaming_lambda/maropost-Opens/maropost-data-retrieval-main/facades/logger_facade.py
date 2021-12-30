class LoggerFacade:
    def __init__(self, logger):
        self._logger = logger

    def info(self, message):
        return self._logger.info(message)

    def error(self, message):
        return self._logger.error(message)
