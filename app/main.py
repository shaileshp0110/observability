import logging
import random
import time

from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from prometheus_fastapi_instrumentator import Instrumentator

# 🌍 OpenTelemetry Tracing Setup
tracer_provider = TracerProvider()
# tracer_provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint="http://otel-collector:4317")))
tracer_provider.add_span_processor(
    BatchSpanProcessor(
        OTLPSpanExporter(endpoint="tempo:4317", insecure=True)
    )
)
trace.set_tracer_provider(tracer_provider)

tracer = trace.get_tracer(__name__)

# 🎯 FastAPI App
app = FastAPI()
FastAPIInstrumentor.instrument_app(app)
Instrumentator().instrument(app).expose(app)


# 📝 Logging Setup (Sent to Loki)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.get("/")
async def read_root():
    with tracer.start_as_current_span("root_request") as span:
        # Add attributes to the span
        span.set_attribute("endpoint", "/")
        span.set_attribute("handler", "read_root")
        logger.info("****************http://tempo:55680****************")
        logger.info("User accessed /")
        return {"message": "Hello World"}

@app.get("/slow")
async def slow_request():
    with tracer.start_as_current_span("slow_request") as span:
        start = time.time()
        
        # Add initial span attributes
        span.set_attribute("endpoint", "/slow")
        span.set_attribute("handler", "slow_request")
        
        # Simulate slow processing with a child span
        with tracer.start_span("processing") as child_span:
            time.sleep(random.uniform(0.5, 2.0))
            duration = round(time.time() - start, 2)
            child_span.set_attribute("duration_seconds", duration)
        
        logger.info(f"Slow request completed - duration: {duration}s")
        return {"message": "Slow request done", "duration": duration}
