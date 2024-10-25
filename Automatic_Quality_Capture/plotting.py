import matplotlib.pyplot as plt

def plot_data(all_quality_data):
    """
    Plots quality metrics over time, including Quality, Bitrate, Latency, and Jitter, with their respective averages.

    Args:
        all_quality_data (dict): A dictionary containing lists for 'quality', 'bitrate', 'latency', and 'jitter'.
    """
    plt.figure(figsize=(12, 10))  # Create figure with defined dimensions

    # Calculate averages for each metric
    average_quality = sum(all_quality_data['quality']) / len(all_quality_data['quality']) if all_quality_data['quality'] else 0
    average_bitrate = sum(all_quality_data['bitrate']) / len(all_quality_data['bitrate']) if all_quality_data['bitrate'] else 0
    average_latency = sum(all_quality_data['latency']) / len(all_quality_data['latency']) if all_quality_data['latency'] else 0
    average_jitter = sum(all_quality_data['jitter']) / len(all_quality_data['jitter']) if all_quality_data['jitter'] else 0

    # Plot each metric in its own subplot
    # Quality plot
    plt.subplot(4, 1, 1)
    plt.plot(all_quality_data['quality'], label='Quality', color='b')
    plt.axhline(y=average_quality, color='orange', linestyle='--', label=f'Average Quality: {average_quality:.2f}')
    plt.title('Quality Over Time')
    plt.xlabel('Time Interval (seconds)')
    plt.ylabel('Quality Score (1-10)')
    plt.grid()
    plt.legend()

    # Bitrate plot
    plt.subplot(4, 1, 2)
    plt.plot(all_quality_data['bitrate'], label='Bitrate', color='purple')
    plt.axhline(y=average_bitrate, color='orange', linestyle='--', label=f'Average Bitrate: {average_bitrate:.2f}')
    plt.title('Bitrate Over Time')
    plt.xlabel('Time Interval (seconds)')
    plt.ylabel('Bitrate (bps)')
    plt.grid()
    plt.legend()

    # Latency plot
    plt.subplot(4, 1, 3)
    plt.plot(all_quality_data['latency'], label='Latency', color='r')
    plt.axhline(y=average_latency, color='orange', linestyle='--', label=f'Average Latency: {average_latency:.2f}')
    plt.title('Latency Over Time')
    plt.xlabel('Time Interval (seconds)')
    plt.ylabel('Latency (ms)')
    plt.grid()
    plt.legend()

    # Jitter plot
    plt.subplot(4, 1, 4)
    plt.plot(all_quality_data['jitter'], label='Jitter', color='g')
    plt.axhline(y=average_jitter, color='orange', linestyle='--', label=f'Average Jitter: {average_jitter:.2f}')
    plt.title('Jitter Over Time')
    plt.xlabel('Time Interval (seconds)')
    plt.ylabel('Jitter (ms)')
    plt.grid()
    plt.legend()

    plt.tight_layout()  # Adjusts layout to prevent overlap
    plt.show()
