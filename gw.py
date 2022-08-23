import logging
import sys
from config import find_config, seed_config, read_config

logger = logging.getLogger(__name__)


def run(config: str = None):
    try:
        config_file = find_config(config)
    except FileNotFoundError:
        logging.debug("No config file found")
        if not (config_file := seed_config()):
            raise FileNotFoundError("No config file found and no config file created")
    config = read_config(config_file)


if __name__ == "__main__":
    run(sys.argv[1]) if len(sys.argv) > 1 else run()
