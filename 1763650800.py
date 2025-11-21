import asyncio

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 49152


class ChatServerDatagramProtocol(asyncio.DatagramProtocol):
    def __init__(self, server_manager):
        self.server_manager = server_manager
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport
        self.server_manager.set_transport(transport)
        print("UDP Server transport ready.")

    def datagram_received(self, data, addr):
        self.server_manager.handle_datagram(data, addr)

    def error_received(self, exc):
        print(f"UDP server error received: {exc}")


class ChatServer:
    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT):
        self.clients = {}
        self.transport = None
        self.host = host
        self.port = port

    def set_transport(self, transport):
        self.transport = transport

    def register_client(self, addr, username):
        if addr in self.clients:
            return False
        self.clients[addr] = username
        return True

    def unregister_client(self, addr):
        if addr in self.clients:
            username = self.clients.pop(addr)
            return username
        return None

    def broadcast(self, message):
        if not self.transport:
            return
        broadcast_data = (message + "\n").encode("utf-8")
        for addr in list(self.clients.keys()):
            try:
                self.transport.sendto(broadcast_data, addr)
            except Exception as e:
                print(f"Warning: Failed to send data to client {addr}. {e}")

    def handle_datagram(self, data, addr):
        message = data.decode("utf-8").strip()
        if not message:
            return
        conn_info = f"{addr[0]}:{addr[1]}"
        username = self.clients.get(addr)
        if username is None:
            if message.startswith("__USERNAME__:") and len(message) > len("__USERNAME__:") + 1:
                new_username = message[len("__USERNAME__:") :].strip()
                if 1 <= len(new_username) <= 15:
                    if self.register_client(addr, new_username):
                        print(f"Client registered: {new_username} ({conn_info})")
                        welcome_message = f"*** {new_username} joined the chat. ***"
                        self.broadcast(welcome_message)
                else:
                    print(f"Warning: Invalid username received from {conn_info}. Ignoring.")
            return
        if message.lower() in ("/quit", "/exit"):
            username_left = self.unregister_client(addr)
            if username_left:
                print(f"Client quit: {username_left} ({conn_info})")
                self.broadcast(f"*** {username_left} left the chat. ***")
            return
        display_name = username
        display_message = f"[{display_name} {conn_info}] {message}"
        print(display_message)
        self.broadcast(display_message)

    async def run(self):
        loop = asyncio.get_running_loop()
        host, port = self.host, self.port
        print(f"Starting Chat Server UDP on {host}:{port}")

        def protocol_factory():
            return ChatServerDatagramProtocol(self)

        self.transport, protocol = await loop.create_datagram_endpoint(protocol_factory, local_addr=(host, port))
        addr = self.transport.get_extra_info("sockname")
        print(f"Chat Server serving on {addr[0]}:{addr[1]}")
        try:
            await asyncio.Future()
        finally:
            if self.transport:
                self.transport.close()


class ChatClientDatagramProtocol(asyncio.DatagramProtocol):
    def __init__(self, username, server_addr, on_con_lost):
        self.username = username
        self.transport = None
        self.server_addr = server_addr
        self.on_con_lost = on_con_lost

    def connection_made(self, transport):
        self.transport = transport
        self.transport.sendto(f"__USERNAME__:{self.username}\n".encode("utf-8"), self.server_addr)
        print("--- Chat Client connected (UDP). Type /quit or /exit to leave. ---")

    def datagram_received(self, data, addr):
        messages = data.decode("utf-8").splitlines()
        for message in messages:
            if message:
                print(f"\r{' ' * 80}\r{message}\n> ", end="", flush=True)

    def error_received(self, exc):
        print(f"Error received: {exc}")

    def connection_lost(self, exc):
        print("Client transport closed.")
        if self.on_con_lost and not self.on_con_lost.done():
            self.on_con_lost.set_result(True)

    def send_message(self, message):
        if self.transport:
            self.transport.sendto((message + "\n").encode("utf-8"), self.server_addr)


