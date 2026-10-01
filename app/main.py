from __future__ import annotations

import asyncio
import os
import time

import psutil
from fastapi import FastAPI, HTTPException, Query, Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, REGISTRY, generate_latest

app = FastAPI(title="Observable Demo Service", version="1.0.0")

REQUESTS = Counter("http_requests_total", "HTTP requests", ["method", "route", "status"])
LATENCY = Histogram("http_request_duration_seconds", "HTTP latency seconds", ["method", "route"], buckets=(.01,.025,.05,.1,.25,.5,1,2,5))
INFLIGHT = Gauge("http_requests_inflight", "Current in-flight requests")
SERVICE_UP = Gauge("demo_service_status", "Application status where 1 is ready")
PROCESS_CPU = Gauge("demo_process_cpu_seconds_total", "Process CPU seconds")
PROCESS_MEMORY = Gauge("demo_process_resident_memory_bytes", "Process resident memory bytes")
SERVICE_UP.set(1)


def route_label(request: Request) -> str:
    route = request.scope.get("route")
    return getattr(route, "path", "unmatched")


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

