-- ============================================================
-- Network Traffic Security Monitoring Dashboard
-- PostgreSQL Database Schema
-- ============================================================

CREATE TABLE IF NOT EXISTS packet_events (
    event_id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    src_ip TEXT NOT NULL,
    dst_ip TEXT NOT NULL,
    protocol TEXT NOT NULL,
    src_port INTEGER,
    dst_port INTEGER,
    packet_size INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS traffic_metrics (
    metric_id SERIAL PRIMARY KEY,
    window_start TIMESTAMPTZ NOT NULL,
    window_end TIMESTAMPTZ NOT NULL,
    packet_count INTEGER NOT NULL,
    total_bytes BIGINT NOT NULL,
    packets_per_second NUMERIC NOT NULL,
    bytes_per_second NUMERIC NOT NULL
);

CREATE TABLE IF NOT EXISTS protocol_metrics (
    metric_id SERIAL PRIMARY KEY,
    window_start TIMESTAMPTZ NOT NULL,
    window_end TIMESTAMPTZ NOT NULL,
    protocol TEXT NOT NULL,
    packet_count INTEGER NOT NULL,
    total_bytes BIGINT NOT NULL
);

CREATE TABLE IF NOT EXISTS top_talkers (
    metric_id SERIAL PRIMARY KEY,
    window_start TIMESTAMPTZ NOT NULL,
    window_end TIMESTAMPTZ NOT NULL,
    src_ip TEXT NOT NULL,
    packet_count INTEGER NOT NULL,
    total_bytes BIGINT NOT NULL
);

CREATE TABLE IF NOT EXISTS port_activity (
    metric_id SERIAL PRIMARY KEY,
    window_start TIMESTAMPTZ NOT NULL,
    window_end TIMESTAMPTZ NOT NULL,
    dst_port INTEGER NOT NULL,
    protocol TEXT NOT NULL,
    packet_count INTEGER NOT NULL,
    total_bytes BIGINT NOT NULL
);

CREATE TABLE IF NOT EXISTS security_alerts (
    alert_id SERIAL PRIMARY KEY,
    alert_timestamp TIMESTAMPTZ NOT NULL,
    alert_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    source_ip TEXT,
    destination_ip TEXT,
    destination_port INTEGER,
    description TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS known_devices (
    device_id SERIAL PRIMARY KEY,
    ip_address TEXT UNIQUE NOT NULL,
    first_seen TIMESTAMPTZ NOT NULL,
    last_seen TIMESTAMPTZ NOT NULL
);