# Tests 测试

项目测试目录，结构与 `src/hsr_nous/` 对应。

## 运行测试

```bash
pytest tests/ -v
```

## 测试规划

| 模块 | 待补充测试 |
|------|-----------|
| `pipeline/` | `loader` 数据加载、`update` 远程拉取 |
| `raw_schema/` | 模型字段解析、边界值处理 |
| `adapters/` | 角色/技能/关卡适配转换 |
| `sim_schema/` | 数据结构序列化/反序列化 |
| `sim/` | 行动序计算、伤害公式、策略解释器 |
| `agents/` | 各 Agent 决策逻辑 |

## 修改记录

- 初始创建：目录结构占位
