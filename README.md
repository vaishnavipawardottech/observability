# Observability Stack

A small, extendable observability environment built with Docker Compose and
[Prometheus](https://prometheus.io/). This project is the foundation for
adding more monitoring and observability components over the coming days.

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) with
  Docker Compose support
- A browser
- Port `9090` available on the host

## Start Prometheus

Clone the repository and change into the project directory:

```bash
git clone https://github.com/vaishnavipawardottech/observability.git
cd observability
```

Start the stack in the background:

```bash
docker compose up -d
```

Prometheus is available at:

<http://localhost:9090>

To stop the stack:

```bash
docker compose down
```

The named `prometheus_data` volume keeps Prometheus data when the container is
recreated. To remove the container and its stored data, use:

```bash
docker compose down -v
```

## Verify the installation

1. Open <http://localhost:9090>.
2. Go to **Status > Targets**.
3. Confirm that the `prometheus` target has state **UP**.
4. Open **Graph** or <http://localhost:9090/graph> and run a PromQL query.

The configuration scrapes Prometheus itself every 15 seconds. The target is
configured as `prometheus:9090` because Prometheus connects to the service over
the Docker Compose network.

## Useful PromQL queries

Run these queries in the Prometheus expression browser:

```promql
# Count all metric series currently collected by Prometheus
count({__name__=~".+"})

# Check Prometheus memory usage in bytes
process_resident_memory_bytes

# Total HTTP requests received by Prometheus
prometheus_http_requests_total

# Filter requests handled by a specific endpoint
prometheus_http_requests_total{handler="/api/v1/query"}

# View the number of active scrape targets
prometheus_target_scrape_pool_targets

# Check whether each target is reachable (1 = up, 0 = down)
up

# Calculate the request rate over the last five minutes
rate(prometheus_http_requests_total[5m])
```

## Prometheus concepts

### Scrape targets

Prometheus uses a pull-based model. At a configured interval, it requests
metrics from each scrape target and stores the returned time series.

### Metric types

- **Counter**: A value that only increases, such as total requests or errors.
- **Gauge**: A value that can increase or decrease, such as memory usage or
  active connections.
- **Histogram**: Observations grouped into configurable buckets, useful for
  request duration and size distributions.
- **Summary**: Observations that calculate quantiles on the client side.

### Labels and time series

Labels add dimensions to a metric:

```promql
http_requests_total{method="GET", status="200"}
```

A time series is identified by its metric name and its complete set of label
key-value pairs. Adding high-cardinality labels, such as unique request IDs,
can significantly increase storage and query costs.

## Project structure

```text
.
├── docker-compose.yml  # Prometheus service and persistent data volume
├── prometheus.yml      # Scrape interval and target configuration
└── README.md           # Setup and usage guide
```

## Configuration

The main settings are defined in [`prometheus.yml`](./prometheus.yml):

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
```

- `scrape_interval` controls how often targets are scraped.
- `evaluation_interval` controls how often recording and alerting rules are
  evaluated. No rules are configured yet.

The Compose definition in [`docker-compose.yml`](./docker-compose.yml) maps
the local configuration into the container and exposes Prometheus on port
`9090`.

After changing the configuration, recreate the service:

```bash
docker compose up -d
```

To inspect service logs:

```bash
docker compose logs -f prometheus
```

## Next steps

- Add application exporters and scrape them from Prometheus.
- Add alerting rules for availability and resource thresholds.
- Configure Alertmanager for notifications.
- Add Grafana for dashboards and visualization.
