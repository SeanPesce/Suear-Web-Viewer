#!/usr/bin/env python3
# Author: Sean Pesce

import os
import platform
import socket
import sys


def ping(host, timeout=1):
    """
    Returns True if the target host sent an ICMP response within the specified timeout interval
    """
    # Protect against command injection
    if type(host) != str:
        raise TypeError(f'Non-string type for "host" argument: {type(host)}')
    # Alphabet for IP addresses and host names
    safe_alphabet = '.:0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_'
    for c in host:
        if c not in safe_alphabet:
            raise ValueError(f'Invalid character in "host" argument: "{c}"')
    host = socket.gethostbyname(host)
    # Determine argument syntax (Linux vs Windows)
    count_flag = 'c'
    dev_null = '/dev/null'
    quote_char = '\''
    wait_flag = 'w'
    if 'windows' in platform.system().lower():
        count_flag = 'n'
        dev_null = 'NUL'
        quote_char = '"'
    if 'darwin' in platform.system().lower():
        wait_flag = 'W'

    cmd = f'ping -{count_flag} 1 -{wait_flag} {int(timeout)} {quote_char}{host}{quote_char} 2>&1 > {dev_null}'
    retcode = os.system(cmd)
    return retcode == 0
