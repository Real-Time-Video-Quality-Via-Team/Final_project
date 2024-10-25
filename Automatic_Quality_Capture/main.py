import argparse
import socket
from threading import Lock, Thread
from queue import Queue
from packet_capture import startTshark, find_largest_streams
from data_analysis import analyzeData, calculateNetworkParameters
from gui import createGUI
from plotting import plot_data
import select
import time

duration = 2  # Duration for analyzing metrics in seconds

def findMyIp():
    ip_addresses = []

    try:
        # Get all addresses using getaddrinfo
        hostname = socket.gethostname()
        addr_info = socket.getaddrinfo(hostname, None)

        for entry in addr_info:
            address = entry[4][0]  # Extract the IP address part
            ip_addresses.append(address)  # Add both IPv4 and IPv6 to the same list

    except Exception as e:
        print(f"Error finding IP addresses: {e}")

    # Return a tuple with the list of IPs
    return tuple(ip_addresses)


def shutdown_listener(shutdown_flag):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 9999))
    server_socket.listen(1)
    print("Listening for shutdown command on port 9999...")

    while not shutdown_flag[0]:
        readable, _, _ = select.select([server_socket], [], [], 1)

        if readable:
            conn, addr = server_socket.accept()
            with conn:
                print(f"Connection established with {addr}")
                data = conn.recv(1024).decode('utf-8')
                if data == "Stop":
                    print("Shutdown signal received: Call ended")
                    shutdown_flag[0] = True
                    break

        if shutdown_flag[0]:
            print("Shutdown flag set, closing socket.")
            break

    server_socket.close()
    print("Listener socket closed.")


def main(interface):
    lock = Lock()
    notify = [False]
    update_notify = [None, False]
    shutdown_flag = [False]
    data_dict = {}
    qualities_list = []
    all_quality_data = {'bitrate': [], 'jitter': [], 'latency': [], 'quality': []}

    myIp = findMyIp()
    print(myIp)
    process = startTshark(interface)
    outgoingStream, incomingStream = find_largest_streams(process, True, True, myIp)

    if outgoingStream and incomingStream:
        analyze_thread = Thread(target=analyzeData, args=(process, outgoingStream, incomingStream, data_dict, lock, notify, shutdown_flag, myIp))
        calc_thread = Thread(target=calculateNetworkParameters, args=(data_dict, lock, notify, update_notify, qualities_list, shutdown_flag, all_quality_data))

        analyze_thread.start()
        calc_thread.start()

        gui_thread = Thread(target=createGUI, args=(lock, update_notify, shutdown_flag, myIp))
        gui_thread.start()

        listener_thread = Thread(target=shutdown_listener, args=(shutdown_flag,))
        listener_thread.start()

        listener_thread.join()
        analyze_thread.join()
        calc_thread.join()
        gui_thread.join()

        if shutdown_flag[0]:
            plot_thread = Thread(target=plot_data, args=(all_quality_data,))
            plot_thread.start()
            plot_thread.join()

    print("Program finished")


if __name__ == '__main__':
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Network Quality Analysis for Microsoft Teams")
    parser.add_argument("interface", help="Network interface to use for packet capture")
    args = parser.parse_args()

    # Run the main function with the specified interface
    main(args.interface)
