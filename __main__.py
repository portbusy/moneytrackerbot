import argparse
import logging.config
import os

import yaml

from configurator import Config

LOGGER = logging.getLogger(__name__)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='vlc-backend', description='vlc-backend application')

    parser.add_argument('-c', '--config_dir', metavar='configuration_directory',
                        required=False, default="config", type=str,
                        help='Configuration directory to use; '
                             'if not specified, default config directory will be used')

    # Configuration file
    parser.add_argument('-f', '--file_app', metavar='configuration_file',
                        required=False, default="application.ini", type=str,
                        help='Configuration file to use; '
                             'if not specified, default configs will be used')

    cmd_args = parser.parse_args()

    with open(os.path.join(cmd_args.config_dir, "log.yaml"), 'rt') as f:
        log_file = yaml.safe_load(f.read())
    logging.config.dictConfig(log_file)
    LOGGER.info(f"Loaded logging configuration from log.yaml")

    Config.init(cmd_args.config_dir, cmd_args.file_app)

    from telegram.bot import MoneyTrackerBot
    bot = MoneyTrackerBot()
    bot.start()