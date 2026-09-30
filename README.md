# Bazi Runtime (BZR)

**A programmable, auditable symbolic runtime for BaZi analysis.** BZR converts caller-supplied pillars into structured intermediate representations, signal graphs and open semantic frames that applications, researchers and interpretation layers can inspect and reuse.

It provides a Python library, JSON protocol and command-line interface. Version 0.4.0 supports layered year-to-minute transits and independent auxiliary pillars (胎元、命宫、身宫).

## Why use BZR?

- **Inspect the reasoning structure.** Structured outputs expose stems/branches, relations, semantic atoms, state features and scoring policy rather than only a final narrative.
- **Keep interpretations open.** Symbolic frames represent tension, support, movement, binding and resonance; the runtime does not rank a closed catalogue of personal life events.
- **Reproduce supplied-input calculations.** Explicit inputs and deterministic rules make results testable. Fine-grained transit layers retain source/rule labels, and auxiliary calculations expose a named method and pinned upstream reference.
- **Compose time layers through one interface.** Optional luck cycles and year, month, day, hour and minute layers feed the same structural pipeline. Fine-grained pillars are supplied by the caller, not inferred from a timestamp.
- **Keep auxiliary coordinates isolated.** Auxiliary pillars are opt-in, with sourced overrides and optional relation annotations. They do not alter the four natal pillars or contribute to natal/transit scores.
- **Preserve differences between schools.** Ziping, coordinate, blind-image and auxiliary paths remain separate; arbitration preserves conflicts instead of averaging incompatible assumptions.
- **Integrate with testable boundaries.** Python APIs, schema-tagged JSON outputs and a CLI share the implementation. The sanitized v0.4.0 source passes 1,680 tests, including exhaustive auxiliary combinations, input validation and output-isolation checks.

These are implementation properties, not evidence of predictive accuracy or comparative superiority over other software.

## Quick start

Python 3.10 or newer:

```sh
python -m pip install .
bazi-runtime --input examples/minute_transit.json --pretty
bazi-runtime --input examples/auxiliary_pillars.json --pretty
```

```python
from bazi_runtime import build_chart, run_minute, auxiliary_pillars

# Synthetic symbols for demonstrating the API, not a person's birth chart.
chart = build_chart("甲子", "丙寅", "戊辰", "庚申")
result = run_minute(
    chart,
    year=2030,
    month_pillar="辛酉",
    day_pillar="甲子",
    hour_pillar="丙寅",
    minute_pillar="乙丑",
    pillar_sources={"minute": "synthetic-example-rule-v1"},
)
print(result["structureFrames"])
print(result["signalGraph"])
print(auxiliary_pillars(chart)["pillars"])
```

## Outputs and interfaces

- Core: four pillars, hidden stems, ten gods, growth stages, void branches, nayin and relations
- State: explicit heuristic features, structural activation and change/binding/resonance measures
- Interpretation: signal graph, open semantic atoms, structure frames, separate school paths and a structural narrative
- Transits: `run_year`, `run_month`, `run_event`, `run_day`, `run_hour`, `run_minute`
- Auxiliary: `auxiliary_pillars(chart, overrides=..., include_relations=True)`

JSON fine-transit inputs use `transit.kind`, `year`, `monthPillar`, `dayPillar`, `hourPillar`, `minutePillar` and optional `pillarSources`. Set top-level `"auxiliary": true` to request independent auxiliary output. See the runnable [examples](examples/) and [auxiliary rules, sources and calendar boundaries](docs/AUXILIARY_PILLARS.md).

## Explicit boundaries

- **No automatic natal/calendar calculation.** Provide the natal pillars yourself. The runtime does not convert dates, locations, time zones, daylight saving, true solar time or day boundaries into pillars.
- **No automatic day/hour/minute pillars.** Fine-grained transit APIs require the target layer and its upper month/day/hour layers. All supplied pillars must be valid sexagenary combinations; this does not validate their correspondence to a real timestamp.
- **Year fallback has an assumption.** `year_pillar(year)` assumes the date is after Li Chun. Supply `year_pillar_override` for another boundary choice; source labels do not independently verify external rules.
- **Scores are heuristics.** Fine-grained activation uses `100 * raw / (100 + raw)` with the raw value exposed. Legacy activation remains compatible. Scores across policies or layer counts are not directly comparable and are not probabilities.
- **Auxiliary methods are specific.** The default is `jie-month-five-tigers-v1`; it is not a claim that all traditions use the same method. Sourced overrides retain both the calculated and selected values.
- **Traditional-cultural research scope.** Symbolic outputs are not scientifically validated predictions, medical conclusions or a basis for high-stakes decisions.

All included demonstrations are synthetic symbolic fixtures or explicitly attributed public rule examples. No personal birth dates, locations or case histories are required to run them.

## Development and validation

```sh
python -m pip install pytest
python -m pytest -q
python -m pip wheel . --no-deps --wheel-dir dist
```

See [validation evidence](evidence/VALIDATION.md), [release changes](CHANGELOG.md) and [third-party sources and notices](THIRD_PARTY_NOTICES.md). Runtime code uses the Python standard library; pytest is a test dependency.

The optional `rcl/bazi_runtime.rcl` artifact retains the v0.3.0 symbolic contract; it is not a separate v0.4.0 RCL validation claim.

## License

MIT. See [LICENSE](LICENSE). Attribution for the pinned lunar-python reference is retained in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
