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