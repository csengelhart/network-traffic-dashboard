"""
config.py

Stores shared configuration values for the network traffic monitoring
application.
"""

# Traffic analysis settings.
ANALYSIS_WINDOW_SECONDS = 60
TOP_N_RESULTS = 10

# Security alert thresholds.
TRAFFIC_SPIKE_MULTIPLIER = 3
EXCESSIVE_PACKET_THRESHOLD = 200
PORT_SCAN_THRESHOLD = 20