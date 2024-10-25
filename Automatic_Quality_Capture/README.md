# Automatic Quality Capture for Microsoft Teams Calls

## Project Overview
This project analyzes the quality of Microsoft Teams calls in real-time by measuring critical network metrics such as **Latency**, **Jitter**, and **Bitrate**. These metrics are captured using **Tshark** and analyzed through a Python-based interface, providing users with continuous monitoring of call quality.

## Table of Contents
1. [Features](#features)
2. [Project Structure](#project-structure)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Key Components](#key-components)
6. [Technical Details](#technical-details)
7. [Results](#results)
8. [Future Improvements](#future-improvements)
9. [References](#references)

---

## Features
- **Real-Time Quality Monitoring**: Track network metrics (latency, jitter, bitrate) in real-time for ongoing calls.
- **Automated Call Initiation**: Initiate and monitor Teams calls automatically using Selenium.
- **Graphical User Interface**: Visualize call quality metrics through an intuitive GUI.
- **Data Visualization**: Generate quality trend plots over time.

---

## Project Structure

```plaintext
Automatic_Quality_Capture/
├── Crouler.py                # Manages data capturing threads
├── data_analysis.py          # Analyzes and processes packet data
├── gui.py                    # GUI for real-time monitoring
├── main.py                   # Main script to initialize processes
├── packet_capture.py         # Handles packet capture with Tshark
├── plotting.py               # Generates trend plots for quality metrics
├── quality_calculations.py   # Calculates quality metrics (latency, jitter, bitrate)
├── TeamsSelenium.jar         # Automates Teams call initiation
└── README.md                 # Project documentation
```
## Installation
### Clone the repository:

bash
Copy code
git clone https://github.com/your-username/Automatic_Quality_Capture.git
cd Automatic_Quality_Capture
### Install dependencies: 
Make sure you have Python 3.x and Java installed. Use the following command to install Python dependencies:

### Install Tshark: 
Install Wireshark to capture packets.

### Usage
#### How to run: 
1. Run "crawler.py".
2. Select the correct network interface on the gui.
3. Enter the required details to initiate the teams call.
4. Wait for the videochat to start and the magic will show up.

#### How to use other components:

* Start a Microsoft Teams call: The project’s TeamsSelenium.jar automates the initiation of a Teams call to ensure consistent and reliable test conditions.

* Start capturing and analyzing data: run 'python main.py --interface' [your_network_interface]
Monitor Real-Time Metrics: The GUI will display latency, jitter, and bitrate, updating continuously throughout the call.

## Key Components
### main.py:
Orchestrates the different components, initializes the GUI, and manages threads for data capture and analysis.
### packet_capture.py: 
Uses Tshark to capture packets on the specified interface.
### quality_calculations.py: 
Computes latency, jitter, and bitrate, which are core metrics for assessing call quality.
### TeamsSelenium.jar: 
Automates call initiation, reducing manual setup time and ensuring consistent testing.
### plotting.py: 
Generates post-call visualizations for each metric, highlighting trends and quality consistency.

## Technical Details

### Latency: 
Calculated as the maximum delay between packets.
### Jitter: 
Measures variability in packet arrival, impacting video/audio sync.
### Bitrate: 
Measures the rate of data transfer, influencing clarity and quality.
#### Data is processed and displayed in real time, providing actionable insights into the network conditions impacting call quality.

## Results
### Sample Observations
**Average Latency:** ~20-30ms (Good quality)    
**Jitter:** Maintained under 10ms   
**Bitrate:** Stable bitrate observed at 1.5 - 2 Mbps
Future Improvements

**Enhanced Latency Detection:** Integrate more precise measurement tools for end-to-end latency.
**Expanded Quality Metrics:** Include additional metrics like MOS (Mean Opinion Score) for comprehensive analysis.
**Dynamic Bitrate Adaptation:** Automatically adjust bitrate based on network conditions for optimized quality.

## References
**Impact of Packet Loss and Delay Variation on Real-Time Video Quality
Source: Springer**  
This study simulates the effects of packet loss and jitter for video formats like MPEG-2 and MPEG-4, showing how they affect video quality. It’s useful for understanding how jitter and packet loss impact visual clarity in video conferencing.

**Impact of Latency on QoE, Performance, and Collaboration in Virtual Environments
Source: MDPI**  
This research examines latency's effects on user experience in immersive environments. Although focused on VR, the findings on latency thresholds (around 75ms) for smooth interactions also apply to video conferencing, aligning with your latency requirements.

**Acceptable Jitter, Latency, and Packet Loss for Webex Meetings
Source: Cisco Community**   Cisco’s community post offers practical thresholds for video conferencing: jitter < 30ms, latency < 300ms, and loss < 1%. This benchmark is relevant for maintaining video and audio quality on Microsoft Teams.

**Effect of Bandwidth Limitations and Video Resolution on QoE for WebRTC-Based Video Conferencing
Source: University of Zagreb**
This paper discusses the impact of different bitrates (300, 600, 1200 kbps) and video resolutions on user experience, showing how higher bitrates correlate with improved quality.

