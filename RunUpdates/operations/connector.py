# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC

"""
 Package: RunUpdates
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-04-18
 Modified: 2026-04-18
 File: RunUpdates/operations/connector.py
 Version: 1.0.0
 Description: Determines how to connect to a host (local or remote)
              and returns a session object capable of executing commands.
"""

# System Libraries
import socket
import subprocess
import paramiko   # You already use this in other tools; if not, we can wrap it
from typing import Optional, List


DEFAULT_SSH_PORT = 22


# ----------------------------------------------------------------------
# Session Abstractions
# ----------------------------------------------------------------------
class LocalSession:
    """
    Executes commands locally using subprocess.
    If use_sudo=True, prefixes commands with sudo.
    """

    def __init__(self, use_sudo: bool = False, logger=None):
        self.use_sudo = use_sudo
        self.logger = logger

    def run(self, command: str) -> tuple[int, str, str]:
        if self.use_sudo:
            command = f"sudo {command}"

        if self.logger:
            self.logger.debug(f"[LOCAL] Executing: {command}")

        proc = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        out, err = proc.communicate()
        return proc.returncode, out, err


class SSHSession:
    """
    Executes commands on a remote host via SSH.

    Supports:
      - key-based auth (keyfile)
      - password auth
    """

    def __init__(
        self,
        hostname: str,
        port: int,
        username: str,
        keyfile: Optional[str] = None,
        password: Optional[str] = None,
        logger=None,
    ):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.keyfile = keyfile
        self.password = password
        self.logger = logger
        self.client: Optional[paramiko.SSHClient] = None

    def connect(self):
        if self.logger:
            self.logger.debug(
                f"[SSH] Connecting to {self.hostname}:{self.port} as {self.username} "
                f"(keyfile={bool(self.keyfile)}, password={bool(self.password)})"
            )

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        connect_kwargs: dict = {
            "hostname": self.hostname,
            "port": self.port,
            "username": self.username,
            "timeout": 5,
        }

        if self.keyfile:
            connect_kwargs["key_filename"] = self.keyfile

        if self.password:
            connect_kwargs["password"] = self.password

        client.connect(**connect_kwargs)
        self.client = client

    def run(self, command: str) -> tuple[int, str, str]:
        if not self.client:
            raise RuntimeError("SSHSession not connected")

        if self.logger:
            self.logger.debug(f"[SSH] Executing on {self.hostname}: {command}")

        stdin, stdout, stderr = self.client.exec_command(command)
        exit_code = stdout.channel.recv_exit_status()

        out = stdout.read()
        err = stderr.read()

        # Decode bytes → str
        out_str = out.decode("utf-8", errors="replace") if isinstance(out, bytes) else str(out)
        err_str = err.decode("utf-8", errors="replace") if isinstance(err, bytes) else str(err)

        return exit_code, out_str, err_str

    def close(self):
        if self.client:
            self.client.close()
            self.client = None


# ----------------------------------------------------------------------
# HostConnector
# ----------------------------------------------------------------------
class HostConnector:
    """
    Determines how to connect to a host:
      - Local host → LocalSession (sudo)
      - Remote host → SSHSession (keyfile first, password fallback)
      - Remote host → address iteration until reachable
    """

    def __init__(self, secrets: dict, logger=None):
        """
        :param secrets: Vault-loaded credentials
        :param logger: Optional logger
        """
        self.secrets = secrets or {}
        self.logger = logger

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def connect(self, host: dict):
        """
        Returns a session object (LocalSession or SSHSession).

        Host dict fields (from InventoryProcessor.flatten()):
          - name
          - address
          - address_list
          - port
        """

        # 1. Local host detection
        if self._is_localhost(host["name"], host.get("address")):
            if self.logger:
                self.logger.debug(f"Host {host['name']} is local; using LocalSession")
            return LocalSession(use_sudo=True, logger=self.logger)

        # 2. Remote host → iterate address list
        addresses: List[str] = host.get("address_list") or [host["address"]]
        port = host.get("port") or DEFAULT_SSH_PORT

        username = self.secrets.get("sudo_user")
        keyfile = self.secrets.get("keyfile")
        password = self.secrets.get("sudo_pass")

        if not username:
            raise RuntimeError("Vault missing required field: sudo_user")

        for addr in addresses:
            # Try key-based auth first
            if keyfile:
                try:
                    if self.logger:
                        self.logger.debug(
                            f"[SSH] Trying keyfile auth for {addr}:{port} as {username}"
                        )
                    session = SSHSession(
                        hostname=addr,
                        port=port,
                        username=username,
                        keyfile=keyfile,
                        password=None,
                        logger=self.logger,
                    )
                    session.connect()
                    return session
                except Exception as e:
                    if self.logger:
                        self.logger.warning(
                            f"Key-based SSH failed for {addr}:{port} → {e}"
                        )

            # Fallback to password auth
            if password:
                try:
                    if self.logger:
                        self.logger.debug(
                            f"[SSH] Trying password auth for {addr}:{port} as {username}"
                        )
                    session = SSHSession(
                        hostname=addr,
                        port=port,
                        username=username,
                        keyfile=None,
                        password=password,
                        logger=self.logger,
                    )
                    session.connect()
                    return session
                except Exception as e:
                    if self.logger:
                        self.logger.warning(
                            f"Password SSH failed for {addr}:{port} → {e}"
                        )

        # If we get here, all addresses failed
        raise RuntimeError(
            f"Unable to connect to host {host['name']} using any address: {addresses}"
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _is_localhost(self, hostname: str, address: Optional[str]) -> bool:
        """
        Determines if the host is the local machine.
        """

        local_names = {
            socket.gethostname(),
            socket.getfqdn(),
            "localhost",
            "127.0.0.1",
        }

        if hostname in local_names:
            return True

        if address in local_names:
            return True

        return False
