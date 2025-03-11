from flask import Flask, jsonify
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.flask import FlaskInstrumentor
import requests
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

# Set up OpenTelemetry Tracing
trace.set_tracer_provider(TracerProvider(
    resource=Resource.create({SERVICE_NAME: "service:A"})
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

@app.route('/send', methods=['GET'])
def send_request():
    with tracer.start_as_current_span("send-request-span"):

        headers = {}
        propagator = TraceContextTextMapPropagator()
        propagator.inject(headers)
        
        # Send a request to Pod B
        response = requests.get('http://service-b/service-b', headers=headers)
        print("Response from service B: ", response)
        return jsonify({"status": "sent", "response": response.text})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


# To send the request to Pod B: curl -v http://127.0.0.1:5000/send