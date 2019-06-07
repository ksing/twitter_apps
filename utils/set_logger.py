import os
import logging


def get_logger(home, file_name, name="tweet_logger"):
    logfile = os.path.join(home, "Logs/{}.log".format(file_name))
    logger = logging.getLogger(name)
    handler = logging.FileHandler(logfile, mode="a")
    formatter = logging.Formatter("%(asctime)s\t[%(levelname)s]\t%(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger
