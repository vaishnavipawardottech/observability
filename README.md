# Observability Stack

A Docker Compose observability stack for monitoring the Asset Tracker
application and the host running it. The stack uses:

- **Prometheus** for collecting and querying metrics
- **Node Exporter** for host-level metrics
- **cAdvisor** for Docker container metrics
- **Grafana** for dashboards and visualization

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) with
  Docker Compose support
- Git
- Ports `3000`, `8080`, `9090`, and `9100` available on the host

## Project structure

```text
.
├── docker-compose.yml
├── prometheus.yml
├── grafana/
│   └── provisioning/
│       └── datasources/
│           └── datasources.yml
└── README.md
```

## Configuration

Create a local `.env` file from `.env_example` and update the values where
needed. The `.env` file contains the database, application, and Grafana
settings used by Docker Compose.

```bash
copy .env_example .env
```

Do not commit `.env` because it can contain passwords and application secrets.

## Start the stack

Clone the repository and change into the project directory:

```bash
git clone https://github.com/vaishnavipawardottech/observability.git
cd observability
copy .env_example .env
```

Start all services in the background:

```bash
docker compose up -d
```

Check the service status:

```bash
docker compose ps
```

## Services

| Service | URL | Purpose |
| --- | --- | --- |
| Prometheus | <http://localhost:9090> | Collects and queries metrics |
| Node Exporter | <http://localhost:9100/metrics> | Exposes host metrics |
| cAdvisor | <http://localhost:8080> | Shows Docker container metrics |
| Grafana | <http://localhost:3000> | Visualizes metrics in dashboards |

### Node Exporter: host metrics

Node Exporter exposes Linux host metrics such as CPU, memory, disk, filesystem,
and network usage. Its `/proc`, `/sys`, and root filesystem mounts are
read-only, so the exporter can collect metrics without modifying the host.

Node Exporter is configured as a Prometheus target in
[`prometheus.yml`](./prometheus.yml) using `node-exporter:9100`.

Open <http://localhost:9100/metrics> to verify that metrics are available.

![Node Exporter metrics](./screenshots/node-exporter.png)

Useful PromQL queries:

```promql
# CPU time by mode
node_cpu_seconds_total{mode="idle"}

# Memory usage percentage
(1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100

# Disk usage percentage for the root filesystem
(1 - node_filesystem_avail_bytes{mountpoint="/"} /
  node_filesystem_size_bytes{mountpoint="/"}) * 100

# Network receive rate
rate(node_network_receive_bytes_total[5m])
```

### cAdvisor: container metrics

cAdvisor monitors Docker container resource usage and performance. It
collects container CPU, memory, filesystem, and network metrics.

The Docker socket, `/sys`, and Docker data directory are mounted read-only so
cAdvisor can discover containers and read their statistics.

cAdvisor is also configured as a Prometheus target using `cadvisor:8080`.
Open <http://localhost:8080> to view the cAdvisor interface.

![cAdvisor container metrics](./screenshots/cadvisor.png)

Useful PromQL queries:

```promql
# CPU usage by container
rate(container_cpu_usage_seconds_total{name!=""}[5m])

# Memory usage by container
container_memory_usage_bytes{name!=""}

# Network receive rate by container
rate(container_network_receive_bytes_total{name!=""}[5m])

# Top three containers by memory usage
topk(3, container_memory_usage_bytes{name!=""})
```

The `{name!=""}` filter excludes aggregated entries and focuses on named
containers.

### Grafana: dashboards and visualization

Grafana provides dashboards for the metrics collected by Prometheus. The
Grafana service uses the `grafana_data` volume so dashboard data persists
when the container is recreated.

Open <http://localhost:3000> and sign in with the values configured in `.env`:

- Username: `grafyn_admin`
- Password: `grafyn_password`

The Prometheus datasource is provisioned automatically from
[`datasources.yml`](./grafana/provisioning/datasources/datasources.yml), so no
manual datasource setup is required. Grafana connects to Prometheus through
the Docker Compose network at `http://prometheus:9090`.

![Grafana dashboard](./screenshots/grafana.png)

## Create a dashboard

To create a simple overview dashboard:

1. Open Grafana and select **Dashboards > New dashboard**.
2. Add a visualization and select the **Prometheus** datasource.
3. Add panels using the queries below.
4. Save the dashboard as **DevOps Observability Overview**.

### CPU usage

```promql
100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
```

Use a Gauge visualization with the title **CPU Usage %**.

### Memory usage

```promql
(1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100
```

Use a Gauge visualization with the title **Memory Usage %**.

### Container CPU usage

```promql
rate(container_cpu_usage_seconds_total{name!=""}[5m]) * 100
```

Use a Time series visualization and the title **Container CPU Usage**.

### Container memory usage

```promql
container_memory_usage_bytes{name!=""} / 1024 / 1024
```

Use a Bar chart visualization and the title **Container Memory (MB)**.

### Disk usage

```promql
(1 - node_filesystem_avail_bytes{mountpoint="/"} /
  node_filesystem_size_bytes{mountpoint="/"}) * 100
```

Use a Stat visualization with the title **Disk Usage %**.

## Verify Prometheus targets

1. Open <http://localhost:9090>.
2. Go to **Status > Targets**.
3. Confirm that `prometheus`, `node-exporter`, and `cadvisor` are **UP**.
4. Open **Graph** and run a PromQL query.

Prometheus scrapes the configured targets every 15 seconds. The target names
use Docker Compose service names because the services share the
`asset-tracker-network` network.

## Stop the stack

Stop the containers without removing persistent data:

```bash
docker compose down
```

To remove the containers and named volumes:

```bash
docker compose down -v
```

## Troubleshooting

View logs for a specific service:

```bash
docker compose logs -f prometheus
docker compose logs -f node-exporter
docker compose logs -f cadvisor
docker compose logs -f grafana
```

If a target is not **UP**, confirm that all services are running with
`docker compose ps` and that the target uses the Compose service name rather
than `localhost`.
