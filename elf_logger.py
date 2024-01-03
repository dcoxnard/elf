import logging
import sys


def handle_exception(exception_type, exception_value, exception_traceback):
    if issubclass(exception_type, KeyboardInterrupt):
        sys.__excepthook__(exception_type, exception_value, exception_traceback)
    else:
        logger.error("Uncaught exception", exc_info=(exception_type,
                                                     exception_value,
                                                     exception_traceback))


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

logger.excepthook = handle_exception

formatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")

filehandler = logging.FileHandler("elf.log")
filehandler.setFormatter(formatter)
logger.addHandler(filehandler)

consolehandler = logging.StreamHandler()
consolehandler.setFormatter(formatter)
logger.addHandler(consolehandler)
