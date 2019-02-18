#!/usr/bin/env python
# Copyright (C) 2017 DearBytes B.V. - All Rights Reserved
import shlex

from paramiko import AutoAddPolicy
from paramiko import RSAKey
from paramiko import SSHClient
from paramiko.ssh_exception import NoValidConnectionsError

from dear.remote_integrity.exceptions import ServerException, DirectoryNotFoundException


class Server:
    """"
    Server class to connect to a remote server
    Once there is a valid connection, all hashes will be calculated on every file
    """

    def __init__(self, config):
        """
        Server constructor
        :param config: Configuration to use
        :type config: config.Config
        """
        self.config = config
        self.client = SSHClient()
        self.client.load_system_host_keys()
        self.connection = None

    def connect(self):
        """
        Connect to the remote server
        :return: None
        """
        try:
            self.client.set_missing_host_key_policy(AutoAddPolicy())
            self.client.connect(
                hostname=self.config.server_address,
                port=self.config.server_port,
                username=self.config.auth_username,
                pkey=RSAKey.from_private_key_file(self.config.auth_private_key))

        except NoValidConnectionsError as e:
            raise ServerException(str(e))

    def acquire_checksum_generator(self, path=None):
        """
        Attempts to acquire a list of checksums of all files recursively
        :return: List of checksums
        :rtype: collections.Generator
        """
        for line in self._exec_checksum_list_cmd(path).splitlines():
            try:
                checksum, path = line.split("  ")[0:2]
            except ValueError:
                print("[!] Warning: Unable to parse checksum output '{}'".format(line))
                continue

            if not self._path_is_blacklisted(path):
                yield path, checksum

    def acquire_checksum_list(self):
        """
        Attempts to acquire a list of checksums of all files recursively
        :return: List of checksums
        :rtype: list
        """
        output  = list(self.acquire_checksum_generator())

        if self.config.scan_php_modules:
            try:
                path = self._exec_php_extension_dir()
                output += list(self.acquire_checksum_generator(path))
            except DirectoryNotFoundException as e:
                print("[!] {}".format(e))
                print(" `- Please install the 'php-dev' package or create a second configuration file with a start directory pointing to your php modules.")

        return output

    def _path_is_blacklisted(self, path):
        """
        Check if the given path is blacklisted (directory/file based)
        :return:
        """
        for directory in self.config.ignore_directories:
            if directory + ("/" if not directory.endswith("/") else "") in path:
                return True

        for file_name in self.config.ignore_files:
            if path.split("/")[-1] == file_name:
                return True

    def _exec_pwd(self):
        """
        Executes the `pwd` command on the remote server to determine the current path
        :return: Returns the current working directory
        :rtype: str
        """
        stdin, stdout, stderr = self.client.exec_command("pwd")
        return stdout.read().decode("utf-8").strip()

    def _exec_home_dir(self):
        """
        Get the home directory of the user
        :return: Current users' home directory
        :rtype: str
        """
        stdin, stdout, stderr = self.client.exec_command("echo $HOME")
        return stdout.read().decode("utf-8").strip()

    def _exec_checksum_list_cmd(self, path=None):
        """
        Execute the checksum list command and return the raw output
        If stderr is set, an exception will be thrown.
        :return: Raw checksum list output
        :rtype: str
        """
        path = self._get_absolute_start_directory(path)
        command = 'find %s -type f -exec sha512sum "{}" +' % shlex.quote(path)
        stdin, stdout, stderr = self.client.exec_command(command)

        stdout = stdout.read()
        stderr = stderr.read()

        if self._exec_successful(stderr):
            return stdout.decode("utf-8")
        else:
            raise ServerException("Unable to retrieve checksum list, reason: {}".format(stderr.decode("utf-8")))

    def _exec_successful(self, stderr):
        """
        Determine whether or not the command was executed successfully
        :param stderr: Stderr output from the command executed on the server
        :type stderr: str
        :return: Returns true if no error is present
        :rtype: bool
        """
        return not any(stderr)

    def _exec_php_extension_dir(self):
        """
        Get the absolute path to the PHP extension directory
        :return:
        """
        stdin, stdout, stderr = self.client.exec_command("php-config --extension-dir")

        if self._exec_successful(stderr):
            return stdout.read().decode("utf-8").strip()
        else:
            raise DirectoryNotFoundException("Unable to locate the php extension directory, skipping check..")

    def _get_absolute_start_directory(self, path=None):
        """
        Get the absolute start directory
        :return: Absolute path to the start directory
        :rtype: str
        """
        path = path or self.config.start_directory

        if path.startswith("~"):
            path = path.replace("~", self._exec_home_dir())

        if path.startswith("./"):
            path = path.replace("./", self._exec_pwd())

        if not path.startswith("/"):
            path = self._exec_pwd() + "/" + path

        return path
