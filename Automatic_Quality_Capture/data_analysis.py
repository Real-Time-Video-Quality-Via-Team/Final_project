import time
from collections import defaultdict
from packet_capture import parse_line, find_largest_streams
from quality_calculations import calculate_quality, calculateLatency, calculateJitter
import select

# Define the interval duration for data processing
duration = 2

def analyzeData(process, outgoingStream, incomingStream, data_dict, lock, notify, shutdown_flag, myIp):
    """
    Continuously analyzes network data to identify and monitor video streams, processing and tracking packet sizes,
    arrival times, and data volume per stream. The function also detects low bitrate streams and updates the
    outgoing/incoming streams as needed.

    Args:
        process (subprocess): Process output to read data packets from.
        outgoingStream (tuple): Current largest outgoing stream IP pair.
        incomingStream (tuple): Current largest incoming stream IP pair.
        data_dict (dict): Shared dictionary storing packet information per conversation.
        lock (threading.Lock): Lock for safely accessing shared data across threads.
        notify (list): Flag list to signal updates for network quality calculations.
        shutdown_flag (list): Shutdown signal flag list to terminate the function.
        myIp (list): List of IPv4 and IPv6 addresses representing the host.

    Variables:
        temporary_dict (defaultdict): Tracks per-stream packet details temporarily.
        sent_timestamps (defaultdict): Stores outgoing packet send times for latency calculations.
        inStreamDict, outStreamDict (defaultdict): Track incoming and outgoing traffic volumes.
    """
    temporary_dict = defaultdict(lambda: (0, 0, [], None))
    sent_timestamps = defaultdict(list)
    start_time = time.time()
    inStreamDict = defaultdict(int)
    outStreamDict = defaultdict(int)

    while True:
        output = ''
        start_read_time = time.time()

        # Attempt to read data for up to 2 seconds
        while time.time() - start_read_time < 2:
            output = process.stdout.readline()
            if output != '':  # Data received
                break
            time.sleep(0.1)  # Reduce CPU usage by pausing briefly

        # Exit if the process has terminated
        if output == '' and process.poll() is not None:
            break

        # Parse the output packet data
        if output:
            packetInfo = parse_line(output)
            if packetInfo:
                src_ip, dest_ip, src_port, dest_port, size, arrival_time = packetInfo

                # Track traffic data for incoming/outgoing streams
                if (src_ip, dest_ip) == incomingStream or (src_ip, dest_ip) == outgoingStream:
                    key = (src_ip, dest_ip, src_port, dest_port)
                    if (src_ip, dest_ip) == outgoingStream:
                        sent_timestamps[key].append(arrival_time)
                    if sent_timestamps[key]:
                        sent_time = sent_timestamps[key].pop(0)
                    current_size, count, arrival_times, last_arrival_time = temporary_dict[key]
                    arrival_times.append(arrival_time)
                    temporary_dict[key] = (current_size + size, count + 1, arrival_times, arrival_time)
                else:
                    # Update stream sizes for IPv4 and IPv6 addresses
                    if src_ip in myIp:
                        outStreamDict[(src_ip, dest_ip)] = outStreamDict.get((src_ip, dest_ip), 0) + size
                    elif dest_ip in myIp:
                        inStreamDict[(src_ip, dest_ip)] = inStreamDict.get((src_ip, dest_ip), 0) + size

        # Periodically update and evaluate stream data every 'duration' seconds
        if time.time() - start_time >= duration:
            with lock:
                total_bytes_in = 0
                total_bytes_out = 0

                # Aggregate data for analysis
                for (src_ip, dest_ip, src_port, dest_port), (total_size, count, arrival_times, _) in temporary_dict.items():
                    if count > 0:
                        data_dict[(src_ip, dest_ip, src_port, dest_port)] = (total_size, count, arrival_times)
                    if incomingStream == (src_ip, dest_ip):
                        total_bytes_in += total_size
                    elif outgoingStream == (src_ip, dest_ip):
                        total_bytes_out += total_size

                # Stream replacement logic if the bitrate drops below 50 kbps
                if total_bytes_in <= 50000 * duration / 8 and inStreamDict:
                    incomingStream = max(inStreamDict, key=inStreamDict.get)
                if total_bytes_out <= 50000 * duration / 8 and outStreamDict:
                    outgoingStream = max(outStreamDict, key=outStreamDict.get)
                else:
                    notify[0] = True

            inStreamDict.clear()
            outStreamDict.clear()
            temporary_dict.clear()
            start_time = time.time()

        if shutdown_flag[0]:  # Check if shutdown is signaled
            print("Analysis shutdown")
            break

def calculateNetworkParameters(data_dict, lock, notify, update_notify, qualities_list, shutdown_flag, all_quality_data):
    """
    Analyzes stored packet data to compute network parameters like bitrate, latency, jitter, and quality. Updates
    results for UI or logging purposes, and appends calculated metrics for further monitoring or historical analysis.

    Args:
        data_dict (dict): Dictionary storing packet information for each conversation.
        lock (threading.Lock): Lock for safely accessing shared data across threads.
        notify (list): Flag to signal data updates for quality calculations.
        update_notify (list): Flag to indicate updated network parameter results.
        qualities_list (list): List storing quality scores for network performance over time.
        shutdown_flag (list): Shutdown signal flag list to terminate the function.
        all_quality_data (dict): Dictionary accumulating quality metrics data over time.
    """
    while not shutdown_flag[0]:
        time.sleep(duration)
        with lock:
            if notify[0]:
                conversationsDict = dict(data_dict)
                notify[0] = False
                results = {}

                # Compute network parameters for each conversation
                for key, (total_size, count, arrival_times) in conversationsDict.items():
                    if count > 0:
                        bitrate = (total_size * 8) / duration
                        jitter = calculateJitter(arrival_times)
                        latency = calculateLatency(arrival_times)
                        quality = calculate_quality(bitrate, latency, jitter)

                        qualities_list.append(quality)
                        all_quality_data['bitrate'].append(bitrate)
                        all_quality_data['jitter'].append(jitter)
                        all_quality_data['latency'].append(latency)
                        all_quality_data['quality'].append(quality)
                        results[key] = (bitrate, jitter, latency, quality)

                # Signal UI update with results
                update_notify[0] = results
                update_notify[1] = True

                # Clear data for the next analysis period
                data_dict.clear()

    print("calcnet shutdown")
