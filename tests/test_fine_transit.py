import copy
import json
import subprocess
import sys

import pytest

from bazi_runtime import build_chart, run_day, run_hour, run_minute
from bazi_runtime.core import sexagenary_pillar
from bazi_runtime.protocol import analyze_v1
from bazi_runtime.semantic import interpret


@pytest.fixture
def chart():
    return build_chart("甲子", "丙寅", "戊辰", "庚申")


BASE = dict(year=2026, month_pillar="戊申", day_pillar="甲子")
MINUTE = dict(**BASE, hour_pillar="丙寅", minute_pillar="乙丑")


@pytest.mark.parametrize("fn,kwargs,kinds", [
    (run_day, BASE, ["year", "month", "day"]),
    (run_hour, dict(**BASE, hour_pillar="丙寅"), ["year", "month", "day", "hour"]),
    (run_minute, MINUTE, ["year", "month", "day", "hour", "minute"]),
])
def test_layers_and_pipeline(chart, fn, kwargs, kinds):
    result = fn(chart, **kwargs, luck_pillar="乙卯", topic="free", question="test")
    expected = ["luck", *kinds]
    assert [x["kind"] for x in result["transit"]["layers"]] == expected
    extra_nodes = [x for x in result["signalGraph"]["nodes"] if not x["natal"]]
    assert [x["kind"] for x in extra_nodes] == expected
    assert len({x["id"] for x in result["signalGraph"]["nodes"]}) == len(expected) + 4
    pillars = [x["pillar"] for x in result["transit"]["layers"]]
    assert result["state"] == interpret(chart, extra_pillars=pillars, topic="free", activation_policy="bounded-v1")["state"]
    assert result["topic"] == "free" and result["question"] == "test"
    assert "narrative" in result and "minute rule" in result["transit"]["boundary"]


@pytest.mark.parametrize("pillar", [sexagenary_pillar(i) for i in range(60)])
def test_all_valid_minute_pillars(chart, pillar):
    args = dict(MINUTE, minute_pillar=pillar)
    assert run_minute(chart, **args)["transit"]["minutePillar"] == pillar


@pytest.mark.parametrize("field", ["month_pillar", "day_pillar", "hour_pillar", "minute_pillar", "luck_pillar", "year_pillar_override"])
@pytest.mark.parametrize("value", ["", "甲丑", "甲", "甲子子", "xx", 12, False])
def test_reject_invalid_pillars(chart, field, value):
    with pytest.raises(ValueError):
        run_minute(chart, **dict(MINUTE, **{field: value}))


@pytest.mark.parametrize("field", ["month_pillar", "day_pillar", "hour_pillar", "minute_pillar"])
def test_missing_layer_explicitly_unsupported(chart, field):
    with pytest.raises(ValueError, match="automatic .* derivation is unsupported"):
        run_minute(chart, **dict(MINUTE, **{field: None}))


def test_omitted_minute_rejected(chart):
    with pytest.raises(ValueError, match="minute_pillar must be supplied"):
        run_minute(chart, **BASE, hour_pillar="丙寅")


@pytest.mark.parametrize("year", [True, False, 0, 10000, 2026.5, "2026", None])
def test_invalid_year(chart, year):
    with pytest.raises(ValueError, match="year must"):
        run_minute(chart, **dict(MINUTE, year=year))


@pytest.mark.parametrize("year", [1, 9999])
def test_year_bounds(chart, year):
    assert run_minute(chart, **dict(MINUTE, year=year))["transit"]["year"] == year


def test_override_and_sources_no_mutation(chart):
    sources = {"minute": "external-example-rule-v1", "year": "before-li-chun"}
    context = {"transitLayers": [{"kind": "fake", "pillar": "甲子"}]}
    before = copy.deepcopy((sources, context, chart.as_dict()))
    result = run_minute(chart, **MINUTE, year_pillar_override="乙巳",
                        pillar_sources=sources, life_context=context)
    layers = result["transit"]["layers"]
    assert layers[0] == {"kind": "year", "pillar": "乙巳", "source": "caller-supplied", "rule": "before-li-chun"}
    assert layers[-1]["rule"] == sources["minute"]
    assert (sources, context, chart.as_dict()) == before
    assert result["transit"]["luckPillar"] is None
    assert len(result["signalGraph"]["nodes"]) == 9


@pytest.mark.parametrize("sources", [{"missing": "x"}, {"minute": ""}, {"minute": 4}, {"year": "x"}, {"luck": "x"}])
def test_invalid_sources(chart, sources):
    with pytest.raises(ValueError):
        run_minute(chart, **MINUTE, pillar_sources=sources)


def test_default_provenance(chart):
    layers = run_minute(chart, **MINUTE)["transit"]["layers"]
    assert layers[0]["source"] == "gregorian-year-after-li-chun"
    assert layers[-1]["source"] == "caller-supplied"
    assert layers[-1]["rule"] == "unspecified"


def payload(kind="minute"):
    return {"pillars": dict(zip(("year", "month", "day", "hour"), ("甲子", "丙寅", "戊辰", "庚申"))),
            "transit": {"kind": kind, "year": 2026, "monthPillar": "戊申", "dayPillar": "甲子", "hourPillar": "丙寅", "minutePillar": "乙丑", "pillarSources": {kind: "example"}}}


@pytest.mark.parametrize("kind", ["day", "hour", "minute"])
def test_protocol(kind):
    data = payload(kind)
    before = copy.deepcopy(data)
    result = analyze_v1(data)
    assert result["transit"]["kind"] == kind
    assert result["transit"]["layers"][-1]["rule"] == "example"
    assert data == before


def test_unknown_kind_rejected():
    with pytest.raises(ValueError, match="unsupported transit kind"):
        analyze_v1(payload("minut"))


def test_cli_success_and_missing_minute():
    data = payload()
    process = subprocess.run([sys.executable, "-m", "bazi_runtime.cli"], input=json.dumps(data), text=True, capture_output=True)
    assert process.returncode == 0
    assert json.loads(process.stdout)["transit"]["minutePillar"] == "乙丑"
    del data["transit"]["minutePillar"]
    process = subprocess.run([sys.executable, "-m", "bazi_runtime.cli"], input=json.dumps(data), text=True, capture_output=True)
    assert process.returncode == 2 and not process.stdout
    assert "automatic minute derivation is unsupported" in process.stderr
    assert "Traceback" not in process.stderr


@pytest.mark.parametrize("data", [[], None, {"pillars": []},
    {"pillars": {"year": "甲子", "month": "丙寅", "day": "", "hour": "庚申"}},
    dict(payload(), transit=[]), dict(payload(), lifeContext=[])])
def test_protocol_shapes(data):
    with pytest.raises(ValueError):
        analyze_v1(data)


@pytest.mark.parametrize("sources", [[], "abc", 1])
def test_source_shape(chart, sources):
    with pytest.raises(ValueError, match="pillar_sources must be"):
        run_minute(chart, **MINUTE, pillar_sources=sources)


def test_activation_bounded_and_auditable(chart):
    results = [run_minute(chart, **dict(MINUTE, minute_pillar=p)) for p in ("甲子", "壬午", "乙丑")]
    for result in results:
        state = result["state"]
        raw = state["scoringPolicy"]["rawActivation"]
        value = round(100 * raw / (100 + raw), 1)
        assert state["metrics"]["structureActivation"] == value < 100
        assert state["metrics"]["eventActivation"] == value
    assert len({r["state"]["metrics"]["structureActivation"] for r in results}) > 1
