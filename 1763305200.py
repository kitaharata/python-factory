import select
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

    def __init__(self):
        """Initializes the ChatClient application and sets up connections."""
        super().__init__()
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
        self.tcp_socket = None
        self.udp_socket = None
        self.running = True
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.setup_gui()
        self.connect_and_start()

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

    def connect_and_start(self):
        """Establishes TCP and UDP connections and starts the network thread."""
        self.display_message(f"--- Attempting TCP connection to {self.server_ip}:{TCP_PORT} ---")
        try:
            self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.tcp_socket.connect((self.server_ip, TCP_PORT))
            self.tcp_socket.setblocking(False)
            self.display_message("--- TCP connected. ---")
            self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            try:
                self.udp_socket.bind(("", UDP_PORT))
                self.udp_socket.setblocking(False)
            except OSError as e:
                self.display_message(f"Error: Could not bind UDP socket ({e}). UDP disabled.")
                self.udp_socket = None
            if self.tcp_socket:
                self.tcp_socket.send(f"NICK:{self.nickname}".encode("utf-8"))
            self.network_thread = threading.Thread(target=self.network_loop, daemon=True)
            self.network_thread.start()
        except ConnectionRefusedError:
            self.display_message("Connection Error: Server refused connection.")
            messagebox.showerror("Error", "Server refused connection. Make sure the server is running.")
            self.on_closing(silent=True)
        except Exception as e:
            self.display_message(f"Connection Error: {e}")
            messagebox.showerror("Error", f"Failed to connect: {e}")
            self.on_closing(silent=True)

    def send_message(self, event=None):
        """Handles sending messages via the selected protocol (TCP or UDP)."""
        message = self.msg_input.get().strip()
        if not message:
            return
        mode = self.mode_var.get()
        full_message = f"[{self.nickname}]: {message}"
        self.msg_input.delete(0, tk.END)
        try:
            if mode == "TCP" and self.tcp_socket:
                self.tcp_socket.send(full_message.encode("utf-8"))
                self.display_message(f"(TCP Sent) {full_message}")
            elif mode == "UDP" and self.udp_socket:
                self.udp_socket.sendto(f"(UDP Broadcast) {full_message}".encode("utf-8"), ("255.255.255.255", UDP_PORT))
            else:
                self.display_message("Error: Socket not ready or invalid mode selected.")
        except Exception as e:
            self.display_message(f"Send Error: {e}")
            self.handle_disconnect()

    def network_loop(self):
        """Runs in a separate thread, using select to monitor sockets."""
        sockets = []
        if self.tcp_socket:
            sockets.append(self.tcp_socket)
        if self.udp_socket:
            sockets.append(self.udp_socket)
        if not sockets:
            self.after(0, lambda: self.display_message("No active sockets. Networking thread exiting."))
            return
        while self.running:
            try:
                readable, _, _ = select.select(sockets, [], [], TIMEOUT)
                for sock in readable:
                    if sock == self.tcp_socket:
                        data = sock.recv(BUFFER_SIZE)
                        if data:
                            msg = data.decode("utf-8")
                            self.after(0, lambda m=msg: self.display_message(f"[TCP] {m}"))
                        else:
                            self.after(0, self.handle_disconnect)
                            return
                    elif sock == self.udp_socket:
                        data, addr = sock.recvfrom(BUFFER_SIZE)
                        if data:
                            msg = data.decode("utf-8")
                            self.after(0, lambda m=msg: self.display_message(f"[UDP from {addr[0]}] {m}"))
            except select.error as se:
                if self.running:
                    print(f"Select Error in client network loop: {se}")
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
        """Closes and nullifies TCP and UDP sockets."""
        if self.tcp_socket:
            try:
                self.tcp_socket.close()
            except OSError as e:
                print(f"Warning: Error closing TCP socket: {e}")
            self.tcp_socket = None
        if self.udp_socket:
            try:
                self.udp_socket.close()
            except OSError as e:
                print(f"Warning: Error closing UDP socket: {e}")
            self.udp_socket = None

    def on_closing(self, silent=False):
        """Handles window closing event, sends QUIT, cleans up, and destroys the UI."""
        self.running = False
        if self.tcp_socket:
            try:
                self.tcp_socket.send("QUIT".encode("utf-8"))
            except OSError as e:
                print(f"Warning: Failed to send QUIT signal: {e}")
        self.cleanup_sockets()
        if not silent:
            self.quit()
            self.destroy()


