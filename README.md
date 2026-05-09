# Distributed System — Identification & Time Server

A small distributed-systems demo built with Python's standard library. A multithreaded TCP server hands out the current server time to client "nodes" that introduce themselves with a short identification handshake. Both the server and the clients have minimal Tkinter GUIs so you can see the message flow in real time.

## Overview

The project is a classic client/server time-synchronization exercise:

- **Server (`server.py`)** — Listens on `127.0.0.1:9090`, accepts incoming TCP connections, and spawns a worker thread per client so multiple nodes can be served concurrently. Each request is logged in a scrollable, timestamped GUI console.
- - **Client (`client.py`)** — A "node" GUI with a single **REQUEST SYNC** button. When clicked, it opens a socket to the server, sends an `IDENTIFY: <node_name>` handshake, waits for the server's reply, and displays it. Network I/O happens on a background thread so the UI stays responsive.
  - - **Demo launcher (`demo.py`)** — Uses `multiprocessing` to start the server and three preset client nodes (`Alpha_Explorer`, `Beta_Traveler`, `Gamma_User`) in separate processes so you can watch the full conversation happen on one machine.
   
    - ## Protocol
   
    - The wire protocol is plain UTF-8 text over a single TCP exchange:
   
    - | Direction | Message |
    - |---|---|
    - | Client → Server | `IDENTIFY: <node_name>` |
    - | Server → Client | `GREETINGS <node_name>. SERVER TIME IS: HH:MM:SS` |
   
    - The server simulates ~2 seconds of processing per request to make the concurrent thread-per-client behavior visible. The client uses a 5-second timeout, the server a 10-second handshake timeout.
   
    - ## Requirements
   
    - - Python 3.8+ (only standard-library modules are used: `socket`, `threading`, `multiprocessing`, `tkinter`, `datetime`).
      - - A desktop environment that can display Tkinter windows (Tk must be available — on most Linux distros install `python3-tk`).
       
        - ## Running
       
        - Clone the repo and run from its root.
       
        - **Option 1 — Run the full demo (1 server + 3 clients):**
       
        - ```bash
          python demo.py
          ```

          **Option 2 — Run server and clients separately.**

          In one terminal:

          ```bash
          python server.py
          ```

          In another terminal (optionally pass a custom node name):

          ```bash
          python client.py Alpha_Explorer
          ```

          Click **REQUEST SYNC** in any client window to send a time-sync request. The server window will log the incoming request and the response.

          ## Configuration

          Network settings are defined as constants at the top of `server.py` and `client.py` and must match between the two:

          ```python
          HOST = "127.0.0.1"
          PORT = 9090
          BUFFER_SIZE = 1024
          ```

          Change `HOST` to `0.0.0.0` on the server (and to the server's IP on the client) to run across machines on a LAN.

          ## Project Structure

          ```
          .
          ├── server.py   # Multithreaded TCP server with Tkinter log console
          ├── client.py   # Client node GUI with REQUEST SYNC button
          └── demo.py     # Launches the server and 3 client nodes via multiprocessing
          ```

          ## Notes

          - The server creates a new daemon thread per accepted connection, so a slow client cannot block others.
          - - All Tk widget updates from worker threads are marshaled back to the main thread via `root.after(0, ...)` to keep Tkinter happy.
            - - Closing the server window terminates the accept loop and, in `demo.py`, also shuts down the spawned client processes.
             
              - ## Author
             
              - [RandomMoaz](https://github.com/RandomMoaz)
              - 
