# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
Package: PythonTools
Author: Leon McClatchey
Company: Linktech Engineering LLC
Created: 2025-12-31
Modified: 2026-02-10
File: PythonTools/net_tools.py
Description: Describe the purpose of this file
"""
# System Libraries
import os
import subprocess
import shlex
from typing import Optional
from types import SimpleNamespace
# Project Libraries

# Default no-op logger
class _NullLogger:
    def debug(self, *a, **k): pass
    def info(self, *a, **k): pass
    def warning(self, *a, **k): pass
    def error(self, *a, **k): pass
    def command_start(self, *a, **k): pass
    def command_end(self, *a, **k): pass
    def command_error(self, *a, **k): pass

logger = _NullLogger()

def set_logger(external_logger):
    global logger
    logger = external_logger


# Runs a command on the local machine
def local_command(cmd: str, raise_on_error: bool = False) -> tuple[str, int, str]:
    try:
        logger.command_start(cmd)
        proc = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        logger.command_end(cmd, proc.returncode)
        if proc.returncode != 0:
            logger.command_error("local_command", RuntimeError(proc.stderr.strip()))
            if raise_on_error:
                raise RuntimeError(proc.stderr.strip())
        return proc.stdout.strip(), proc.returncode, proc.stderr.strip()

    except Exception as error:
        logger.command_error("local_command", error)
        if raise_on_error:
            raise RuntimeError(str(error))
        return "", 1, str(error)

def run_with_error_handling(cmd: str, sudo_password: Optional[str], raise_on_error: bool = True, **kwargs):
    """
    Wrapper around sudo_run that always passes raise_on_error explicitly.
    Ensures audit-friendly error handling across all modules.
    """
    return sudo_run(cmd, sudo_password=sudo_password, raise_on_error=raise_on_error, **kwargs)


# Sudo Command Function
def sudo_run(cmd: str,sudo_password: Optional[str], raise_on_error: bool = False) -> SimpleNamespace:
    """
    Run a command with sudo if password is provided,
    otherwise fall back to local_command (root mode).

    Parameters
    ----------
    command : str
        The shell command to run (without 'sudo').
    sudo_password : str
        Sudo password obtained from vault/secrets.

    Returns
    -------
    tuple
        (out, code, err)
        out  : str  -> stdout from the command
        code : int  -> return code (0 = success)
        err  : str  -> stderr from the command
    """
    if sudo_password is None:
        # Root mode already validated upstream
        out, code, err = local_command(cmd)
        return SimpleNamespace(
            msg=out,
            code=code,
            err=err,
            stdout=out,
            stderr=err,
            returncode=code,
            as_tuple=(out, code, err)
        )
    """
    Run a command safely under sudo, handling quoting and logging.
    Accepts either a string or a list.
    """
    cmd_list = ["sudo", "-S"]
    if isinstance(cmd, str):
        # If the command contains shell operators, wrap it
        if any(op in cmd for op in ["&&", "||", "|", ";", ">", "<"]):
            raw_cmd = cmd
            args = ["sh", "-c", cmd]
        else:
            raw_cmd = cmd
            args = shlex.split(cmd)
    elif isinstance(cmd, list):
        raw_cmd = " ".join(cmd)
        args = cmd
    else:
        raise TypeError("cmd must be str or list")
    try:
        logger.command_start(f"sudo_run raw: {raw_cmd}, sudo_run args: {args}")
        cmd_list.extend(args)
        result = subprocess.run(
            cmd_list,
            capture_output=True,
            text=True,
            input=f"{sudo_password}\n",  # feed password to stdin
            check=True
        )
        result_obj = SimpleNamespace(
            msg=result.stdout,
            code=result.returncode,
            err=result.stderr,
            stdout=result.stdout,
            stderr=result.stderr,
            returncode=result.returncode,
            as_tuple=(result.stdout, result.returncode, result.stderr)
        )
    except subprocess.CalledProcessError as e:
        result_obj = SimpleNamespace(
            msg=e.stdout,
            code=e.returncode,
            err=e.stderr,
            stdout=e.stdout,
            stderr=e.stderr,
            returncode=e.returncode,
            as_tuple=(e.stdout, e.returncode, e.stderr)
        )
    finally:
        # logging, cleanup, lifecycle markers
        logger.command_end("sudo_run finished", result_obj.code)
    return result_obj
