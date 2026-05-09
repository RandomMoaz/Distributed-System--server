
import socket
import threading
import time
from datetime import datetime
import tkinter as tk
from tkinter import scrolledtext

# -----------------------------------------------------------------------------
# Network configuration
# -----------------------------------------------------------------------------
HOST = "127.0.0.1"
PORT = 9090
BUFFER_SIZE = 1024


class IdentityServer:
    def __init__(self, root):
        self.root = root
        self.root.title("Enterprise Identity Server")
        self.root.geometry("560x420")
        self.root.configure(bg="#1e1e2e")

        # ---------------- GUI ----------------
        title = tk.Label(
            root,
            text="IDENTIFICATION & TIME SERVER",
            font=("Segoe UI", 14, "bold"),
            bg="#1e1e2e",
            fg="white",
        )
        title.pack(pady=(15, 8))

        self.status_label = tk.Label(
            root,
            text="LISTENING",
            font=("Segoe UI", 11, "bold"),
            bg="#2196F3",
            fg="white",
            width=18,
            pady=4,
        )
        self.status_label.pack(pady=(0, 10))

        self.log_box = scrolledtext.ScrolledText(
            root,
            width=70,
            height=18,
            bg="#0f0f17",
            fg="#00ff88",
            font=("Consolas", 10),
            insertbackground="white",
        )
        self.log_box.pack(padx=12, pady=8, fill="both", expand=True)
        self.log_box.configure(state="disabled")

        # ---------------- Socket ----------------
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            self.server_socket.bind((HOST, PORT))
            self.server_socket.listen(5)
            self.log(f"# SERVER ONLINE on {HOST}:{PORT} -- AWAITING CLIENTS...")
        except OSError as e:
            self.log(f"!! FAILED TO START SERVER: {e}")
            return

        
        self.running = True
        accept_thread = threading.Thread(target=self.accept_loop, daemon=True)
        accept_thread.start()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    # ---------------------------------------------------------------------
    # Thread-safe logging
    # ---------------------------------------------------------------------
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        line = f"[{timestamp}] {message}\n"

        def _append():
            try:
                self.log_box.configure(state="normal")
                self.log_box.insert(tk.END, line)
                self.log_box.see(tk.END)
                self.log_box.configure(state="disabled")
            except tk.TclError:
                pass

        try:
            self.root.after(0, _append)
        except RuntimeError:
            pass

  
    def accept_loop(self):
        while self.running:
            try:
                client_sock, client_addr = self.server_socket.accept()
            except OSError:
                break

            worker = threading.Thread(
                target=self.handle_client,
                args=(client_sock, client_addr),
                daemon=True,
            )
            worker.start()

 
    def handle_client(self, client_sock, client_addr):
        try:
            client_sock.settimeout(10.0)

            raw = client_sock.recv(BUFFER_SIZE)
            if not raw:
                self.log(f"!! EMPTY CONNECTION from {client_addr}")
                return

            message = raw.decode("utf-8", errors="replace").strip()

            if message.startswith("IDENTIFY:"):
                client_name = message.split(":", 1)[1].strip() or "UNKNOWN"
            else:
                client_name = "UNKNOWN"

            self.log(f"REQUEST: Time Sync | FROM: {client_name}")

            # Simulate 2s processing. Because each client runs on its own
            # worker thread, other clients are NOT blocked.
            time.sleep(2)

            server_time = datetime.now().strftime("%H:%M:%S")
            response = f"GREETINGS {client_name}. SERVER TIME IS: {server_time}"

            client_sock.sendall(response.encode("utf-8"))

        except socket.timeout:
            self.log(f"!! TIMEOUT waiting for handshake from {client_addr}")
        except ConnectionResetError:
            self.log(f"!! CONNECTION RESET by {client_addr}")
        except Exception as e:
            self.log(f"!! ERROR with {client_addr}: {e}")
        finally:
            try:
                client_sock.close()
            except OSError:
                pass

    def on_close(self):
        self.running = False
        try:
            self.server_socket.close()
        except OSError:
            pass
        self.root.destroy()


def run_server_window():
    root = tk.Tk()
    IdentityServer(root)
    root.mainloop()


if __name__ == "__main__":
    run_server_window()