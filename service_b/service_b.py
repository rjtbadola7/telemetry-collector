from flask import Flask, jsonify, request
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.flask import FlaskInstrumentor
import time, requests
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

# Set up OpenTelemetry Tracing
trace.set_tracer_provider(TracerProvider(
    resource = Resource.create({
        SERVICE_NAME: "service:B"
    })
))

tracer = trace.get_tracer(__name__)


otlp_exporter = OTLPSpanExporter(
    #endpoint="http://otel-collector.default.svc.cluster.local:4318/v1/traces" # OTLPHTTP
    endpoint="http://otel-collector.default.svc.cluster.local:4317" # OTLPGRPC
)

span_processor_otlp = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor_otlp)

# Initialize Flask app
app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)

@app.route('/service-b', methods=['GET'])
def receive_request():

    propagator = TraceContextTextMapPropagator()
    context = propagator.extract(request.headers)
    tracer = trace.get_tracer(__name__)

    with tracer.start_as_current_span("receive-request-span", context=context):
        
        headers = {}
        propagator.inject(headers)

        # Process the request
        response = requests.get('http://service-c/service-c', headers=headers)
        time.sleep(10)
        print("Sending response back to service A")
        return jsonify({"status": "received"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)

# To send the request to Pod B: curl -v http://127.0.0.1:5001/service-b
