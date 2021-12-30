import logging

import watchtower

from facades.logger_facade import LoggerFacade


def get_logger(log_group: str):
    """Returns an instance of logger wrapped in a facade.
    The only logger handler currently added to logger is a Cloud Watch handler.

    Args:
        log_group: str

    Returns:
        An instance of LoggerFacade
    """
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    if len(logger.handlers) == 0:
        logger.addHandler(watchtower.CloudWatchLogHandler(log_group=log_group))

    return LoggerFacade(logger)
