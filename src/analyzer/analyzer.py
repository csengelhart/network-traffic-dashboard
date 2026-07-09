"""
analyzer.py

Calculates traffic metrics from stored packet events and writes summarized
network activity data to PostgreSQL metric tables.
"""

import sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timedelta, timezone

# find project folder and append to find project modules
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

# project imports
from src.database.database import create_db_connection
from src.database.queries import (
    get_packets_for_time_window,
    insert_traffic_metrics,
    insert_protocol_metric,
    insert_top_talker,
    insert_port_activity,
)

WINDOW_SECONDS = 60
TOP_N = 10


def analyze_time_window(connection, window_start, window_end):
    """
    Analyzes packet events within a time window and stores summary metrics.
    """
    packets = get_packets_for_time_window(connection, window_start, window_end)

    if not packets:
        print("No packets found for this time window.")
        return

    packet_count = len(packets)
    total_bytes = sum(packet[6] for packet in packets if packet[6] is not None) # packet[6] = packet_size column

    protocol_summary = defaultdict(lambda: {"packet_count": 0, "total_bytes": 0})
    src_ip_summary = defaultdict(lambda: {"packet_count": 0, "total_bytes": 0})
    port_summary = defaultdict(lambda: {"packet_count": 0, "total_bytes": 0})

    for packet in packets:
        timestamp, src_ip, dst_ip, protocol, src_port, dst_port, packet_size = packet
        packet_size = packet_size or 0

        protocol_summary[protocol]["packet_count"] += 1
        protocol_summary[protocol]["total_bytes"] += packet_size

        src_ip_summary[src_ip]["packet_count"] += 1
        src_ip_summary[src_ip]["total_bytes"] += packet_size

        if dst_port is not None:
            # create combined key using destination port and protocol
            port_key = (dst_port, protocol)
            port_summary[port_key]["packet_count"] += 1
            port_summary[port_key]["total_bytes"] += packet_size

    # populate traffic_metrics table
    insert_traffic_metrics(
        connection,
        window_start,
        window_end,
        packet_count,
        total_bytes
    )

    # store one row per protocol into protocol_metrics
    for protocol, values in protocol_summary.items():
        insert_protocol_metric(
            connection,
            window_start,
            window_end,
            protocol,
            values["packet_count"],
            values["total_bytes"]
        )

    # sort source IPs by total bytes and in descending order
    top_sources = sorted(
        src_ip_summary.items(),
        key=lambda item: item[1]["total_bytes"],
        reverse=True
    )[:TOP_N]

    # store top talker in the top_talkers table
    for src_ip, values in top_sources:
        insert_top_talker(
            connection,
            window_start,
            window_end,
            src_ip,
            values["packet_count"],
            values["total_bytes"]
        )

    top_ports = sorted(
        port_summary.items(),
        key=lambda item: item[1]["packet_count"],
        reverse=True
    )[:TOP_N]

    # loop through each top port/protocol pair and
    # store port activity in the port_activity table
    for (dst_port, protocol), values in top_ports:
        insert_port_activity(
            connection,
            window_start,
            window_end,
            dst_port,
            protocol,
            values["packet_count"],
            values["total_bytes"]
        )

    print(f"Analyzed {packet_count} packets from {window_start} to {window_end}.")


def main():
    """
    Runs one traffic analysis window over the most recent packet data.
    """
    connection = create_db_connection()

    # set start and end of analysis window to current UTC time
    window_end = datetime.now(timezone.utc)
    window_start = window_end - timedelta(seconds=WINDOW_SECONDS)

    try:
        analyze_time_window(connection, window_start, window_end)

    finally:
        connection.close()


if __name__ == "__main__":
    main()