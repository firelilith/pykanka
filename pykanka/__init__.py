import logging.config

import yaml
import os


def _make_logging():
    path = os.path.dirname(__file__)
    log_cnfg = "logging_config.yml"

    with open(os.path.join(path, log_cnfg), "r") as f:
        config = yaml.safe_load(f)

    for handler in config["handlers"]:
        if "filename" in config["handlers"][handler]:
            if not config["handlers"][handler]["filename"][0] in r"/\.~":
                config["handlers"][handler]["filename"] = os.path.join(path, config["handlers"][handler]["filename"])

    logging.config.dictConfig(config)

    logger = logging.getLogger(__name__)

    logger.info(f"logging was successfully created.")


_make_logging()

from pykanka.kanka_client import KankaClient
