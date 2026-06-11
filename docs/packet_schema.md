# Packet Message Schema

Each captured network packet is converted into a JSON message and published to the Kafka topic `network-packets`.

## Message Format

```json
{
  "timestamp": "2026-06-10T23:44:35.080881+00:00",
  "src_ip": "10.0.0.210",
  "dst_ip": "52.191.97.148",
  "protocol": "TCP",
  "src_port": "52184",
  "dst_port": "443",
  "packet_size": 1494
}
```

## Supported Protocols

The packet producer currently supports:

* IPv4
* IPv6
* TCP
* UDP
* ICMP
* ICMPv6

## Field Descriptions

| Field       | Description                                 |
| ----------- | ------------------------------------------- |
| timestamp   | UTC timestamp when the packet was captured  |
| src_ip      | Source IPv4 or IPv6 address                 |
| dst_ip      | Destination IPv4 or IPv6 address            |
| protocol    | Transport protocol (TCP, UDP, ICMP, ICMPv6) |
| src_port    | Source port number when applicable          |
| dst_port    | Destination port number when applicable     |
| packet_size | Total packet size in bytes                  |

## Example IPv6 Packet

```json
{
  "timestamp": "2026-06-11T00:37:49.695708+00:00",
  "src_ip": "2001:4860:482c:7700::",
  "dst_ip": "2601:441:8401:e9f0:c5ee:6633:c05d:8ac9",
  "protocol": "TCP",
  "src_port": "443",
  "dst_port": "55829",
  "packet_size": 1294
}
```
