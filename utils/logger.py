import logging


class CustomFormatter(logging.Formatter):

    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(asctime)s[%(levelname)s] %(name)s: '%(message)s' (%(filename)s:%(lineno)d %(funcName)s)"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def create_logger_instance(name):
    logger = logging.getLogger(name)

    logger.propagate = 0
    logger.setLevel(logging.DEBUG)

    logger_handler = logging.StreamHandler()
    logger_handler.setLevel(logging.DEBUG)
    logger.addHandler(logger_handler)
    logger_handler.setFormatter(CustomFormatter())

    return logger
