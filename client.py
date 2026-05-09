

import sys
import socket
import threading
import tkinter as tk

# -----------------------------------------------------------------------------
# Network configuration -- must match server.py
# -----------------------------------------------------------------------------
HOST = "127.0.0.1"
PORT = 9090
BUFFER_SIZE = 1024
CLIENT_TIMEOUT = 5.0   


class ClientNode:
    def __init__(self, root, node_name):
        self.root = root
        self.node_name = node_name

        self.root.title(f"Node: {node_name}")
        self.root.geometry("360x280")
        self.root.configure(bg="#f4f4f4")

        # ---------------- GUI ----------------
        tk.Label(
            root,
            text=node_name.upper(),
            font=("Segoe UI", 13, "bold"),
            bg="#f4f4f4",
            fg="#222",
        ).pack(pady=(14, 8))

        self.received_label = tk.Label(
            root,
            text="RECEIVED:\nNode Idle.",
            font=("Segoe UI", 10, "italic"),
            bg="#f4f4f4",
            fg="#555",
            wraplength=320,
            justify="center",
        )
        self.received_label.pack(pady=10, padx=10)

        self.sync_btn = tk.Button(
            root,
            text="REQUEST SYNC",
            font=("Segoe UI", 11, "bold"),
            bg="#2196F3",
            fg="white",
            activebackground="#1976D2",
            activeforeground="white",
            width=22,
            pady=8,
            relief="flat",
            cursor="hand2",
            command=self.on_sync_click,
        )
        self.sync_btn.pack(pady=10)

    
    def on_sync_click(self):
        self.sync_btn.config(state="disabled", text="SYNCING...")
        self.set_received("Syncing...")
        threading.Thread(target=self.request_sync, daemon=True).start()

    def request_sync(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(CLIENT_TIMEOUT)   # 5s timeout (spec)
                s.connect((HOST, PORT))

                handshake = f"IDENTIFY: {self.node_name}"
                s.sendall(handshake.encode("utf-8"))

                data = s.recv(BUFFER_SIZE)
                result = (
                    data.decode("utf-8", errors="replace")
                    if data else
                    "ERROR: empty response from server."
                )

        except socket.timeout:
            result = "ERROR: server did not respond within 5 seconds."
        except ConnectionRefusedError:
            result = "ERROR: Server Offline. Please start server.py first."
        except OSError as e:
            result = f"ERROR: network failure ({e})."
        except Exception as e:
            result = f"ERROR: unexpected failure ({e})."

        self.safe_update(result)

   
    def safe_update(self, received_text):
        def _apply():
            try:
                self.set_received(received_text)
                self.sync_btn.config(state="normal", text="REQUEST SYNC")
            except tk.TclError:
                pass

        try:
            self.root.after(0, _apply)
        except RuntimeError:
            pass

    def set_received(self, text):
        self.received_label.config(text=f"RECEIVED:\n{text}")



def run_client_window(node_name):
    root = tk.Tk()
    ClientNode(root, node_name)
    root.mainloop()


def main():
    node_name = sys.argv[1] if len(sys.argv) > 1 else "Alpha_Explorer"
    run_client_window(node_name)


if __name__ == "__main__":
    main()