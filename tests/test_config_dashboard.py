import json
from pathlib import Path

ROOT=Path(__file__).parents[1]
PROM=(ROOT/'prometheus/prometheus.yml').read_text(encoding='utf-8')
RULES=(ROOT/'prometheus/rules.yml').read_text(encoding='utf-8')
DASH=json.loads((ROOT/'grafana/dashboards/observability.json').read_text(encoding='utf-8'))

def test_scrape_interval(): assert 'scrape_interval: 5s' in PROM
def test_target_and_metrics_path(): assert '127.0.0.1:8008' in PROM and 'metrics_path: /metrics' in PROM
def test_rule_file_linked(): assert 'rules.yml' in PROM
def test_down_alert_has_for(): assert 'DemoServiceDown' in RULES and 'for: 1m' in RULES
def test_error_alert_has_window(): assert 'http_requests_total' in RULES and '[5m]' in RULES and 'for: 2m' in RULES
def test_six_panels(): assert len(DASH['panels'])==6
def test_panel_titles(): assert {'服务状态','请求速率','状态码和错误率','请求延迟 p50 p95','进程 CPU','进程内存'}=={p['title'] for p in DASH['panels']}
def test_p95_query(): assert any('histogram_quantile(0.95' in t['expr'] for p in DASH['panels'] for t in p['targets'])
def test_rate_windows_present(): assert any('[1m]' in t['expr'] for p in DASH['panels'] for t in p['targets']) and any('[5m]' in t['expr'] for p in DASH['panels'] for t in p['targets'])
def test_no_high_cardinality_labels():
    text=json.dumps(DASH,ensure_ascii=False); assert 'user_id' not in text and 'item_id' not in text and 'request_id' not in text
def test_units_and_no_data(): assert all('noValue' in p.get('fieldConfig',{}).get('defaults',{}) for p in DASH['panels'])
def test_job_variable(): assert DASH['templating']['list'][0]['name']=='job'

