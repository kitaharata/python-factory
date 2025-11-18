import asyncio
import socket
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext, simpledialog

TCP_PORT = 49152
UDP_PORT = 49153
BUFFER_SIZE = 4096
TIMEOUT = 0.1


class ChatClient(tk.Tk):
    """A LAN chat client application built with Tkinter."""

    def __init__(self, loop):
        """Initializes the ChatClient application and sets up connections."""
        super().__init__()
        self.loop = loop
        self.title("LAN Chat Client")
        self.geometry("600x450")
        self.nickname = simpledialog.askstring("Nickname", "Enter your nickname:", parent=self)
        if not self.nickname:
            self.nickname = "Guest"
        self.server_ip = simpledialog.askstring(
            "Server IP",
            "Enter Server IP (127.0.0.1 for local, 192.168.x.x for LAN):",
            parent=self,
            initialvalue="127.0.0.1",
        )
        if not self.server_ip:
            messagebox.showerror("Error", "Server IP is required.")
            self.quit()
            return
        self.tcp_reader = None
        self.tcp_writer = None
        self.udp_socket = None
        self.listen_task = None
        self.running = True
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.setup_gui()

    def setup_gui(self):
        """Sets up the graphical user interface elements."""
        self.chat_display = scrolledtext.ScrolledText(self, state="disabled", wrap=tk.WORD)
        self.chat_display.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        input_frame = tk.Frame(self)
        input_frame.pack(padx=10, pady=5, fill=tk.X)
        self.msg_input = tk.Entry(input_frame, width=50)
        self.msg_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.msg_input.bind("<Return>", self.send_message)
        self.send_button = tk.Button(input_frame, text="Send", command=self.send_message)
        self.send_button.pack(side=tk.LEFT)
        self.mode_var = tk.StringVar(value="TCP")
        tcp_radio = tk.Radiobutton(input_frame, text="TCP", variable=self.mode_var, value="TCP")
        udp_radio = tk.Radiobutton(input_frame, text="UDP Broadcast", variable=self.mode_var, value="UDP")
        tcp_radio.pack(side=tk.LEFT, padx=5)
        udp_radio.pack(side=tk.LEFT)

    def display_message(self, message):
        """Displays a message in the chat window and scrolls to the end."""
        self.chat_display.config(state="normal")
        self.chat_display.insert(tk.END, message + "\n")
        self.chat_display.config(state="disabled")
        self.chat_display.yview(tk.END)

    async def connect_and_start(self):
        """Establishes TCP and UDP connections and starts the network tasks."""
        self.display_message(f"--- Attempting TCP connection to {self.server_ip}:{TCP_PORT} ---")
        try:
            self.tcp_reader, self.tcp_writer = await asyncio.open_connection(self.server_ip, TCP_PORT)
            self.display_message("--- TCP connected. ---")

            self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            try:
                self.udp_socket.bind(("", UDP_PORT))
                self.udp_socket.setblocking(False)

                self.loop.add_reader(self.udp_socket.fileno(), self._handle_udp_receive)

            except OSError as e:
                self.display_message(f"Error: Could not bind UDP socket ({e}). UDP disabled.")
                self.udp_socket = None

            if self.tcp_writer:
                self.tcp_writer.write(f"NICK:{self.nickname}".encode("utf-8"))
                await self.tcp_writer.drain()

            self.listen_task = self.loop.create_task(self.network_loop())

        except ConnectionRefusedError:
            self.display_message("Connection Error: Server refused connection.")
            self.after(
                0, lambda: messagebox.showerror("Error", "Server refused connection. Make sure the server is running.")
            )
            self.after(0, lambda: self.on_closing(silent=True))
        except Exception as e:
            self.display_message(f"Connection Error: {e}")
            self.after(0, lambda current_e=e: messagebox.showerror("Error", f"Failed to connect: {current_e}"))
            self.after(0, lambda: self.on_closing(silent=True))

    def _handle_udp_receive(self):
        """Handles synchronous UDP data reception triggered by asyncio loop."""
        if self.udp_socket:
            try:
                data, addr = self.udp_socket.recvfrom(BUFFER_SIZE)
                if data:
                    msg = data.decode("utf-8")
                    self.after(0, lambda m=msg: self.display_message(f"[UDP from {addr[0]}] {m}"))
            except BlockingIOError:
                pass
            except Exception as e:
                if self.running:
                    print(f"Client UDP Receive Error: {e}")

    async def _send_tcp_message(self, full_message):
        """Asynchronously sends a TCP message."""
        try:
            if self.tcp_writer:
                self.tcp_writer.write(full_message.encode("utf-8"))
                await self.tcp_writer.drain()
                self.after(0, lambda: self.display_message(f"(TCP Sent) {full_message}"))
            else:
                self.after(0, lambda: self.display_message("Error: TCP connection not established."))
        except Exception as e:
            print(f"Async Send Error: {e}")
            self.after(0, self.handle_disconnect)

    def send_message(self, event=None):
        """Handles sending messages via the selected protocol (TCP or UDP)."""
        message = self.msg_input.get().strip()
        if not message:
            return
        mode = self.mode_var.get()
        full_message = f"[{self.nickname}]: {message}"
        self.msg_input.delete(0, tk.END)

        if mode == "TCP":
            self.loop.create_task(self._send_tcp_message(full_message))
        elif mode == "UDP" and self.udp_socket:
            try:
                self.udp_socket.sendto(f"(UDP Broadcast) {full_message}".encode("utf-8"), ("255.255.255.255", UDP_PORT))
            except Exception as e:
                self.display_message(f"Send Error (UDP): {e}")
        else:
            self.display_message("Error: Socket not ready or invalid mode selected.")

    async def network_loop(self):
        """Runs in an asyncio task to monitor TCP reader stream."""
        if not self.tcp_reader:
            self.after(0, lambda: self.display_message("TCP stream not available. Networking task exiting."))
            return

        while self.running:
            try:
                data = await self.tcp_reader.read(BUFFER_SIZE)
                if data:
                    msg = data.decode("utf-8")
                    self.after(0, lambda m=msg: self.display_message(f"[TCP] {m}"))
                else:
                    self.after(0, self.handle_disconnect)
                    break
            except ConnectionResetError:
                self.after(0, self.handle_disconnect)
                break
            except asyncio.CancelledError:
                print("Client network loop cancelled.")
                break
            except Exception as e:
                if self.running:
                    print(f"Client Network Loop Error: {e}")
                    self.after(0, self.handle_disconnect)
                break

    def handle_disconnect(self):
        """Handles cleanup and informs user."""
        if self.running:
            self.running = False
            self.display_message("--- Disconnected from Server. ---")
            messagebox.showinfo("Disconnected", "TCP Connection lost.")
            self.cleanup_sockets()

    def cleanup_sockets(self):
        """Closes TCP streams, UDP sockets, and cancels network tasks."""
        if self.listen_task:
            if not self.listen_task.done():
                self.listen_task.cancel()
            self.listen_task = None

        if self.tcp_writer:
            try:
                self.tcp_writer.close()
            except Exception:
                pass
            self.tcp_reader = None
            self.tcp_writer = None

        if self.udp_socket:
            try:
                self.loop.remove_reader(self.udp_socket.fileno())
            except Exception:
                pass
            try:
                self.udp_socket.close()
            except OSError as e:
                print(f"Warning: Error closing UDP socket: {e}")
            self.udp_socket = None

    def on_closing(self, silent=False):
        """Handles window closing event, sends QUIT, cleans up, and destroys the UI."""
        self.running = False
        if self.tcp_writer:
            try:

                async def send_quit():
                    self.tcp_writer.write("QUIT".encode("utf-8"))
                    await self.tcp_writer.drain()

                self.loop.create_task(send_quit())
            except Exception as e:
                print(f"Warning: Failed to schedule QUIT signal: {e}")

        self.cleanup_sockets()

        if not silent:
            if self.loop.is_running():
                self.loop.stop()
            self.quit()
            self.destroy()


