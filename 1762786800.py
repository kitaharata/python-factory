import psutil


def check_all_network():
    """Check all system network status, including I/O, addresses, and connections."""

    print("--- Network Interface IO Status (MB/Packets/Errors) ---")
    net_io = psutil.net_io_counters(pernic=True)
    for interface, stats in net_io.items():
        print(f"\nInterface: {interface}")
        print(f"  Bytes Sent: {stats.bytes_sent / (1024**2):.2f} MB")
        print(f"  Bytes Received: {stats.bytes_recv / (1024**2):.2f} MB")
        print(f"  Packets Sent: {stats.packets_sent}")
        print(f"  Packets Received: {stats.packets_recv}")
        print(f"  Errors In: {stats.errin}")
        print(f"  Errors Out: {stats.errout}")
        print(f"  Drops In: {stats.dropin}")
        print(f"  Drops Out: {stats.dropout}")

    print("\n--- Network Interface Addresses ---")
    net_addrs = psutil.net_if_addrs()
    for interface, addrs in net_addrs.items():
        print(f"\nInterface: {interface}")
        for addr in addrs:
            print(f"  Family: {addr.family.name}")
            if addr.address:
                print(f"  Address: {addr.address}")
            if addr.netmask:
                print(f"  Netmask: {addr.netmask}")
            if addr.broadcast:
                print(f"  Broadcast: {addr.broadcast}")
            if addr.ptp:
                print(f"  P2P: {addr.ptp}")

    print("\n--- Network Interface Statistics ---")
    net_stats = psutil.net_if_stats()
    for interface, stats in net_stats.items():
        print(f"\nInterface: {interface}")
        print(f"  Is Up: {stats.isup}")
        print(f"  Duplex: {stats.duplex.name}")
        print(f"  Speed: {stats.speed} MB")
        print(f"  MTU: {stats.mtu}")
        if stats.flags:
            print(f"  Flags: {stats.flags}")


if __name__ == "__main__":
    check_all_network()
