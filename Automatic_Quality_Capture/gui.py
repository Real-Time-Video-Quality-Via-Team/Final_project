import tkinter as tk
import queue

def createGUI(lock, update_notify, shutdown_flag, myIp):
    """
    Creates and manages a Tkinter-based GUI for monitoring network quality parameters (bitrate, jitter, latency,
    quality) for active network connections. Displays dynamic connection details with real-time updates in a scrollable
    view. Highlights connections associated with the local host.

    Args:
        lock (threading.Lock): Lock for safely accessing shared data across threads.
        update_notify (list): List flag to signal GUI updates for displaying network data.
        shutdown_flag (list): Flag list for indicating when to close the GUI.
        myIp (list): List containing local IPv4 and IPv6 addresses, highlighted in the GUI.

    Variables:
        data_queue (Queue): Queue for handling thread-safe data updates for GUI display.
        connection_labels (dict): Dictionary of labels for each network connection, storing all related metric labels.
        update_counter (list): Counter for managing periodic clearing of outdated connections from the GUI.
    """
    # Initialize queue and main GUI window
    data_queue = queue.Queue()
    root = tk.Tk()
    root.title("Network Quality Monitor")
    root.geometry("1000x600")
    root.configure(bg="#2c3e50")

    # Header setup
    header = tk.Label(root, text="Network Connections", font=("Helvetica", 20, "bold"), bg="#34495e", fg="#ecf0f1",
                      padx=20, pady=15)
    header.pack(pady=(20, 10), fill=tk.X)

    # Frame for network connections with scrollbar
    conn_frame = tk.Frame(root, bg="#2c3e50")
    conn_frame.pack(padx=20, pady=(0, 20), fill=tk.BOTH, expand=True)

    canvas = tk.Canvas(conn_frame, bg="#2c3e50")
    scrollbar = tk.Scrollbar(conn_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="#2c3e50")

    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    connection_labels = {}
    update_counter = [0]  # Update counter stored in a list to allow modification in nested functions

    def clear_gui():
        """Clear all labels from the GUI, resetting the display."""
        for key in list(connection_labels.keys()):
            for label in connection_labels[key]:
                label.grid_forget()
            connection_labels.pop(key)

    def updateLabel():
        """Fetches data from the queue, updating labels for network connections. Clears outdated connections periodically."""
        while not data_queue.empty():
            try:
                results = data_queue.get_nowait()
                row = 0  # Reset row position for connections display

                # Clear the GUI every 5 update cycles
                if update_counter[0] == 5:
                    clear_gui()
                    update_counter[0] = 0

                # Identify connections to remove
                keys_to_remove = set(connection_labels.keys()) - set(results.keys())
                for key in keys_to_remove:
                    for label in connection_labels[key]:
                        label.grid_forget()
                    connection_labels.pop(key)

                # Add or update labels for active connections
                for key, (bitrate, jitter, latency, quality) in results.items():
                    src_ip, dest_ip, src_port, dest_port = key

                    # Check if connection is new, and if so, add its labels
                    if key not in connection_labels:
                        src_label = tk.Label(scrollable_frame, text=f"Src IP: {src_ip}:{src_port}", font=("Helvetica", 12),
                                             bg="#e74c3c" if src_ip in myIp else "#34495e", fg="#ecf0f1",
                                             anchor="w", relief="raised", bd=1, padx=5, pady=5)
                        arrow_label = tk.Label(scrollable_frame, text="→", font=("Helvetica", 12), bg="#2c3e50", fg="#ecf0f1",
                                               anchor="w")
                        dest_label = tk.Label(scrollable_frame, text=f"Dest IP: {dest_ip}:{dest_port}", font=("Helvetica", 12),
                                               bg="#34495e", fg="#ecf0f1", anchor="w", relief="raised", bd=1, padx=5, pady=5)

                        # Create metric labels for connection statistics
                        bitrate_label = tk.Label(scrollable_frame, text=f"Bitrate: {bitrate:.2f} bps", font=("Helvetica", 12),
                                                 bg="#34495e", fg="#ecf0f1", anchor="w", relief="flat", bd=0, padx=5, pady=5)
                        jitter_label = tk.Label(scrollable_frame, text=f"Jitter: {jitter:.2f} ms", font=("Helvetica", 12),
                                                bg="#34495e", fg="#ecf0f1", anchor="w", relief="flat", bd=0, padx=5, pady=5)
                        latency_label = tk.Label(scrollable_frame, text=f"Latency: {latency:.2f} ms", font=("Helvetica", 12),
                                                 bg="#34495e", fg="#ecf0f1", anchor="w", relief="flat", bd=0, padx=5, pady=5)
                        quality_label = tk.Label(scrollable_frame, text=f"Quality: {quality}/10", font=("Helvetica", 12),
                                                 bg="#34495e", fg="#ecf0f1", anchor="w", relief="flat", bd=0, padx=5, pady=5)

                        # Add labels to the dictionary and arrange them in the grid
                        connection_labels[key] = (src_label, arrow_label, dest_label, bitrate_label, jitter_label, latency_label, quality_label)
                        src_label.grid(row=row, column=0, sticky="ew", padx=5, pady=5)
                        arrow_label.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
                        dest_label.grid(row=row, column=2, sticky="ew", padx=5, pady=5)
                        bitrate_label.grid(row=row + 1, column=0, sticky="ew", padx=5, pady=5)
                        jitter_label.grid(row=row + 1, column=1, sticky="ew", padx=5, pady=5)
                        latency_label.grid(row=row + 1, column=2, sticky="ew", padx=5, pady=5)
                        quality_label.grid(row=row + 1, column=3, sticky="ew", padx=5, pady=5)

                    else:
                        # Update existing labels for the connection
                        src_label, arrow_label, dest_label, bitrate_label, jitter_label, latency_label, quality_label = connection_labels[key]
                        src_label.config(text=f"Src IP: {src_ip}:{src_port}")
                        src_label.config(bg="#e74c3e" if src_ip in myIp else "#34495e")
                        dest_label.config(text=f"Dest IP: {dest_ip}:{dest_port}")
                        bitrate_label.config(text=f"Bitrate: {bitrate:.2f} bps")
                        jitter_label.config(text=f"Jitter: {jitter:.2f} ms")
                        latency_label.config(text=f"Latency: {latency:.2f} ms")
                        quality_label.config(text=f"Quality: {quality}/10")

                    row += 2  # Move to the next row after each connection

                update_counter[0] += 1

            except queue.Empty:
                pass

        root.after(1000, updateLabel)

    def process_data():
        """Fetches data from shared variables, adds it to the queue for thread-safe updates, and checks for shutdown."""
        with lock:
            if shutdown_flag[0]:
                print("GUI shutdown")
                root.quit()
                return
            if update_notify[1]:
                data_queue.put(update_notify[0])
                update_notify[1] = False

        root.after(500, process_data)

    def on_close():
        """Handles GUI shutdown and sets the shutdown flag for other threads."""
        shutdown_flag[0] = True
        print("Shutting down the GUI...")

    root.protocol("WM_DELETE_WINDOW", on_close)
    process_data()
    updateLabel()
    root.mainloop()
