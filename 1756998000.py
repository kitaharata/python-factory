import socket
import struct
import sys
import urllib.parse


def ip_to_decimal(ip_address):
    """Converts an IP address string (IPv4 or IPv6) to its decimal representation."""
    if ip_address == "::1" or ip_address == "0:0:0:0:0:0:0:1":
        ip_address = "127.0.0.1"
    try:
        packed_ip = socket.inet_aton(ip_address)
        decimal_ip = struct.unpack("!I", packed_ip)[0]
        return str(decimal_ip)
    except socket.error:
        try:
            packed_ip_v6 = socket.inet_pton(socket.AF_INET6, ip_address)
            if packed_ip_v6[0:12] == b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff":
                ipv4_bytes = packed_ip_v6[12:]
                decimal_ip = struct.unpack("!I", ipv4_bytes)[0]
                return str(decimal_ip)
            else:
                decimal_ip = int.from_bytes(packed_ip_v6, byteorder="big")
                return str(decimal_ip)
        except socket.error:
            return None


def convert_url_ip_to_decimal(url):
    """Converts IPv4 addresses in a URL to their decimal representation and returns the new URL."""
    parsed_url = urllib.parse.urlparse(url)
    if not parsed_url.netloc:
        return f"Error: Invalid URL format or host not found: {url}"
    host = parsed_url.hostname
    port = parsed_url.port
    if not host:
        return f"Error: Hostname not found: {url}"
    decimal_host = ip_to_decimal(host)
    if decimal_host is None:
        return f"Error: The specified host is not an IPv4 address: {host}"
    new_netloc_parts = [decimal_host]
    if port is not None:
        new_netloc_parts.append(str(port))
    new_netloc = ":".join(new_netloc_parts)
    new_parsed_url = parsed_url._replace(netloc=new_netloc)
    return new_parsed_url.geturl()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python <script_name>.py <URL>")
        print("Example: python 1756998000.py http://127.0.0.1:8080/")
        sys.exit(1)
    input_url = sys.argv[1]
    result_url = convert_url_ip_to_decimal(input_url)
    print(result_url)
