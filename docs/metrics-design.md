# 指标设计

| 运维问题 | 指标 | 类型 | 单位 | 标签 | 约束 |
|---|---|---|---|---|---|
| 服务是否可达 | `up` | Gauge | 0/1 | job instance environment | Prometheus 自动生成 |
| 流量何时变化 | `http_requests_total` | Counter | requests | method route status | route 是模板路径 |
| 尾部延迟是否升高 | `http_request_duration_seconds` | Histogram | seconds | method route le | 固定桶至 5 秒 |
| 当前并发多少 | `http_requests_inflight` | Gauge | requests | 无 | 不记录用户 |
| 进程消耗多少 CPU | `demo_process_cpu_seconds_total` | Gauge 快照 | CPU seconds | job instance | 当前应用进程 |
| 进程使用多少内存 | `demo_process_resident_memory_bytes` | Gauge | bytes | job instance | RSS，不是整机 |

高基数审查：不使用用户 ID、item_id、查询串、原始 URL、异常消息或关联 ID作为标签。`/work/{item_id}` 的所有实例都归并到同一模板路由。CPU 查询 `rate(...[1m])` 的单位是 CPU 核，不是整机百分比。

