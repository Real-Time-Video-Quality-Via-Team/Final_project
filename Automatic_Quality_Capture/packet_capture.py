import subprocess
from collections import defaultdict
import re

def startTshark(interface):
    """
    Initiates a tshark subprocess to capture UDP and TCP packets on the specified network interface.

    Args:
        interface (str): The network interface to capture packets on (e.g., "eth0").

    Returns:
        Popen: A subprocess Popen object capturing tshark output in real-time.
    """
    command = ['tshark', '-i', interface, '-f', 'udp or tcp']
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8',
                               errors='ignore')
    print("Capturing packets...")
    return process


def parse_line(output):
    """
    Parses a line of tshark output to extract relevant packet information, including source/destination IPs and ports.

    Args:
        output (str): A single line of output from tshark.

    Returns:
        tuple: Parsed information as (src_ip, dest_ip, src_port, dest_port, total_size, arrival_time) or None if parsing fails.
    """
    parts = output.split()

    # Check if the packet protocol is one of the expected ones (UDP, TCP, SSL, or TLS)
    if not any(protocol in parts for protocol in ['UDP', 'TCP', 'SSL']):
        return None

    # Regular expressions for detecting IPv4 and IPv6 addresses
    ipv4_regex = r'\d{1,3}(\.\d{1,3}){3}'
    ipv6_regex = r'([a-fA-F0-9:]+:+)+[a-fA-F0-9]+'

    if len(parts) >= 10:
        try:
            arrival_time = float(parts[0])

            # Match source and destination IPs (could be either IPv4 or IPv6)
            src_ip_match = re.match(ipv6_regex, parts[2]) or re.match(ipv4_regex, parts[2])
            dest_ip_match = re.match(ipv6_regex, parts[4]) or re.match(ipv4_regex, parts[4])

            if not src_ip_match or not dest_ip_match:
                return None

            src_ip = src_ip_match.group(0)
            dest_ip = dest_ip_match.group(0)

            # Extract source and destination ports
            src_port = parts[7]
            dest_port = parts[9]

            # Extract total packet size
            total_size = int(parts[6])

            return src_ip, dest_ip, src_port, dest_port, total_size, arrival_time
        except (IndexError, ValueError):
            return None
    return None


def find_largest_streams(process, findOutgoing, findIncoming, myIp):
    """
    Identifies the largest outgoing and incoming data streams based on packet counts for a specified IP.

    Args:
        process (Popen): The tshark subprocess object for reading captured packet data.
        findOutgoing (bool): Flag to find the largest outgoing stream.
        findIncoming (bool): Flag to find the largest incoming stream.
        myIp (list): List containing local IP addresses.

    Returns:
        tuple: The largest outgoing and incoming streams as tuples of (src_ip, dest_ip).
    """
    incomingDict = defaultdict(int)
    outgoingDict = defaultdict(int)
    count = 0

    # Read 2000 packets or until the process ends
    while count < 2000:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            packetInfo = parse_line(output)
            if packetInfo:
                src_ip, dest_ip, _, _, _, _ = packetInfo
                if src_ip in myIp:
                    outgoingDict[(src_ip, dest_ip)] += 1
                    count += 1

                elif dest_ip in myIp:
                    incomingDict[(src_ip, dest_ip)] += 1
                    count += 1

                else:
                    print("Error format")
                    print(packetInfo)
                    print(f"{src_ip} ---> {dest_ip}")
            else:
                print(output)
                print("Error parsing line!")

    # Determine the largest streams based on packet counts
    if findIncoming and findOutgoing:
        max_incoming = max(incomingDict, key=incomingDict.get) if incomingDict else None
        max_outgoing = max(outgoingDict, key=outgoingDict.get) if outgoingDict else None
        return max_outgoing, max_incoming
    elif findIncoming:
        return max(incomingDict, key=incomingDict.get) if incomingDict else None
    elif findOutgoing:
        return max(outgoingDict, key=outgoingDict.get) if outgoingDict else None
    return None
