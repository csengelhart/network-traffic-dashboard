# Database Architecture

## Overview

The PostgreSQL database serves as the persistent storage layer for the
**Real-Time Network Traffic Security Monitoring Dashboard**. While
Apache Kafka provides high-speed streaming of packet metadata between
application components, PostgreSQL stores both raw packet data and
aggregated network metrics for historical analysis and dashboard
visualization.

The database currently consists of five primary tables:

-   `packet_events`
-   `traffic_metrics`
-   `protocol_metrics`
-   `top_talkers`
-   `port_activity`

These tables separate raw network events from summarized analytics,
allowing Grafana to efficiently visualize network traffic without
repeatedly querying every captured packet.

## Database Architecture Diagram

``` text
                 Kafka Consumer
                      │
                      ▼
              packet_events
                      │
                 analyzer.py
                      │
      ┌───────────────┼────────────────┐
      ▼               ▼                ▼
traffic_metrics  protocol_metrics  top_talkers
                      │
                      ▼
               port_activity
                      │
                      ▼
                  Grafana
```

## Table Responsibilities

### packet_events

Stores every captured packet from the network. This table acts as the
source of truth for all downstream analysis.

**Columns**

| Column      | Description                               |
| ----------- | ----------------------------------------- |
| event_id    | Unique packet identifier                  |
| timestamp   | Packet capture time (UTC)                 |
| src_ip      | Source IP address                         |
| dst_ip      | Destination IP address                    |
| protocol    | Network protocol (TCP, UDP, ICMP, ICMPv6) |
| src_port    | Source port number                        |
| dst_port    | Destination port number                   |
| packet_size | Packet size in bytes                      |


### traffic_metrics

Stores overall network traffic statistics for each analysis window.

**Metrics** - Packet count - Total bytes - Packets per second - Bytes
per second

------------------------------------------------------------------------

### protocol_metrics

Stores packet counts and byte totals grouped by protocol.

------------------------------------------------------------------------

### top_talkers

Stores the most active source IP addresses for each analysis window.

------------------------------------------------------------------------

### port_activity

Stores packet counts and byte totals grouped by destination port and
protocol.

