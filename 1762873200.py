import psutil


def check_network_connections():
    """Display current TCP/UDP network connections and associated process information."""

    print("--- Network Connections (TCP/UDP) ---")
    connections = psutil.net_connections(kind="inet")
    for conn in connections:
        pid_info = str(conn.pid) if conn.pid else "N/A"

        if conn.pid:
            try:
                p = psutil.Process(conn.pid)
                pid_info += f" ({p.name()})"
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pid_info += " (Unknown/Denied)"

        print(f"\nPID: {pid_info}")
        print(f"  Family: {conn.family.name}, Type: {conn.type.name}")
        print(f"  Status: {conn.status}")

        laddr_str = "N/A"
        if conn.laddr:
            laddr_str = f"{conn.laddr.ip}:{conn.laddr.port}"
        print(f"  Local Address: {laddr_str}")

        raddr_str = "N/A"
        if conn.raddr:
            raddr_str = f"{conn.raddr.ip}:{conn.raddr.port}"
        print(f"  Remote Address: {raddr_str}")


if __name__ == "__main__":
    check_network_connections()
