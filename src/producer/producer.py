"""
producer.py

Real-Time Network Traffic Monitoring Dashboard

This module captures live network packet metadata using PyShark and
publishes the extracted packet information to an Apache Kafka topic.

The producer monitors a selected network interface, extracts relevant
network metadata including source and destination IP addresses,
protocol information, ports, packet size, and timestamps, then
serializes the data as JSON and streams it to Kafka for downstream
processing.

Kafka Topic:
    network-packets

Author: Christopher Engelhart
"""

import asyncio
import json
from datetime import datetime, timezone

import pyshark
from kafka import KafkaProducer


KAFKA_TOPIC = "network-packets"
KAFKA_BOOTSTRAP_SERVER = "127.0.0.1:9092"
INTERFACE = "Wi-Fi"
PACKET_LIMIT = 500


def create_kafka_producer():
    """
        Creates and returns a Kafka producer instance.

        The producer establishes a connection to the Kafka broker and
        configures JSON serialization for outgoing messages. Packet
        metadata dictionaries are automatically converted to JSON and
        encoded as UTF-8 bytes before being published to Kafka.

        Returns:
            KafkaProducer: Configured Kafka producer object.
        """
    return KafkaProducer(
        bootstrap_servers=[KAFKA_BOOTSTRAP_SERVER],
        value_serializer=lambda value: json.dumps(value).encode("utf-8")
    )


def extract_packet_metadata(packet):
    """
      Extracts key metadata from a PyShark packet.

      Supports IPv4, IPv6, TCP, UDP, ICMP, and ICMPv6 packets. Returns a
      dictionary containing timestamp, source/destination IPs, protocol,
      source/destination ports, and packet size.

      Returns None if the packet does not contain IPv4 or IPv6 data, or if
      metadata extraction fails.
      """

    try:
        timestamp = packet.sniff_time.astimezone(timezone.utc).isoformat()
        packet_size = int(packet.length)

        src_ip = None
        dst_ip = None
        src_port = None
        dst_port = None
        protocol = packet.highest_layer

        # IPv4
        if hasattr(packet, "ip"):
            src_ip = packet.ip.src
            dst_ip = packet.ip.dst

        # IPv6
        elif hasattr(packet, "ipv6"):
            src_ip = packet.ipv6.src
            dst_ip = packet.ipv6.dst

        # Skip non-IP packets such as ARP
        else:
            return None

        # Transport layer detection
        if hasattr(packet, "tcp"):
            src_port = packet.tcp.srcport
            dst_port = packet.tcp.dstport
            protocol = "TCP"

        elif hasattr(packet, "udp"):
            src_port = packet.udp.srcport
            dst_port = packet.udp.dstport
            protocol = "UDP"

        elif hasattr(packet, "icmp"):
            protocol = "ICMP"

        elif hasattr(packet, "icmpv6"):
            protocol = "ICMPv6"

        return {
            "timestamp": timestamp,
            "src_ip": src_ip,
            "dst_ip": dst_ip,
            "protocol": protocol,
            "src_port": src_port,
            "dst_port": dst_port,
            "packet_size": packet_size
        }

    except Exception as error:
        print(f"Error extracting packet: {error}")
        return None


def main():
    """
       Main producer workflow.

       Initializes the asyncio event loop required by PyShark,
       creates a Kafka producer connection, starts live packet
       capture on the configured network interface, and streams
       packet metadata to the Kafka topic.

       For each captured packet:
           1. Extract packet metadata
           2. Convert metadata to a dictionary
           3. Publish the message to Kafka
           4. Track processing statistics

       After packet capture completes, the function flushes
       pending Kafka messages, closes producer resources,
       and displays summary statistics.

       Returns:
           None
       """

    # Create asyncio event loop required by PyShark
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Initialize Kafka producer connection
    producer = create_kafka_producer()

    capture = pyshark.LiveCapture(
        interface=INTERFACE,
        eventloop=loop
    )

    captured_count = 0
    published_count = 0
    skipped_count = 0

    print(f"Starting packet capture on interface: {INTERFACE}")
    print(f"Publishing packets to Kafka topic: {KAFKA_TOPIC}")

    for packet in capture.sniff_continuously(packet_count=PACKET_LIMIT):
        captured_count += 1

        packet_metadata = extract_packet_metadata(packet)

        if packet_metadata is None:
            skipped_count += 1

            try:
                print(f"Skipped packet layer: {packet.highest_layer}")
            except Exception:
                print("Skipped packet layer: unknown")

            continue

        # Publish packet metadata to Kafka topic
        producer.send(KAFKA_TOPIC, packet_metadata)
        published_count += 1

        print(f"Published packet: {packet_metadata}")

    try:
        capture.close()
    except Exception:
        pass

    # Ensure all pending messages are delivered
    producer.flush()
    producer.close()

    print("\nCapture complete.")
    print(f"Packets captured: {captured_count}")
    print(f"Packets published: {published_count}")
    print(f"Packets skipped: {skipped_count}")

    try:
        loop.run_until_complete(asyncio.sleep(0.1))
        loop.close()
    except Exception:
        pass


if __name__ == "__main__":
    main()