class ChatClient:
    def __init__(self, host, port, username):
        self.host = host
        self.port = port
        self.username = username
        self.protocol = None
        self.transport = None
        self.on_con_lost = None

    async def _input_handler(self):
        loop = asyncio.get_running_loop()

        def get_input():
            try:
                return input("> ")
            except EOFError:
                return None

        while True:
            try:
                message = await loop.run_in_executor(None, get_input)
                if message is None:
                    break
                message = message.strip()
                if message.lower() in ("/quit", "/exit"):
                    print("Exiting chat client.")
                    break
                if message and self.protocol:
                    self.protocol.send_message(message)
            except KeyboardInterrupt:
                print("\nInterrupted.")
                break

    async def run(self):
        loop = asyncio.get_running_loop()
        self.on_con_lost = loop.create_future()
        server_addr = (self.host, self.port)

        def client_protocol_factory():
            return ChatClientDatagramProtocol(self.username, server_addr, self.on_con_lost)

        try:
            self.transport, self.protocol = await loop.create_datagram_endpoint(
                client_protocol_factory, remote_addr=server_addr
            )
        except OSError as e:
            print(f"Error creating UDP socket: {e}")
            return
        input_task = loop.create_task(self._input_handler())
        done, pending = await asyncio.wait(
            [input_task, self.on_con_lost],
            return_when=asyncio.FIRST_COMPLETED,
        )
        if self.transport:
            self.transport.close()
        for task in pending:
            if not task.done():
                task.cancel()
        if pending:
            await asyncio.gather(*pending, return_exceptions=True)


async def main():
    print("Socket Chat")
    mode = ""
    while mode not in ("c", "s"):
        try:
            mode = input("Select mode (C=Client / S=Server): ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("Configuration interrupted. Exiting.")
            return
    is_server = mode == "s"
    username = ""
    if not is_server:
        while not (1 <= len(username) <= 15):
            try:
                username = input("Enter your name (1-15 characters): ").strip()
                if not (1 <= len(username) <= 15):
                    print("Error: Name must be between 1 and 15 characters long.")
            except (EOFError, KeyboardInterrupt):
                print("Configuration interrupted. Exiting.")
                return
    host = DEFAULT_HOST
    port = DEFAULT_PORT
    while True:
        try:
            prompt_role = "server listen" if is_server else "server target"
            default_addr = f"{DEFAULT_HOST}:{DEFAULT_PORT}"
            prompt = f"Enter {prompt_role} address (e.g., 127.0.0.1:{DEFAULT_PORT}) [{default_addr}]: "
            user_input = input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            print("Configuration interrupted. Exiting.")
            return
        current_host = DEFAULT_HOST
        current_port = DEFAULT_PORT
        if user_input:
            parts = user_input.rsplit(":", 1)
            if len(parts) == 2:
                raw_host, raw_port = parts
                if raw_host.startswith("[") and raw_host.endswith("]"):
                    current_host = raw_host.strip("[]")
                else:
                    current_host = raw_host
                if not current_host:
                    current_host = DEFAULT_HOST
                try:
                    current_port = int(raw_port)
                    if not (DEFAULT_PORT <= current_port <= 65535):
                        print(f"Error: Port number is out of the valid range ({DEFAULT_PORT}-65535).")
                        continue
                except ValueError:
                    print("Error: Invalid port number.")
                    continue
            elif len(parts) == 1:
                current_host = parts[0]
        if not is_server and current_host == "0.0.0.0":
            print("Error: 0.0.0.0 is not allowed as a client target IP.")
            continue
        host = current_host
        port = current_port
        break
    if is_server:
        print(f"Starting server on {host}:{port}")
        server = ChatServer(host, port)
        await server.run()
    else:
        print(f"Connecting to server at {host}:{port} as user {username}")
        client = ChatClient(host, port, username)
        await client.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    except Exception:
        pass
