import asyncio

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 49152


class ChatServerProtocol(asyncio.Protocol):
    def __init__(self, server_manager):
        self.server_manager = server_manager
        self.transport = None
        self.addr = None
        self.username = None

    def connection_made(self, transport):
        peername = transport.get_extra_info("peername")
        self.addr = peername
        self.transport = transport
        self.server_manager.register_client(self)
        print(f"Client connected: {peername[0]}:{peername[1]}")

    def data_received(self, data):
        message = data.decode("utf-8").strip()
        if not message:
            return
        conn_info = f"{self.addr[0]}:{self.addr[1]}"
        if self.username is None:
            if message.startswith("__USERNAME__:") and len(message) > len("__USERNAME__:") + 1:
                username = message[len("__USERNAME__:") :]
                if 1 <= len(username) <= 15:
                    self.username = username
                    print(f"Client registered: {self.username} ({conn_info})")
                    welcome_message = f"*** {self.username} joined the chat. ***"
                    self.server_manager.broadcast(welcome_message)
                else:
                    print(f"Warning: Invalid username received from {conn_info}. Disconnecting.")
                    self.transport.close()
            return
        display_name = self.username
        display_message = f"[{display_name} {conn_info}] {message}"
        print(display_message)
        self.server_manager.broadcast(display_message)

    def connection_lost(self, exc):
        if self.addr:
            conn_info = f"{self.addr[0]}:{self.addr[1]}"
            if self.username:
                print(f"Client disconnected: {self.username} ({conn_info})")
                self.server_manager.broadcast(f"*** {self.username} left the chat. ***")
            else:
                print(f"Client disconnected: {conn_info}")
            self.server_manager.unregister_client(self)


class ChatServer:
    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT):
        self.clients = set()
        self.host = host
        self.port = port

    def register_client(self, protocol_instance):
        self.clients.add(protocol_instance)

    def unregister_client(self, protocol_instance):
        self.clients.discard(protocol_instance)

    def broadcast(self, message):
        broadcast_data = (message + "\n").encode("utf-8")
        for client_protocol in list(self.clients):
            try:
                client_protocol.transport.write(broadcast_data)
            except Exception as e:
                print(f"Warning: Failed to write data to client. {e}")

    async def run(self):
        loop = asyncio.get_running_loop()
        host, port = self.host, self.port
        print(f"Starting Chat Server on {host}:{port}")

        def protocol_factory():
            return ChatServerProtocol(self)

        server = await loop.create_server(protocol_factory, host, port)
        addr = server.sockets[0].getsockname()
        print(f"Chat Server serving on {addr[0]}:{addr[1]}")
        async with server:
            await server.serve_forever()


class ChatClientProtocol(asyncio.Protocol):
    def __init__(self, username, on_con_lost):
        self.username = username
        self.transport = None
        self.on_con_lost = on_con_lost

    def connection_made(self, transport):
        self.transport = transport
        self.transport.write(f"__USERNAME__:{self.username}\n".encode("utf-8"))
        print("--- Chat Client connected. Type /quit or /exit to leave. ---")

    def data_received(self, data):
        messages = data.decode("utf-8").splitlines()
        for message in messages:
            if message:
                print(f"\r{' ' * 80}\r{message}\n> ", end="", flush=True)

    def connection_lost(self, exc):
        print("The server closed the connection.")
        if self.on_con_lost and not self.on_con_lost.done():
            self.on_con_lost.set_result(True)

    def send_message(self, message):
        if self.transport:
            self.transport.write((message + "\n").encode("utf-8"))


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

        def client_protocol_factory():
            return ChatClientProtocol(self.username, self.on_con_lost)

        try:
            self.transport, self.protocol = await loop.create_connection(client_protocol_factory, self.host, self.port)
        except ConnectionRefusedError:
            print(f"Error: Connection refused to {self.host}:{self.port}. Is the server running?")
            return
        except OSError as e:
            print(f"Error establishing connection: {e}")
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
