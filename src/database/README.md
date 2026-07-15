## Database Initialization

After starting the Docker containers, initialize the PostgreSQL schema.

### 1. Start Docker

```powershell
docker compose up -d
```

### 2. Create the database tables

```powershell
Get-Content src\database\schema.sql | docker exec -i network_postgres psql -U postgres -d network_monitor
```

This command creates all required database tables:

- packet_events
- traffic_metrics
- protocol_metrics
- top_talkers
- port_activity
- security_alerts
- known_devices

**Note**: The schema uses `CREATE TABLE IF NOT EXISTS`, so the command is safe to run multiple times.