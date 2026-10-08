import logging

from devaci.console import configure_logging, get_logger, logger


def test_get_logger_returns_child_logger():
    assert get_logger("demo").name == "devaci.demo"


def test_get_logger_without_name_returns_root():
    assert get_logger() is logger


def test_configure_logging_is_idempotent():
    original = list(logger.handlers)
    try:
        configure_logging()
        configure_logging()
        streams = [
            handler
            for handler in logger.handlers
            if isinstance(handler, logging.StreamHandler)
            and not isinstance(handler, logging.NullHandler)
        ]
    finally:
        logger.handlers = original

    assert len(streams) == 1