class ChatServer:
    """A simple TCP/IP chat server for relaying messages between clients."""

    def __init__(self, host="127.0.0.1", tcp_port=TCP_PORT):
        """Initializes the ChatServer with host and port settings."""
        self.host = host
        self.tcp_port = tcp_port
        self.running = True
        self.clients = {}
        self.inputs = []
        self.tcp_listener = None

    def start(self):
        """Sets up and starts the TCP listener socket in a new thread."""
        try:
            self.tcp_listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.tcp_listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.tcp_listener.bind((self.host, self.tcp_port))
            self.tcp_listener.listen(5)
            self.inputs.append(self.tcp_listener)
            print(f"Server started. Listening on {self.host}:{self.tcp_port} (TCP)")
            threading.Thread(target=self.server_loop, daemon=True).start()
            return True
        except Exception as e:
            print(f"Could not start server: {e}")
            return False

    def broadcast(self, sender_socket, message):
        """Sends a message to all connected clients except the sender."""
        encoded_message = message.encode("utf-8")
        for sock, nickname in list(self.clients.items()):
            if sock != sender_socket:
                try:
                    sock.send(encoded_message)
                except OSError:
                    self.cleanup_client(sock)

    def cleanup_client(self, sock):
        """Removes a client from tracking lists and closes their socket."""
        if sock in self.inputs:
            self.inputs.remove(sock)
        if sock in self.clients:
            nickname = self.clients.pop(sock)
            print(f"Client {nickname} disconnected.")
            self.broadcast(None, f"--- {nickname} has left the chat. ---")
        try:
            sock.close()
        except OSError as e:
            print(f"Warning: Error closing client socket: {e}")

    def server_loop(self):
        """Main server loop using select to handle new connections and client data."""
        while self.running:
            try:
                readable, _, exceptional = select.select(self.inputs, [], self.inputs, TIMEOUT)
                for s in readable:
                    if s == self.tcp_listener:
                        client_socket, client_address = self.tcp_listener.accept()
                        client_socket.setblocking(False)
                        self.inputs.append(client_socket)
                        print(f"New connection established from {client_address}")
                    else:
                        try:
                            data = s.recv(BUFFER_SIZE)
                            if data:
                                msg = data.decode("utf8").strip()
                                if s not in self.clients and msg.startswith("NICK:"):
                                    nickname = msg[5:].strip()
                                    self.clients[s] = nickname
                                    print(f"Client registered: {nickname}")
                                    self.broadcast(None, f"--- {nickname} has joined the chat. ---")
                                    s.send(f"Welcome, {nickname}!".encode("utf-8"))
                                elif msg == "QUIT":
                                    self.cleanup_client(s)
                                else:
                                    self.broadcast(s, msg)
                                    print(f"Relayed: {msg}")
                            else:
                                self.cleanup_client(s)
                        except ConnectionResetError:
                            self.cleanup_client(s)
                        except Exception as e:
                            print(f"Error handling client data: {e}")
                            self.cleanup_client(s)
                for s in exceptional:
                    self.cleanup_client(s)
            except select.error as se:
                if self.running:
                    print(f"Server Select Error: {se}")
                break
            except Exception as e:
                if self.running:
                    print(f"Server Loop Fatal Error: {e}")
                break

    def stop(self):
        """Stops the server, closes listeners, and disconnects all clients."""
        self.running = False
        if self.tcp_listener:
            try:
                self.tcp_listener.close()
            except OSError as e:
                print(f"Warning: Error closing TCP listener socket: {e}")
        for sock in list(self.clients.keys()):
            self.cleanup_client(sock)
        self.inputs = []
        print("Server stopped.")


if __name__ == "__main__":
    try:
        root = tk.Tk()
        root.withdraw()
        mode = simpledialog.askstring("Mode Selection", "Run as (S)erver or (C)lient?", initialvalue="C")
        if mode:
            mode = mode.upper()
            if mode == "S":
                server_host = simpledialog.askstring(
                    "Server Binding IP",
                    "Enter IP to bind (e.g., 127.0.0.1 for local testing, 192.168.x.x for LAN):",
                    initialvalue="127.0.0.1",
                )
                if server_host:
                    server = ChatServer(host=server_host)
                    if server.start():
                        print("Server running. Close this console window or press Ctrl+C to stop.")
                        while server.running:
                            threading.Event().wait(1)
                else:
                    print("Server IP binding cancelled. Exiting.")
            elif mode == "C":
                app = ChatClient()
                app.mainloop()
            else:
                print("Invalid mode selected. Exiting.")
    except Exception as e:
        print(f"An error occurred in main execution: {e}")
    finally:
        if "root" in locals() and root.winfo_exists():
            root.destroy()
