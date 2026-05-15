# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC

"""
 Package: RunUpdates
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-04-18
 Modified: 2026-04-28
 File: RunUpdates/operations/connector.py
 Version: 1.0.0
 Description: Determines how to connect to a host (local or remote)
              and returns a session object capable of executing commands.
"""

import socket
import time
from dataclasses import dataclass
from typing import Optional, List
from PythonTools.sessions.ssh_sessions import SSHSession

DEFAULT_SSH_PORT = 22


@dataclass
class SSHConnectionInfo:
    hostname: str
    port: int
    username: str
    keyfile: Optional[str]
    password: Optional[str]
    logger: Optional[object] = None


class HostConnector:
    """
    Determines how to connect to a host:
      - Local host → "local"
      - Remote host → SSHConnectionInfo
    """

    def __init__(self, secrets: dict, logger=None):
        self.secrets = secrets or {}
        self.logger = logger

    def connect(self, host: dict):
        """
        Returns:
            - "local"
            - SSHSession(...)
            - False (if unreachable)
        """

        username = self.secrets["sudo_user"]
        password = self.secrets["sudo_pass"]
        keyfile = self.secrets["keyfile"]

        # 1. Local host detection
        if self._is_localhost(host["name"], host.get("address")):
            if self.logger:
                self.logger.debug(f"[CONNECT] Host {host['name']} is local")
            return "local"

        # 2. Remote host → build candidate list
        candidates = [host["name"]] + host["address"]
        port = host.get("port") or DEFAULT_SSH_PORT

        # 3. Port probe
        reachable = None
        for addr in candidates:
            if self.port_open(addr, port):
                reachable = addr
                break

        if not reachable:
            if self.logger:
                self.logger.error(
                    f"[CONNECT] No reachable SSH port for host {host['name']} "
                    f"on any candidate: {candidates}"
                )
            return False

        if self.logger:
            self.logger.debug(
                f"[CONNECT] Using reachable endpoint {reachable}:{port} "
                f"for host {host['name']}"
            )

        # 4. Build SSHSession (NOT SSHConnectionInfo)
        session = SSHSession(
            hostname=reachable,
            port=port,
            username=username,
            keyfile=keyfile,
            password=None if keyfile else password,
            logger=self.logger,
        )

        # 5. Connect
        session.connect()

        return session

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _is_localhost(self, hostname: str, addresses: list[str] | None) -> bool:
        local_names = {
            socket.gethostname(),
            socket.getfqdn(),
            "localhost",
        }

        if hostname in local_names:
            return True

        if not addresses:
            return False

        local_ips = {"127.0.0.1"}
        try:
            local_ips.update(socket.gethostbyname_ex(socket.gethostname())[2])
        except Exception:
            pass

        return any(addr in local_ips for addr in addresses)

    def port_open(self, host: str, port: int, timeout: float = 1.0) -> bool:
        try:
            start = time.time()
            with socket.create_connection((host, port), timeout=timeout):
                duration = (time.time() - start) * 1000
                if self.logger:
                    self.logger.debug(
                        f"[PORT] {host}:{port} reachable ({duration:.1f} ms)"
                    )
                return True

        except OSError as e:
            if self.logger:
                self.logger.debug(
                    f"[PORT] {host}:{port} unreachable → {e}"
                )
            return False
