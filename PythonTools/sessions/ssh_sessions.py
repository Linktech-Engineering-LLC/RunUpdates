# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC

"""
 Package: RunUpdates
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-04-19
 Modified: 2026-04-19
 File: PythonTools/sessions/ssh_sessions.py
 Version: 1.0.0
 Description: Description of this module
"""

import paramiko
from types import SimpleNamespace


class SSHSession:
    """
    Persistent SSH execution session.
    Executor controls lifecycle:
        session = SSHSession(...)
        session.connect()
        session.run(...)
        session.close()
    """

    def __init__(self, hostname, username, password=None, keyfile=None,
                 port=22, logger=None, sudo_password=None, timeout=30):

        self.hostname = hostname
        self.username = username
        self.password = password
        self.keyfile = keyfile
        self.port = port
        self.logger = logger
        self.sudo_password = sudo_password
        self.timeout = timeout

        self.client = None   # Not connected yet

    # ------------------------------------------------------------
    # Connection handling
    # ------------------------------------------------------------
    def connect(self):
        if self.logger:
            self.logger.debug(
                f"[SSHSession] Connecting to {self.hostname}:{self.port}"
            )

        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            self.client.connect(
                hostname=self.hostname,
                username=self.username,
                password=self.password,
                key_filename=self.keyfile,
                port=self.port,
                timeout=self.timeout,
            )

            if self.logger:
                self.logger.info(f"[SSHSession] Connected to {self.hostname}")

        except Exception as e:
            if self.logger:
                self.logger.error(f"[SSHSession] Connection failed: {e}")
            raise

    # ------------------------------------------------------------
    # Core execution
    # ------------------------------------------------------------
    def run(self, command: str, use_sudo: bool = False):
        client = self._require_client()

        if self.logger:
            mode = "sudo" if use_sudo else "ssh"
            self.logger.debug(f"[SSHSession] Executing ({mode}): {command}")

        if use_sudo:
            sudo_cmd = f"sudo -S {command}"
            stdin, stdout, stderr = client.exec_command(sudo_cmd)
            stdin.write(f"{self.sudo_password}\n")
            stdin.flush()
        else:
            stdin, stdout, stderr = client.exec_command(command)

        out = stdout.read().decode("utf-8").strip()
        err = stderr.read().decode("utf-8").strip()
        code = stdout.channel.recv_exit_status()

        result = SimpleNamespace(
            msg=out,
            code=code,
            err=err,
            stdout=out,
            stderr=err,
            returncode=code,
            as_tuple=(out, code, err),
        )

        if self.logger:
            self.logger.debug(
                f"[SSHSession] Result code={code}, stdout={out}, stderr={err}"
            )

        return result

    def _require_client(self):
        if self.client is None:
            raise RuntimeError("SSHSession client is not connected")
        return self.client

    # ------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------
    def close(self):
        if self.client:
            if self.logger:
                self.logger.debug(f"[SSHSession] Closing connection to {self.hostname}")
            self.client.close()
            self.client = None
            return True
        return False
