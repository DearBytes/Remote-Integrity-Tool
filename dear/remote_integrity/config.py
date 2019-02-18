#!/usr/bin/env python
# Copyright (C) 2017 DearBytes B.V. - All Rights Reserved
import os
from configparser import ConfigParser, NoSectionError, NoOptionError

from dear.remote_integrity.exceptions import ConfigurationException


class Config:
    """
    Configuration object
    """

    def __int__(self):

        # [server]
        self.server_name = None
        self.server_port = None
        self.server_address = None

        # [auth]
        self.auth_username = None
        self.auth_private_key = None

        # [filter]
        self.start_directory = None
        self.ignore_files = []
        self.ignore_directories = []
        self.scan_php_modules = True

        # [email]
        self.email_smtp_host = None
        self.email_smtp_user = None
        self.email_smtp_pass = None
        self.email_recipients = []
        self.email_noreply_address = None

        # [telegram]
        self.telegram_api_token = None
        self.telegram_api_chat_id = None

        # [logging]
        self.logging_syslog_host = None

    def smtp_auth_enabled(self):
        """
        Check if SMTP should log in or not
        :return: True if SMTP should call login()
        """
        return self.email_smtp_user and self.email_smtp_pass

    @staticmethod
    def load(path):
        """
        Read the configuration file and extract the
        :param path: Path to the configuration file to be loaded
        :return: New instance of the config object
        :rtype: Config
        """
        if not os.path.exists(path):
            raise ConfigurationException("Configuration file '{}' does not exist, did you specify the correct path?".format(path))

        config = Config()

        parser = ConfigParser()
        parser.read(path)

        try:
            config.server_name = parser.get("server", "server_name")
            config.server_port = parser.getint("server", "server_port", fallback=21)
            config.server_address = parser.get("server", "server_address")

            config.auth_username = parser.get("auth", "auth_username")
            config.auth_private_key = os.path.expanduser(parser.get("auth", "auth_private_key"))

            config.ignore_files = parser.get("filter", "ignore_files").split(",") or []
            config.ignore_directories = parser.get("filter", "ignore_directories").split(",") or []
            config.start_directory = parser.get("filter", "start_directory")
            config.scan_php_modules = parser.getboolean("filter", "scan_php_modules")

            config.email_smtp_host = parser.get("email", "email_smtp_host") or None
            config.email_smtp_user = parser.get("email", "email_smtp_user") or None
            config.email_smtp_pass = parser.get("email", "email_smtp_pass") or None
            config.email_recipients = parser.get("email", "email_recipients") or None
            config.email_noreply_address = parser.get("email", "email_noreply_address") or None

            config.telegram_api_token = parser.get("telegram", "telegram_api_token") or None
            config.telegram_api_chat_id = parser.getint("telegram", "telegram_api_chat_id") or None

            config.logging_syslog_host = parser.get("logging", "logging_syslog_host") or None

        except (NoSectionError, NoOptionError) as e:
            raise ConfigurationException("{} in configuration file '{}'".format(str(e), path))

        for attr in config.__dict__.keys():
            if getattr(config, attr) == "":
                raise ConfigurationException("Missing attribute value '{}' in configuration file '{}'".format(attr, path))

        return config

