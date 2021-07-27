"""
Logger instance for CRUSOE project.
"""

import logging
import structlog

DATEFMT = "%Y-%m-%d %H:%M.%S"


def default_adapter(logger, method_name, event_dict):
    """Structlog processor that adapts output of underlying logger
    :param logger: logger
    :param method_name: method_name
    :param event_dict: event_dict
    :return: annotated event_dict
    """
    message = f"{event_dict['event'].ljust(30)}"
    del event_dict['event']
    if len(event_dict) > 0:
        message += " ("
        message += "; ".join(map(lambda x: f"{x[0]}={x[1]}", event_dict.items()))
        message += ")"
    return message


def create_logging_backend(name, file_name, level=logging.INFO):
    """Create instance of logging backend (name has to be unique for the component!)
    :param name: unique name of the logging backend
    :param file_name: name of the output log file
    :param level: logging level
    """
    handler = logging.FileHandler(file_name)
    handler.setFormatter(logging.Formatter("[%(asctime)s][%(levelname)s] %(message)s", DATEFMT))

    logger = logging.getLogger(name)
    logger.setLevel(level)
    if len(logger.handlers) < 1:
        logger.addHandler(handler)

    return logger


def get_logger(name, file_name, processors=[default_adapter], level=logging.INFO):
    """Get instance of logging backend (nahe has to be unique for the component!)
    :param name: unique name of the logging backend
    :param file_name: name of the output log file
    :param processors: list of structlog processors (last one should be adapter)
    :param level: logging level
    """
    return structlog.wrap_logger(
        create_logging_backend(name, file_name, level),
        processors=processors,
        context_class=dict
    )
