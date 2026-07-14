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

def insert_security_alert(
    connection,
    alert_timestamp,
    alert_type,
    severity,
    source_ip,
    destination_ip,
    destination_port,
    description
):
    """
    Inserts one detected security alert into PostgreSQL.
    """

    query = """
        INSERT INTO security_alerts (
            alert_timestamp,
            alert_type,
            severity,
            source_ip,
            destination_ip,
            destination_port,
            description
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s);
    """

    values = (
        alert_timestamp,
        alert_type,
        severity,
        source_ip,
        destination_ip,
        destination_port,
        description
    )

    with connection.cursor() as cursor:
        cursor.execute(query, values)

    connection.commit()

def get_known_device(connection, ip_address):
    """
    Returns a known device record for an IP address, or None if it is new.
    """

    query = """
        SELECT device_id, ip_address, first_seen, last_seen
        FROM known_devices
        WHERE ip_address = %s;
    """

    with connection.cursor() as cursor:
        cursor.execute(query, (ip_address,))
        return cursor.fetchone()

def insert_known_device(connection, ip_address, first_seen):
    """
    Inserts a newly observed IP address into the known_devices table.
    """

    query = """
        INSERT INTO known_devices (
            ip_address,
            first_seen,
            last_seen
        )
        VALUES (%s, %s, %s);
    """

    with connection.cursor() as cursor:
        cursor.execute(query, (ip_address, first_seen, first_seen))

    connection.commit()

def update_device_last_seen(connection, ip_address, last_seen):
    """
    Updates the last observed timestamp for a known device.
    """

    query = """
        UPDATE known_devices
        SET last_seen = %s
        WHERE ip_address = %s;
    """

    with connection.cursor() as cursor:
        cursor.execute(query, (last_seen, ip_address))

    connection.commit()

def get_recent_average_packet_rate(connection, before_time, limit=5):
    """
    Returns the average packet rate from recent completed traffic windows.
    """

    query = """
        SELECT AVG(packets_per_second)
        FROM (
            SELECT packets_per_second
            FROM traffic_metrics
            WHERE window_end < %s
            ORDER BY window_end DESC
            LIMIT %s
        ) AS recent_windows;
    """

    with connection.cursor() as cursor:
        cursor.execute(query, (before_time, limit))
        result = cursor.fetchone()

    return float(result[0]) if result and result[0] is not None else None