class ChatServer:
    """A simple TCP/IP chat server for relaying messages between clients."""

    def __init__(self, host="127.0.0.1", tcp_port=TCP_PORT, loop=None):
        """Initializes the ChatServer with host and port settings."""
        self.host = host
        self.tcp_port = tcp_port
        self.loop = loop or asyncio.get_event_loop()
        self.running = True
        self.clients = {}
        self.tcp_server = None

    async def start(self):
        """Sets up and starts the TCP listener using asyncio."""
        try:
            self.tcp_server = await asyncio.start_server(self.handle_client, self.host, self.tcp_port)
            print(f"Server started. Listening on {self.host}:{self.tcp_port} (TCP)")
            return True
        except Exception as e:
            print(f"Could not start server: {e}")
            return False

    async def broadcast(self, sender_writer, message):
        """Sends a message to all connected clients except the sender."""
        encoded_message = message.encode("utf-8")

        writers_to_remove = []
        for writer in list(self.clients.keys()):
            if writer != sender_writer:
                try:
                    writer.write(encoded_message)
                    await writer.drain()
                except ConnectionResetError:
                    writers_to_remove.append(writer)
                except Exception as e:
                    print(f"Error broadcasting to client: {e}")
                    writers_to_remove.append(writer)

        for writer in writers_to_remove:
            self.cleanup_client(writer)

    def cleanup_client(self, writer):
        """Removes a client from tracking lists and closes their stream."""
        if writer in self.clients:
            nickname = self.clients.pop(writer)
            print(f"Client {nickname} disconnected.")
            self.loop.create_task(self.broadcast(None, f"--- {nickname} has left the chat. ---"))

        try:
            writer.close()
        except Exception as e:
            print(f"Warning: Error closing client stream: {e}")

    async def handle_client(self, reader, writer):
        """Handles a single client connection asynchronously."""
        addr = writer.get_extra_info("peername")
        print(f"New connection established from {addr}")

        nickname = None

        try:
            data = await reader.read(BUFFER_SIZE)
            if not data:
                return

            msg = data.decode("utf8").strip()
            if msg.startswith("NICK:"):
                nickname = msg[5:].strip()
                self.clients[writer] = nickname
                print(f"Client registered: {nickname}")
                await self.broadcast(None, f"--- {nickname} has joined the chat. ---")

                welcome_msg = f"Welcome, {nickname}!".encode("utf-8")
                writer.write(welcome_msg)
                await writer.drain()
            else:
                print(f"Connection closed: Did not send NICK for {addr}")
                writer.close()
                return

            while self.running:
                data = await reader.read(BUFFER_SIZE)
                if not data:
                    break

                msg = data.decode("utf8").strip()

                if msg == "QUIT":
                    break
                else:
                    await self.broadcast(writer, msg)
                    print(f"Relayed: {msg}")

        except ConnectionResetError:
            pass
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"Error handling client {nickname or addr}: {e}")
        finally:
            if writer in self.clients:
                self.cleanup_client(writer)
            else:
                try:
                    writer.close()
                except Exception:
                    pass

    async def stop(self):
        """Stops the server, closes listeners, and disconnects all clients."""
        self.running = False
        if self.tcp_server:
            self.tcp_server.close()
            await self.tcp_server.wait_closed()

        for writer in list(self.clients.keys()):
            self.cleanup_client(writer)

        print("Server stopped.")


