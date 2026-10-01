# 实验 8 软件运行监控与可观测性平台

为本地 FastAPI 服务设计埋点、Prometheus 抓取与告警，并提供自主 Grafana 六面板 Dashboard。作者：侯宇晴，23120506154，软件2304。

## 架构

```mermaid
flowchart LR
  L[受控负载脚本] --> A[FastAPI 8008]
  A -->|metrics| P[Prometheus 9090]
  P --> Q[PromQL 和告警]
  Q --> G[Grafana 3000]
  G --> D[六面板 Dashboard]
```

应用提供健康、受控延迟/错误和 `/metrics`。Prometheus 每 5 秒抓取并计算 rate、错误率和分位数；Grafana 只查询 Prometheus，不直接访问应用。

## 安装和课堂前半段

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\scripts\start-app.ps1
Invoke-WebRequest http://127.0.0.1:8008/metrics
```

下载官方 Prometheus 3.14.0 Windows ZIP，把 `prometheus/prometheus.yml` 和 `rules.yml` 放入其工作目录，执行：

```powershell
.\promtool.exe check config .\prometheus.yml
.\promtool.exe check rules .\rules.yml
.\prometheus.exe --config.file=.\prometheus.yml --storage.tsdb.path=.\data --web.listen-address=127.0.0.1:9090
```

Targets 应显示 `demo-app` 为 UP。核心查询：

```promql
up{job="demo-app"}
sum(rate(http_requests_total{job="demo-app"}[1m]))
sum(rate(http_requests_total{job="demo-app",status=~"5.."}[5m])) / clamp_min(sum(rate(http_requests_total{job="demo-app"}[5m])), 0.001)
histogram_quantile(0.95, sum by (le) (rate(http_request_duration_seconds_bucket{job="demo-app"}[5m])))
rate(demo_process_cpu_seconds_total{job="demo-app"}[1m])
demo_process_resident_memory_bytes{job="demo-app"}
```

## Grafana 和课堂后半段

使用 Grafana OSS 13.2.1。将 `grafana/provisioning` 指定为 provisioning 路径，或手工添加 `http://127.0.0.1:9090` 数据源并导入 `grafana/dashboards/observability.json`。Dashboard 有服务状态、请求速率、状态码/错误率、p50/p95、进程 CPU、进程内存六个面板，默认最近 15 分钟、每 5 秒刷新。

## 受控异常

```powershell
.\.venv\Scripts\python.exe scripts\load.py --count 60 --concurrency 4 --delay-ms 150 --fail-every 10
```

脚本只压测本人回环应用，并限制最多 500 请求、20 并发和 2 秒延迟。停止应用一分钟验证 `DemoServiceDown` 的 Pending/Firing，再启动观察恢复。CPU 与 p95 同时升高只能说明时间相关，不能单独证明 CPU 是根因，还需剖析、日志和资源饱和证据。

## 测试和复现边界

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

本机没有可用 Docker daemon，也未安装 Prometheus/Grafana 原生二进制；已验证应用、指标语义、配置文件、PromQL 字符串、告警门槛和 Dashboard JSON。完整组件启动步骤保留在上文，不能把配置测试表述成已经运行 Grafana。详细证据见 `docs/TESTING.md`。

## 指标边界和许可证

进程 CPU 是累计 CPU 秒，`rate(...[1m])` 表示使用的 CPU 核；RSS 是应用进程内存，不是整机资源。标签不含用户 ID、item_id 或原始 URL。指标设计见 `docs/metrics-design.md`。Prometheus、Grafana 和客户端的来源与许可证见 `NOTICE.md`；Grafana 网络部署需遵守 AGPL-3.0。

上游提供抓取、存储、查询和绘图；本人实现业务埋点、受控故障、PromQL、Dashboard、规则、配置和测试。开发使用 `feature/observability-dashboard`、Issue、PR 和文字自审。

