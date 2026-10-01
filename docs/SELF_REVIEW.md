# Pull Request 自审

- [x] Counter、Gauge 和 Histogram 的名称、单位与标签有设计表。
- [x] 请求标签使用模板路由，不含 ID、查询串或异常文本。
- [x] metrics 自身不计入业务流量。
- [x] 业务异常按 5xx 状态计数，延迟在 finally 路径记录。
- [x] Prometheus 抓取、规则文件和窗口固定。
- [x] 六个自主面板覆盖 up、速率、错误、p50/p95、CPU 和内存。
- [x] 面板具备单位、Legend、阈值或无数据状态。
- [x] 负载脚本限制目标、总量、并发和延迟。
- [x] 文档不把指标相关性写成根因结论。

