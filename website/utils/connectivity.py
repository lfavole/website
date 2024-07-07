import socket
from time import time

_offline_result = True
_offline_time = 0


def internet(host="8.8.8.8", port=53, timeout=3):
    """
    Check the Internet connectivity. Caches the result for 15 seconds.

    Host: 8.8.8.8 (google-public-dns-a.google.com)
    OpenPort: 53/tcp
    Service: domain (DNS/TCP)
    """
    global _offline_result, _offline_time
    if time() - _offline_time < 15:
        return _offline_result

    _offline_time = time()
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        ret = True
    except socket.error:
        ret = False
    _offline_result = ret
    return ret
