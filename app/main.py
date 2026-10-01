from __future__ import annotations

import asyncio
import os
import time

import psutil
from fastapi import FastAPI, HTTPException, Query, Request, Response
from fastapi.responses import HTMLResponse
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, REGISTRY, generate_latest

app = FastAPI(title="Observable Demo Service", version="1.0.0")

REQUESTS = Counter("http_requests_total", "HTTP requests", ["method", "route", "status"])
LATENCY = Histogram("http_request_duration_seconds", "HTTP latency seconds", ["method", "route"], buckets=(.01,.025,.05,.1,.25,.5,1,2,5))
INFLIGHT = Gauge("http_requests_inflight", "Current in-flight requests")
SERVICE_UP = Gauge("demo_service_status", "Application status where 1 is ready")
PROCESS_CPU = Gauge("demo_process_cpu_seconds_total", "Process CPU seconds")
PROCESS_MEMORY = Gauge("demo_process_resident_memory_bytes", "Process resident memory bytes")
SERVICE_UP.set(1)

DASHBOARD_PREVIEW = r"""<!doctype html><html lang='zh-CN'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>服务指标预览</title><style>
body{font-family:system-ui;background:#0b1020;color:#e8eefc;margin:0}.wrap{max-width:1100px;margin:auto;padding:40px}.top{display:flex;justify-content:space-between;align-items:center}.badge{background:#143a2a;color:#6ee7a2;padding:8px 13px;border-radius:20px}.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}.card{background:#151d33;border:1px solid #293653;border-radius:14px;padding:20px}.value{font-size:30px;font-weight:700;color:#79a7ff}.wide{grid-column:span 2}pre{white-space:pre-wrap;color:#aab8d5;font-size:12px;max-height:220px;overflow:auto}@media(max-width:750px){.grid{grid-template-columns:1fr}.wide{grid-column:auto}}</style></head><body><div class='wrap'><div class='top'><div><h1>服务可观测性指标预览</h1><p>FastAPI /metrics · Prometheus 与 Grafana 配置见仓库</p></div><span class='badge'>● 服务运行中</span></div><div class='grid'><div class='card'><h3>服务状态</h3><div class='value'>UP</div><p>demo_service_status = 1</p></div><div class='card'><h3>请求指标</h3><div class='value'>Counter</div><p>按 method route status 分组</p></div><div class='card'><h3>延迟指标</h3><div class='value'>Histogram</div><p>0.01 s 至 5 s 固定桶</p></div><div class='card'><h3>进程 CPU</h3><div class='value'>CPU seconds</div><p>rate 后表示使用的 CPU 核</p></div><div class='card'><h3>进程内存</h3><div class='value'>RSS bytes</div><p>当前应用进程，不是整机</p></div><div class='card'><h3>标签边界</h3><div class='value'>有界</div><p>不包含用户 ID 或原始 URL</p></div><div class='card wide'><h3>实时指标节选</h3><pre id='raw'>加载中…</pre></div><div class='card'><h3>受控异常</h3><p><a style='color:#79a7ff' href='/work/1?delay_ms=150'>150 ms 请求</a></p><p><a style='color:#79a7ff' href='/work/1?fail=true'>受控 503</a></p><p><a style='color:#79a7ff' href='/docs'>OpenAPI</a></p></div></div></div><script>fetch('/metrics').then(r=>r.text()).then(t=>{document.querySelector('#raw').textContent=t.split('\n').filter(x=>x.includes('demo_')||x.includes('http_requests_total')).slice(0,24).join('\n')})</script></body></html>"""


def route_label(request: Request) -> str:
    route = request.scope.get("route")
    return getattr(route, "path", "unmatched")


@app.get("/", response_class=HTMLResponse)
def dashboard_preview(): return DASHBOARD_PREVIEW


@app.middleware("http")
async def metrics(request: Request, call_next):
    if request.url.path == "/metrics": return await call_next(request)
    start = time.perf_counter(); status = 500; INFLIGHT.inc()
    try:
        response = await call_next(request); status = response.status_code; return response
    except Exception:
        status = 500; raise
    finally:
        route = route_label(request)
        REQUESTS.labels(request.method, route, str(status)).inc()
        LATENCY.labels(request.method, route).observe(time.perf_counter()-start)
        INFLIGHT.dec()


@app.get("/health")
def health(): return {"status":"ok","version":"1.0.0"}


@app.get("/work/{item_id}")
async def work(item_id: int, delay_ms: int = Query(0, ge=0, le=2000), fail: bool = False):
    if delay_ms: await asyncio.sleep(delay_ms/1000)
    if fail: raise HTTPException(503,"controlled failure")
    return {"item_id":item_id,"delay_ms":delay_ms,"status":"done"}


@app.get("/metrics",include_in_schema=False)
def metrics_endpoint():
    process=psutil.Process(os.getpid()); cpu=process.cpu_times()
    PROCESS_CPU.set(cpu.user+cpu.system); PROCESS_MEMORY.set(process.memory_info().rss)
    return Response(generate_latest(REGISTRY),headers={"Content-Type":CONTENT_TYPE_LATEST})

