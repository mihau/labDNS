from urllib.parse import urlparse
import socket


def resolve(result):
    parsed = urlparse(result)
    # if result is an ip
    return socket.gethostbyname(parsed.netloc) if parsed.netloc else result

processor = resolve