if __name__ == "__main__":
    loop = None
    root = None
    try:
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        root = tk.Tk()
        root.withdraw()
        mode = simpledialog.askstring("Mode Selection", "Run as (S)erver or (C)lient?", initialvalue="C")

        if mode:
            mode = mode.upper()

            if mode == "S":

                async def server_runner():
                    server_host = simpledialog.askstring(
                        "Server Binding IP",
                        "Enter IP to bind (e.g., 127.0.0.1 for local testing, 192.168.x.x for LAN):",
                        initialvalue="127.0.0.1",
                    )
                    if server_host:
                        server = ChatServer(host=server_host, loop=loop)
                        if await server.start():
                            print("Server running. Press Ctrl+C to stop.")
                            while server.running:
                                await asyncio.sleep(1)
                            await server.stop()
                    else:
                        print("Server IP binding cancelled. Exiting.")

                try:
                    loop.run_until_complete(server_runner())
                except KeyboardInterrupt:
                    print("Interrupted by user.")

            elif mode == "C":
                app = ChatClient(loop=loop)

                def start_network_tasks():
                    if app.running:
                        asyncio.run_coroutine_threadsafe(app.connect_and_start(), loop)
                        loop.run_forever()

                network_thread = threading.Thread(target=start_network_tasks, daemon=True)
                network_thread.start()

                app.mainloop()

            else:
                print("Invalid mode selected. Exiting.")

    except Exception as e:
        print(f"An error occurred in main execution: {e}")
    finally:
        if "root" in locals() and root and root.winfo_exists():
            root.destroy()
        if loop and not loop.is_running() and not loop.is_closed():
            loop.close()
