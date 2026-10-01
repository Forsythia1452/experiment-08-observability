# 测试和异常记录

执行 `.\.venv\Scripts\python.exe -m pytest -q`。测试覆盖健康检查、成功和受控 503、延迟上限、Counter、Histogram、CPU、内存、服务状态、metrics 自身排除、模板路由标签、Prometheus 抓取配置、两条告警、六面板、p95、窗口、单位和高基数审查。

受控异常命令：

```powershell
.\.venv\Scripts\python.exe scripts\load.py --count 60 --concurrency 4 --delay-ms 150 --fail-every 10
```

安全限制：最多 500 请求、20 并发、2000 ms 延迟，默认只访问 `127.0.0.1:8008`。预期 54 个 200、6 个 503；请求速率上升，p95 接近 0.25 秒桶，错误率约 10%。停止应用后 Prometheus 下一轮抓取 `up=0`，持续一分钟进入 Firing；恢复后回到 Resolved。

当前工作区未安装 Prometheus 和 Grafana 原生二进制，也没有可用 Docker daemon，因此本机验证到应用 `/metrics`、配置结构、PromQL 和 Dashboard JSON。配置固定 3.14.0 / 13.2.1 格式，复核者需要按 README 下载官方二进制后执行 `promtool check config` 和 Grafana provisioning。

