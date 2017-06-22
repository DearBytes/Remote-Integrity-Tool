#!/usr/bin/env python
# Copyright (C) 2017 DearBytes B.V. - All Rights Reserved
from tabulate import tabulate

from models import Server, Checksum, Event


class Inspector:

    def __init__(self, args):
        """
        Inspector constructor
        :param args: Arguments passed to the scripts
        """
        self.args = args

    def run(self):
        """
        Run the database inspector
        :return: None
        """
        if self.args.list == "servers":
            return self._list_servers()

        if self.args.list == "checksums":
            return self._list_checksums()

        if self.args.list == "events":
            return self._list_events()

    def _list_servers(self):
        """
        Print a list of all servers
        :return: None
        """
        data = Server.query().all()
        print(tabulate([d.values() for d in data], Server.keys(), "grid"))

    def _list_checksums(self):
        """
        Print a list of all checksums
        :return: None
        """
        data = Checksum.query().all()
        print(tabulate([d.values() for d in data], Checksum.keys(), "grid"))

    def _list_events(self):
        """
        Print a list of all events
        :return: None
        """
        data = Event.query().all()
        print(tabulate([d.values() for d in data], Event.keys(), "grid"))
