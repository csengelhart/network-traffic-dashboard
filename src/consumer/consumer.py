"""
consumer.py

Reads packet metadata from Kafka and stores packet events in PostgreSQL.
"""

import json
import sys
from pathlib import Path

from kafka import KafkaConsumer

# Allows imports from src/database when running from project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

from src.database.database import create_db_connection
from src.database.queries import insert_packet_event


KAFKA_TOPIC = "network-packets"
KAFKA_BOOTSTRAP_SERVER = "127.0.0.1:9092"
CONSUMER_GROUP_ID = "network-monitor-consumer"


def create_kafka_consumer():
    """
    Creates and returns a Kafka consumer for packet metadata messages.
    """
    return KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=[KAFKA_BOOTSTRAP_SERVER],
        value_deserializer=lambda value: json.loads(value.decode("utf-8")),
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id=CONSUMER_GROUP_ID
    )


def main():
    """
    Runs the Kafka consumer workflow.

    Reads packet metadata from Kafka and inserts each packet record into PostgreSQL.
    """
    consumer = create_kafka_consumer()
    connection = create_db_connection()

    inserted_count = 0

    print("Consumer started.")
    print(f"Reading from Kafka topic: {KAFKA_TOPIC}")
    print("Writing packet events to PostgreSQL...")

    try:
        for message in consumer:
            packet = message.value
            insert_packet_event(connection, packet)
            inserted_count += 1

            print(f"Inserted packet #{inserted_count}: {packet}")

    except KeyboardInterrupt:
        print("\nConsumer stopped by user.")

    finally:
        consumer.close()
        connection.close()
        print(f"Total packets inserted: {inserted_count}")
        print("Consumer and database connection closed.")


if __name__ == "__main__":
    main()