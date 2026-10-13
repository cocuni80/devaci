import logging

from devaci.console import (
    LOGGER_NAME,
    configure_logging,
    get_console,
    get_logger,
    logger,
)


def test_get_logger_returns_child_logger():
    assert get_logger("demo").name == "devaci.demo"


def test_get_logger_keeps_qualified_name():
    assert get_logger("devaci.deploy").name == "devaci.deploy"


def test_get_logger_without_name_returns_root():
    assert get_logger() is logger


def test_module_logger_has_no_double_prefix(caplog):
    module_logger = get_logger("devaci.inputs.datasets")

    with caplog.at_level(logging.INFO, logger=LOGGER_NAME):
        module_logger.info("hello")

    assert caplog.records[0].name == "devaci.inputs.datasets"


def test_configure_logging_is_idempotent():
    original_handlers = list(logger.handlers)
    original_level = logger.level
    try:
        configure_logging()
        configure_logging()
        streams = [h for h in logger.handlers if h.get_name() == "devaci-stream"]
    finally:
        logger.handlers = original_handlers
        logger.setLevel(original_level)

    assert len(streams) == 1


def test_configure_logging_sets_level():
    original_handlers = list(logger.handlers)
    original_level = logger.level
    try:
        configure_logging(level=logging.DEBUG)
        assert logger.level == logging.DEBUG
    finally:
        logger.handlers = original_handlers
        logger.setLevel(original_level)


def test_get_console_is_shared():
    assert get_console() is get_console()
