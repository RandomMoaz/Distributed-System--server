import multiprocessing
import time

from server import run_server_window
from client import run_client_window


CLIENT_NAMES = ["Alpha_Explorer", "Beta_Traveler", "Gamma_User"]


def main():
    processes = []

    # 1. Start the server window first
    print("Launching Enterprise Identity Server...")
    server_proc = multiprocessing.Process(
        target=run_server_window,
        name="Server",
        daemon=False,
    )
    server_proc.start()
    processes.append(server_proc)

    
    time.sleep(1.5)

    
    for name in CLIENT_NAMES:
        print(f"Launching Node: {name}")
        p = multiprocessing.Process(
            target=run_client_window,
            args=(name,),
            name=f"Client-{name}",
            daemon=False,
        )
        p.start()
        processes.append(p)

    print()
    print("All 4 windows launched: 1 server + 3 clients.")
    print("Close any window to stop that process.")
    print("Close the server window (or press Ctrl+C) to terminate the demo.")

    # Wait until the server is closed, then terminate the clients.
    try:
        server_proc.join()
    except KeyboardInterrupt:
        pass
    finally:
        for p in processes:
            if p.is_alive():
                p.terminate()
        for p in processes:
            p.join(timeout=2)


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()