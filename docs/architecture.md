# Overall Project Architecture

**Network Interface**

        ↓
**PyShark Packet Capture**

        ↓
**Kafka Producer**

        ↓
**Kafka Topic: network-packets**

        ↓
**Python Consumer**

        ↓

**PostgreSQL**

        ↓
**Grafana Dashboard**