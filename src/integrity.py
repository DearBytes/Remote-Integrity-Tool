#!/usr/bin/env python
# Copyright (C) 2017 DearBytes B.V. - All Rights Reserved
from axel import Event as EventHandler
from models import database_exists, create_database, DATABASE_PATH, Server, Checksum, Event


class Integrity:
    """
    Class that handles the integrity check process
    If the current server does not exist in the database, a new record will be added
    """

    def __init__(self, config):
        """
        Integrity constructor
        :param config: Configuration object
        :type config: config.Config
        """
        self.config = config
        self.server = None
        self.server_is_new = False  # If set to true, no events will be fired
        self.events = []

        self.on_events_detected = EventHandler()

    def load_database(self):
        """
        Loads and initializes the database if necessary
        :return: None
        """
        if not database_exists():
            print("[+] No database found, creating database '{}'".format(DATABASE_PATH))
            create_database()

        if self._server_exists():
            self._load_server()
        else:
            print("[+] First run detected for server '{}', setting up tracker.".format(self.config.server_name))
            print("[?] Note: No changes will be able to be detected this session")
            self._add_server()

    def _server_exists(self):
        """
        Check if this server already is being tracked
        :return: Returns true if the server already exists
        """
        return Server.exists(name=self.config.server_name)

    def _add_server(self):
        """
        Add the current server to the table of servers
        The server_is_new flag will also be set for this session
        :return: None
        """
        self.server = Server.create(name=self.config.server_name)
        self.server_is_new = True

    def _load_server(self):
        """
        Load the server from the database
        :return: None
        """
        self.server = Server.get(name=self.config.server_name)

    def identify(self, output):
        """
        Identify
        :param output: Server output
        :type output: list
        :return:
        """
        for index, (path, checksum) in enumerate(output):

            # Find the checksum record
            checksum_record = self.server.get_related_checksum(path, checksum)

            # New (unknown) file detected
            if checksum_record is None:
                checksum_record = Checksum.create(path=path, checksum=checksum, server=self.server)
                self._handle_file_added(checksum_record)
                continue

            # Check if the file was modified
            if checksum_record.checksum != checksum:
                self._handle_file_modified(checksum_record, checksum)
                checksum_record.checksum = checksum
                continue

        # Loop through all known records first and try to find them
        for checksum_record in self.server.checksums:
            if not any([o for o in output if o[0] == checksum_record.path]):
                self._handle_file_removed(checksum_record)
                checksum_record.delete()

        # On events detected
        if any(self.events):
            self.on_events_detected.fire(self._get_events_as_anonymous_obj_list())

    def _get_events_as_anonymous_obj_list(self):
        """
        Convert the events dict to a list of anonymous objects
        :return: List of anonymous objects
        :rtype: dict[object]
        """
        return [e.to_anonymous_object() for e in self.events]

    def _handle_file_added(self, checksum_record):
        """
        An unknown new file was detected, log the event
        :param checksum_record: Checksum record which the event will be related to
        :type checksum_record: models.Checksum
        :return: None
        """
        if not self.server_is_new:
            description = "A new file was detected at '{path}'".format(path=checksum_record.path)
            event = Event.create(event=Event.FILE_ADDED, description=description, checksum=checksum_record)
            self.events.append(event)

    def _handle_file_modified(self, checksum_record, checksum):
        """
        A known file was modified, log the event
        :param checksum_record: Checksum record which the event will be related to
        :param checksum: The new checksum that was detected
        :type checksum_record: models.Checksum
        :type checksum: str
        :return: None
        """
        description = "File modification was detected at '{path}'".format(path=checksum_record.path)
        event = Event.create(event=Event.FILE_MODIFIED, description=description, checksum=checksum_record)
        self.events.append(event)

    def _handle_file_removed(self, checksum_record):
        """
        A known file was modified, log the event
        :param checksum_record: Checksum record which the event will be related to
        :type checksum_record: models.Checksum
        :return: None
        """
        description = "File removal was detected at '{path}'".format(path=checksum_record.path)
        event = Event.create(event=Event.FILE_REMOVED, description=description, checksum=checksum_record)
        self.events.append(event)

    def print_statistics(self):
        """
        Print the statistics of all events that were found
        :return:
        """
        print("[+] Integrity statistics")
        print("    |-- Files added:    {}".format(self._get_addition_event_count()))
        print("    |-- Files removed:  {}".format(self._get_removal_event_count()))
        print("    `-- Files modified: {}".format(self._get_modified_event_count()))

    def _get_addition_event_count(self):
        """
        Get the amount of events related to file removal
        :return: Amount of modification events
        :rtype: int
        """
        return len([e for e in self.events if e.event == Event.FILE_ADDED])

    def _get_removal_event_count(self):
        """
        Get the amount of events related to file removal
        :return: Amount of modification events
        :rtype: int
        """
        return len([e for e in self.events if e.event == Event.FILE_REMOVED])

    def _get_modified_event_count(self):
        """
        Get the amount of events related to file modification
        :return: Amount of modification events
        :rtype: int
        """
        return len([e for e in self.events if e.event == Event.FILE_MODIFIED])
