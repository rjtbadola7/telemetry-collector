from flask import Flask, jsonify
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.flask import FlaskInstrumentor
import  time
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

#attributes = dict(attr.split('=') for attr in resource_attributes.split(','))
#print(attributes)
# Set up OpenTelemetry Tracing
trace.set_tracer_provider(TracerProvider(
    resource = Resource.create({
        SERVICE_NAME: "service:C"
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

@app.route('/service-c', methods=['GET'])
def receive_request():

    propagator = TraceContextTextMapPropagator()
    context = propagator.extract(request.headers)
    tracer = trace.get_tracer(__name__)

    with tracer.start_as_current_span("receive-request-span", context=context):
        # Process the request
        time.sleep(5)
        print("Sending response back to service B")
        return jsonify({"status": "received"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)