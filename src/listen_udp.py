"""
This is a small example script on how to listen to UDP data.
"""

import socket
from src.utils import Config

cfg = Config()


def main():
    # Create UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Bind to all interfaces on the specified port
    host = cfg.get("udp.host", "127.0.0.1")
    port = cfg.get("udp.port", 9001)
    sock.bind((host, port))

    print(f"Listening for UDP packets on {host}:{port}...")

    try:
        while True:
            data, addr = sock.recvfrom(8192)
            print(f"Received from {addr}: {data.decode('utf-8', errors='replace')}")
    except KeyboardInterrupt:
        pass
    finally:
        sock.close()
        print("Exiting...")


if __name__ == "__main__":
    main()
