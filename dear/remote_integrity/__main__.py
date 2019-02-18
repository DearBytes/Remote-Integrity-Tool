#!/usr/bin/env python
# Copyright (C) 2017 DearBytes B.V. - All Rights Reserved
from argparse import ArgumentParser

from dear.remote_integrity.exceptions import DearBytesException
from dear.remote_integrity.config import Config
from dear.remote_integrity.inspector import Inspector
from dear.remote_integrity.logger import Logger
from dear.remote_integrity.server import Server
from dear.remote_integrity.integrity import Integrity
from dear.remote_integrity.models import session as database


def main():
    """
    Main entry point of the script
    :return: None
    """
    try:
        args = load_arguments()

        if args.config:
            return dispatch_remote_integrity_checker(args)

        if args.list:
            return dispatch_database_inspector(args)

    except DearBytesException as e:
        print("[!] Error: {}".format(e))


def dispatch_remote_integrity_checker(args):
    """
    Dispatch the main remote integrity tool
    :param args: Arguments passed to the script
    :return: None
    """
    config = load_config(path=args.config)

    server = Server(config=config)
    server.connect()
    output  = server.acquire_checksum_list()

    logger = Logger(config=config)
    integrity = Integrity(config=config)

    integrity.on_events_detected += logger.dispatch_syslog
    integrity.on_events_detected += logger.dispatch_events_mail
    integrity.on_events_detected += logger.dispatch_telegram_msg

    integrity.load_database()
    integrity.identify(output)
    integrity.print_statistics()

    database.commit()


def dispatch_database_inspector(args):
    """
    Dispatch the database inspection tool
    :param args: Arguments passed to the script
    :return: None
    """
    inspector = Inspector(args)
    inspector.run()


def load_arguments():
    """"
    Loads all arguments through argparse
    :return: Parsed ArgumentParser object
    """
    parser = ArgumentParser(description="DearBytes remote file integrity checker")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-c", "--config", help="Path to the server configuration file")
    group.add_argument("-l", "--list", help="List data from the local database")
    return parser.parse_args()


def load_config(path):
    """"
    Loads a config file specified by the argument
    :param path: Path to the configuration file
    :type path: str
    :return: Parsed Config object
    """
    return Config.load(path)


if __name__ == '__main__':
    main()
