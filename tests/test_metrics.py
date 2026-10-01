import re
from fastapi.testclient import TestClient
from app.main import app

client=TestClient(app)

def metrics(): return client.get('/metrics').text
def test_health(): assert client.get('/health').json()['status']=='ok'
def test_work_success(): assert client.get('/work/123').status_code==200
def test_delay_bound_rejected(): assert client.get('/work/1?delay_ms=2001').status_code==422
def test_controlled_failure(): assert client.get('/work/1?fail=true').status_code==503
def test_metrics_content_type(): assert 'text/plain' in client.get('/metrics').headers['content-type']
def test_counter_present(): assert 'http_requests_total' in metrics()
def test_histogram_present(): assert 'http_request_duration_seconds_bucket' in metrics()
def test_process_cpu_present(): assert 'demo_process_cpu_seconds_total' in metrics()
def test_process_memory_present(): assert 'demo_process_resident_memory_bytes' in metrics()
def test_service_status_present(): assert 'demo_service_status 1.0' in metrics()
def test_metrics_endpoint_excluded(): assert 'route="/metrics"' not in metrics()
def test_template_route_not_raw_id():
    client.get('/work/987'); text=metrics(); assert 'route="/work/{item_id}"' in text and 'route="/work/987"' not in text
def test_503_counted():
    client.get('/work/2?fail=true'); assert re.search(r'http_requests_total\{method="GET",route="/work/\{item_id\}",status="503"\}',metrics())

