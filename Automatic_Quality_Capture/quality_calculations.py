import numpy as np


def calculateJitter(arrival_times):
    """
    Calculates the jitter (variation in packet delay) based on arrival times of packets.

    Parameters:
    - arrival_times (list of float): Timestamps of packet arrivals in seconds.

    Returns:
    - jitter (float): Calculated jitter in milliseconds.

    Process:
    1. Calculate the time differences between consecutive packet arrivals.
    2. Compute the mean of these time differences.
    3. Determine the standard deviation from the mean, representing jitter.
    4. Convert the result to milliseconds.
    """
    if len(arrival_times) < 2:
        return 0

    time_diffs = [arrival_times[i] - arrival_times[i - 1] for i in range(1, len(arrival_times))]
    mean_diff = sum(time_diffs) / len(time_diffs)
    squared_diffs = [(diff - mean_diff) ** 2 for diff in time_diffs]
    jitter = (sum(squared_diffs) / len(squared_diffs)) ** 0.5
    return jitter * 1000  # Convert to milliseconds


def calculateLatency(arrival_times):
    """
    Calculates the worst-case latency between packets based on arrival times.

    Parameters:
    - arrival_times (list of float): Timestamps of packet arrivals in seconds.

    Returns:
    - max_latency (float): Calculated worst-case latency in milliseconds.

    Process:
    1. Compute time differences between consecutive packets.
    2. Find the maximum time difference to represent the highest delay, or latency.
    3. Convert the result to milliseconds.
    """
    if len(arrival_times) < 2:
        return 0

    time_diffs = np.diff(arrival_times)
    max_latency = np.max(time_diffs) * 1000  # Convert to milliseconds
    return max_latency


def latency_score(latency):
    """
    Generates a score from 1 to 10 based on latency.

    Parameters:
    - latency (float): Measured latency in milliseconds.

    Returns:
    - score (float): Quality score based on latency (1-10).

    Scoring:
    - Scores decrease as latency increases, with gradients applied for smoothness.
    """
    if latency <= 50:
        return 10
    elif latency <= 100:
        return 8 + (50 - (latency - 50)) / 50 * 2  # Smoother gradient
    elif latency <= 150:
        return 6 + (100 - (latency - 100)) / 50 * 2
    elif latency <= 200:
        return 4 + (150 - (latency - 150)) / 50 * 2
    else:
        return 1


def jitter_score(jitter):
    """
    Generates a score from 1 to 10 based on jitter.

    Parameters:
    - jitter (float): Measured jitter in milliseconds.

    Returns:
    - score (float): Quality score based on jitter (1-10).

    Scoring:
    - Scores decrease as jitter increases, with smoother scoring adjustments.
    """
    if jitter <= 5:
        return 10
    elif jitter <= 15:
        return 8 + (10 - (jitter - 5)) / 10 * 2
    elif jitter <= 25:
        return 6 + (10 - (jitter - 15)) / 10 * 2
    else:
        return 3


def bitrate_score(bitrate):
    """
    Generates a score from 1 to 10 based on bitrate.

    Parameters:
    - bitrate (int): Measured bitrate in bits per second (bps).

    Returns:
    - score (float): Quality score based on bitrate (1-10).

    Scoring:
    - Higher bitrates yield higher scores, with gradients for smoother scoring.
    """
    if bitrate > 2000000:  # > 2 Mbps
        return 10
    elif bitrate >= 1500000:  # 1.5 to 2 Mbps
        return 9 + (bitrate - 1500000) / 500000
    elif bitrate >= 1000000:  # 1 to 1.5 Mbps
        return 7 + (bitrate - 1000000) / 500000 * 1.5
    elif bitrate >= 500000:  # 500 kbps to 1 Mbps
        return 5 + (bitrate - 500000) / 500000 * 2
    else:
        return max(1, 4 - (500000 - bitrate) / 500000)


def calculate_quality(bitrate, latency, jitter):
    """
    Calculates an overall quality score based on bitrate, latency, and jitter.

    Parameters:
    - bitrate (int): Measured bitrate in bits per second (bps).
    - latency (float): Measured latency in milliseconds.
    - jitter (float): Measured jitter in milliseconds.

    Returns:
    - star_rating (int): Overall quality score, normalized to a 1-10 scale.

    Process:
    1. Generate individual scores for latency, jitter, and bitrate using their respective functions.
    2. Combine these scores, with weights assigned to each metric based on importance:
       - Latency: 0.3
       - Jitter: 0.3
       - Bitrate: 0.4
    3. Apply penalty factors based on thresholds:
       - Bitrate penalties for values below 2 Mbps, with increasing penalties below 1 Mbps.
       - Latency penalties for values over 50 ms, with larger penalties for values over 200 ms.
       - Jitter penalties for values above 10 ms, with higher penalties for jitter above 25 ms.
    4. Multiply combined score by penalty factor and normalize to a 1-10 scale.
    """
    lat_score = latency_score(latency)
    jit_score = jitter_score(jitter)
    bit_score = bitrate_score(bitrate)

    weights = {
        'latency': 0.3,
        'jitter': 0.3,
        'bitrate': 0.4,
    }

    combined_score = (lat_score * weights['latency'] +
                      jit_score * weights['jitter'] +
                      bit_score * weights['bitrate'])

    penalty_factor = 1.0
    if bitrate < 300000:
        penalty_factor *= 0.2
    elif bitrate < 500000:
        penalty_factor *= 0.5
    elif bitrate < 1000000:
        penalty_factor *= 0.7
    elif bitrate < 2000000:
        penalty_factor *= 0.9

    if latency > 200:
        penalty_factor *= 0.5
    elif latency > 100:
        penalty_factor *= 0.7
    elif latency > 50:
        penalty_factor *= 0.9

    if jitter > 25:
        penalty_factor *= 0.5
    elif jitter > 20:
        penalty_factor *= 0.8
    elif jitter > 10:
        penalty_factor *= 0.9

    overall_score = combined_score * penalty_factor

    star_rating = max(0, min(round(overall_score), 10))
    return star_rating
