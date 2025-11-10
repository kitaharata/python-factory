import psutil


def check_all_memory():
    """Check all system memory status."""
    memory = psutil.virtual_memory()
    print("--- Physical Memory Status ---")
    print(f"Total: {memory.total / (1024**3):.2f} GB")
    print(f"Available: {memory.available / (1024**3):.2f} GB")
    print(f"Used: {memory.used / (1024**3):.2f} GB")
    print(f"Free: {memory.free / (1024**3):.2f} GB")
    print(f"Percentage used: {memory.percent}%")

    swap = psutil.swap_memory()
    print("\n--- Swap Memory Status ---")
    print(f"Total: {swap.total / (1024**3):.2f} GB")
    print(f"Used: {swap.used / (1024**3):.2f} GB")
    print(f"Free: {swap.free / (1024**3):.2f} GB")
    print(f"Percentage used: {swap.percent}%")
    print(f"Swapped in (cumulative): {swap.sin / (1024**2):.2f} MB")
    print(f"Swapped out (cumulative): {swap.sout / (1024**2):.2f} MB")


if __name__ == "__main__":
    check_all_memory()
