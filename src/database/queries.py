"""
queries.py

Contains SQL query helper functions for inserting packet data into PostgreSQL.
"""


def insert_packet_event(connection, packet):
    """
    Inserts one packet metadata record into the packet_events table.
    """

    query = """
        INSERT INTO packet_events (
            timestamp,
            src_ip,
            dst_ip,
            protocol,
            src_port,
            dst_port,
            packet_size
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s);
    """

    values = (
        packet.get("timestamp"),
        packet.get("src_ip"),
        packet.get("dst_ip"),
        packet.get("protocol"),
        int(packet["src_port"]) if packet.get("src_port") else None,
        int(packet["dst_port"]) if packet.get("dst_port") else None,
        int(packet["packet_size"]) if packet.get("packet_size") else None
    )

    with connection.cursor() as cursor:
        cursor.execute(query, values)

    connection.commit()

def get_packets_for_time_window(connection, window_start, window_end):
    """
    Retrieves packets from packet_events within a specific time window.
    """
    query = """
        SELECT timestamp, src_ip, dst_ip, protocol, src_port, dst_port, packet_size
        FROM packet_events
        WHERE timestamp >= %s
          AND timestamp < %s;
    """

    with connection.cursor() as cursor:
        cursor.execute(query, (window_start, window_end))
        return cursor.fetchall()


def insert_traffic_metrics(connection, window_start, window_end, packet_count, total_bytes):
    """
    Inserts overall traffic metrics for one analysis time window.

    Calculates packet and byte rates from the window duration, then stores
    total packet count, total bytes, packets per second, and bytes per second.
    """
    duration_seconds = (window_end - window_start).total_seconds()

    packets_per_second = packet_count / duration_seconds if duration_seconds > 0 else 0
    bytes_per_second = total_bytes / duration_seconds if duration_seconds > 0 else 0

    query = """
        INSERT INTO traffic_metrics (
            window_start,
            window_end,
            packet_count,
            total_bytes,
            packets_per_second,
            bytes_per_second
        )
        VALUES (%s, %s, %s, %s, %s, %s);
    """

    values = (
        window_start,
        window_end,
        packet_count,
        total_bytes,
        packets_per_second,
        bytes_per_second
    )

    with connection.cursor() as cursor:
        cursor.execute(query, values)

    connection.commit()

def insert_protocol_metric(connection, window_start, window_end, protocol, packet_count, total_bytes):
    """
    Inserts protocol-level traffic metrics for one analysis time window.

    Stores the packet count and byte total for a specific protocol such as
    TCP, UDP, ICMP, or ICMPv6.
    """
    query = """
        INSERT INTO protocol_metrics (
            window_start,
            window_end,
            protocol,
            packet_count,
            total_bytes
        )
        VALUES (%s, %s, %s, %s, %s);
    """

    values = (
        window_start,
        window_end,
        protocol,
        packet_count,
        total_bytes
    )

    with connection.cursor() as cursor:
        cursor.execute(query, values)

    connection.commit()

def insert_top_talker(connection, window_start, window_end, src_ip, packet_count, total_bytes):
    """
    Inserts top talker metrics for one source IP within a time window.

    Stores how many packets and bytes were sent by a source IP so active
    devices can be ranked by traffic volume.
    """
    query = """
        INSERT INTO top_talkers (
            window_start,
            window_end,
            src_ip,
            packet_count,
            total_bytes
        )
        VALUES (%s, %s, %s, %s, %s);
    """

    values = (
        window_start,
        window_end,
        src_ip,
        packet_count,
        total_bytes
    )

    with connection.cursor() as cursor:
        cursor.execute(query, values)

    connection.commit()

def insert_port_activity(connection, window_start, window_end, dst_port, protocol, packet_count, total_bytes):
    """
    Inserts destination port activity metrics for one analysis time window.

    Stores packet and byte totals for a destination port and protocol pair,
    supporting analysis of commonly used services and ports.
    """
    query = """
        INSERT INTO port_activity (
            window_start,
            window_end,
            dst_port,
            protocol,
            packet_count,
            total_bytes
        )
        VALUES (%s, %s, %s, %s, %s, %s);
    """

    values = (
        window_start,
        window_end,
        dst_port,
        protocol,
        packet_count,
        total_bytes
    )

    with connection.cursor() as cursor:
        cursor.execute(query, values)

    connection.commit()