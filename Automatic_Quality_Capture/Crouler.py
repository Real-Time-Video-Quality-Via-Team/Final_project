import subprocess
import socket
import time
import os
import signal
import psutil
import tkinter as tk
from tkinter import messagebox

# GUI to select network interface
def select_network_interface_gui():
    def on_select():
        selected = interface_var.get()
        if selected:
            root.destroy()  # Close the GUI window
            start_process(selected)  # Start processes with the selected interface
        else:
            messagebox.showwarning("No Selection", "Please select a network interface.")

    # Initialize GUI window
    root = tk.Tk()
    root.title("Select Network Interface")
    root.geometry("400x400")  # Set the window size (width x height)

    # Variable to store selected interface, initialized to None
    interface_var = tk.StringVar()  # Let it be empty initially (no default selection)

    interfaces = list(psutil.net_if_addrs().keys())  # Get list of interfaces

    # Set custom font for labels and radio buttons
    label_font = ("Arial", 14, "bold")  # Font for the main label
    radio_font = ("Arial", 12)  # Font for each radio button

    # Create label for the title
    label = tk.Label(root, text="Available Network Interfaces:", font=label_font)
    label.pack(pady=10)

    # Create radio buttons for each network interface with increased font size
    for interface in interfaces:
        rb = tk.Radiobutton(root, text=interface, variable=interface_var, value=interface, font=radio_font)
        rb.deselect()  # Explicitly ensure all are deselected at the start
        rb.pack(anchor="w")

    # Add a button to confirm selection with increased font size
    select_button = tk.Button(root, text="Select", command=on_select, font=("Arial", 12))
    select_button.pack(pady=20)

    # Start the Tkinter event loop
    root.mainloop()

# Step 2: Start Selenium and QualityCapture processes with the selected interface
def start_process(selected_interface):
    # Step 1: Run the Selenium JAR file to start the call
    selenium_process = subprocess.Popen(
        ['java', '-jar', 'TeamsSelenium.jar'],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    print("Selenium JAR started, making the call...")

    # Step 2: Wait for call start signal from Selenium
    def wait_for_call_start():
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            server_socket.bind(('localhost', 9999))
            server_socket.listen(1)
            print("Waiting for call start signal from Selenium...")

            conn, addr = server_socket.accept()
            with conn:
                data = conn.recv(1024).decode()
                if data == "Start":
                    print("Call has started. Beginning quality analysis...")
                    server_socket.close()
                    time.sleep(5)  # Buffer time before starting QualityCapture

                    # Step 3: Run the QualityCapture process with selected interface as an argument
                    quality_capture_process = subprocess.Popen(['python', 'main.py', selected_interface])

                    # Wait for the QualityCapture process to finish
                    quality_capture_process.wait()
                    print("QualityCapture process terminated.")

        except Exception as e:
            print(f"Error occurred: {e}")
        finally:
            server_socket.close()

    # Wait for the call to start before proceeding
    wait_for_call_start()

    # Step 4: Ensure all child processes of Selenium are terminated
    def terminate_process_and_children(process):
        parent_pid = process.pid
        try:
            if os.name == 'nt':  # Windows
                subprocess.call(['taskkill', '/F', '/T', '/PID', str(parent_pid)], stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
            else:  # Unix-based systems
                os.killpg(os.getpgid(parent_pid), signal.SIGTERM)
        except Exception as e:
            print(f"Error terminating process: {e}")

    # Step 5: Stop the Selenium process once QualityCapture is complete
    terminate_process_and_children(selenium_process)
    selenium_process.wait()
    print("Selenium process terminated. Program stopped.")


# Initialize the GUI for selecting the network interface
select_network_interface_gui()
