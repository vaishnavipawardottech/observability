from opentelemetry import trace, metrics
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter

resource = Resource.create({"service.name": "day76-test"})

trace_provider = TracerProvider(resource=resource)
trace_provider.add_span_processor(
    BatchSpanProcessor(
        OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True)
    )
)
trace.set_tracer_provider(trace_provider)

tracer = trace.get_tracer("day76-test")

with tracer.start_as_current_span("day76-test-span"):
    print("Test trace sent")

metric_reader = PeriodicExportingMetricReader(
    OTLPMetricExporter(endpoint="http://localhost:4317", insecure=True),
    export_interval_millis=1000,
)

metrics.set_meter_provider(MeterProvider(
    resource=resource,
    metric_readers=[metric_reader],
))

meter = metrics.get_meter("day76-test")
counter = meter.create_counter("test_requests_total")
counter.add(42, {"test": "day76"})

import time
time.sleep(3)

trace_provider.shutdown()
metrics.get_meter_provider().shutdown()