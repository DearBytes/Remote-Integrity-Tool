#!/usr/bin/env python
# Copyright (C) 2017 DearBytes B.V. - All Rights Reserved
from datetime import datetime
from smtplib import SMTP
from email.mime.text import MIMEText

from dear.remote_integrity.syslog_client import Syslog

from telegram.ext import Updater


class Logger:

    def __init__(self, config):
        """
        Logging constructor
        :param config: Configuration
        :type config: config.Config
        """
        self.config = config

    def dispatch_syslog(self, events):
        """
        Dispatch a syslog
        :param events: List of events that were found
        :type events: dict[models.Event]
        :return: None
        """
        if not any(events):
            return print("[-] No events detected, skipping syslog.")

        if not self.config.logging_syslog_host:
            return print("[-] No syslog host configured, skipping syslog.")

        log = Syslog(host=self.config.logging_syslog_host)
        for event in events: log.warn(event.description)

        print("[+] Remote syslog sent to server: {}".format(self.config.logging_syslog_host))

    def dispatch_telegram_msg(self, events):
        """
        Dispatch a telegram push message
        :param events: List of events that were found
        :type events: dict[models.Event]
        :return: None
        """
        if not any(events):
            return print("[-] No events detected, skipping telegram push notification.")

        if not self.config.telegram_api_token:
            return print("[-] No telegram api token configured, skipping push notification.")

        if not self.config.telegram_api_chat_id:
            return print("[-] No telegram chat id configured, skipping push notification.")

        bot = Updater(token=self.config.telegram_api_token).bot
        bot.sendMessage(chat_id=self.config.telegram_api_chat_id, text=self._get_email_body_from_events(events))

    def dispatch_events_mail(self, events):
        """
        Dispatch an email information about all found events
        :param events: List of events that were found
        :type events: dict[models.Event]
        :return: None
        """
        if not any(events):
            return print("[-] No events detected, skipping email.")

        if not any(self.config.email_recipients):
            return print("[-] No email recipients configured, skipping email.")

        if not self.config.email_smtp_host:
            return print("[-] No SMTP host configured, skipping email.")

        email_subject = "Suspicious activity detected ({} incident{})".format(len(events), "s" if len(events) > 1 else "")
        email_from = "DearBytes Remote Integrity Tool <{}>".format(self.config.email_noreply_address)
        email_body = self._get_email_body_from_events(events)

        email = MIMEText(email_body)
        email["Subject"] = email_subject
        email["From"] = email_from
        email["To"] = self.config.email_recipients

        smtp = SMTP(host=self.config.email_smtp_host)

        if self.config.smtp_auth_enabled():
            smtp.login(user=self.config.email_smtp_user, password=self.config.email_smtp_pass)

        smtp.sendmail(email_from, self.config.email_recipients, email.as_string())
        smtp.quit()

        print("[+] Email notifications sent to: {}".format(self.config.email_recipients))

    def _get_email_body_from_events(self, events):
        """
        Get the email body for the event that were detected
        :param events: Events that occurred
        :type events: dict[models.Event]
        :return: Formatted email body
        :rtype: str
        """
        email  = "Dear Administrator,\n"
        email += "\n"
        email += "The DearBytes remote integrity tool has detected suspicious activity on your server.\n"
        email += "For your own protection we ask you to review the following incident{}:\n".format("s" if len(events) > 1 else "")
        email += "\n"
        email += "\tServer: '{name}' ({ip}:{port})\n".format(name=self.config.server_name, ip=self.config.server_address, port=self.config.server_port)
        email += "\tTimestamp: {timestamp}\n".format(timestamp=datetime.now().strftime("%B %d, %Y on %H:%M:%S"))
        email += "\tNumber of incidents: {incidents}\n".format(incidents=len(events))
        email += "\n"
        email += "{incidents}\n".format(incidents=self._get_email_body_text_formatted(events))
        email += "\n"
        email += "Kind regards,\n"
        email += "DearBytes"
        return email

    def _get_email_body_text_formatted(self, events):
        """
        Format a list of events into an email formatted string
        :param events: Events that occurred
        :type events: dict[models.Event]
        :return: Formatted list of events
        :rtype: str
        """
        return "\n".join(["\t" + e.description for e in events])
