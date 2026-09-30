# v0.4.0

- 新增有来源和版本的胎元/命宫/身宫独立计算，节令月支与五虎遁口径
- 严格验证手工覆盖，保留计算值、实际值与来源
- v1 协议和 CLI 显式启用；默认兼容原输出，无评分扩张
- 可选原局两两合冲害标注，不推吉凶、不合化
- 全年干/月支/时支穷举、边界、覆盖、协议隔离及 CLI 回归测试

# Changelog

## 0.3.0
- Add caller-supplied day/hour/minute transit APIs and public exports.
- Include ordered layer provenance; explicitly reject absent fine-grained pillars.
- Route day/hour/minute JSON through the existing CLI and interpretation pipeline.
- Validate fine-transit sexagenary pillars and year bounds; reject unknown protocol kinds.
- Normalize fine-transit activation using an auditable bounded-v1 heuristic; legacy scores remain unchanged.
- Improve CLI input error handling and document unchanged score weighting/saturation.
- Preserve valid legacy year/month/event output and original calendar assumptions.


## 0.2.0
- Remove closed-world event taxonomy from the main interpretation path.
- Remove Life-Stage Prior and Career-State Machine from interpretation ranking.
- Add BZR-SignalGraph.
- Add open semantic atoms for ten gods, growth stages and structural relations.
- Add generic structure frames: output/rule tension, support-under-pressure, change, binding, resonance.
- Add generic changePressure, bindingPressure and resonance state metrics.
- Narrator now reports structural signals instead of naming concrete life events.
- Preserve school isolation and incremental transit APIs.

## 0.1.1
- Historical version with event hypothesis ranking.
