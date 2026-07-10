# Overall project architecture

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