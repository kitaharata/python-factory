import datetime
import socket
import ssl
import sys
import urllib.parse


def format_name(name_list):
    """Formats SSL subject/issuer name lists into a readable string."""
    formatted_parts = []
    for item in name_list:
        for entry in item:
            if len(entry) == 2:
                formatted_parts.append(f"{entry[0]}={entry[1]}")
    return ", ".join(formatted_parts)


def parse_ssl_time(time_str):
    """Parses a time string found in SSL certificates into a datetime object."""
    time_str_no_tz = time_str.replace(" GMT", "")
    return datetime.datetime.strptime(time_str_no_tz, "%b %d %H:%M:%S %Y")


def get_certificate_details(origin):
    """Retrieve and display SSL/TLS certificate details for the specified host."""
    if not origin.startswith(("http://", "https://")):
        origin = "https://" + origin
    parsed_url = urllib.parse.urlparse(origin)
    hostname = parsed_url.hostname
    port = parsed_url.port
    if hostname is None:
        print(f"Error: Invalid origin format '{origin}'. Could not extract hostname.")
        return
    if port is None:
        port = 443
    try:
        context = ssl.create_default_context()
        with socket.create_connection((hostname, port)) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                print(f"--- Certificate Details ({hostname}:{port}) ---")
                print(f"Subject: {format_name(cert['subject'])}")
                print(f"Issuer: {format_name(cert['issuer'])}")
                not_before = parse_ssl_time(cert["notBefore"])
                not_after = parse_ssl_time(cert["notAfter"])
                print(f"Valid From: {not_before}")
                print(f"Valid Until: {not_after}")
                time_remaining = not_after - datetime.datetime.now()
                print(f"Days Remaining: {time_remaining.days} days")
                if "subjectAltName" in cert:
                    san_list = [f"{k}: {v}" for k, v in cert["subjectAltName"]]
                    print("Subject Alternative Names (SAN):")
                    for san in san_list:
                        print(f"  - {san}")
    except ssl.SSLError as e:
        print(f"Error: An SSL/TLS connection or certificate processing error occurred: {e}")
    except socket.gaierror:
        print(f"Error: Could not resolve hostname '{hostname}'.")
    except socket.error as e:
        print(f"Error: A socket connection error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python 1763046000.py <origin>")
        print("Example 1 (default port 443): python 1763046000.py https://google.com")
        print("Example 2 (specific port): python 1763046000.py google.com:8443")
        sys.exit(1)
    origin = sys.argv[1]
    get_certificate_details(origin)
