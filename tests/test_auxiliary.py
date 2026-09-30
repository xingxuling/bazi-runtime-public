import copy
import json
import subprocess
import sys
import pytest
from bazi_runtime import auxiliary_pillars, build_chart
from bazi_runtime.core import STEMS, BRANCHES, sexagenary_pillar, sexagenary_index
from bazi_runtime.protocol import analyze_v1
from bazi_runtime.auxiliary import MONTH_BRANCHES

BASE = {"pillars": dict(year="甲子", month="戊辰", day="甲子", hour="甲戌")}

def chart():
    return build_chart(**BASE["pillars"])


def test_classical_ming_example():
    out = auxiliary_pillars(chart())
    assert out["pillars"]["mingGong"]["text"] == "丁卯"
    assert out["pillars"]["taiYuan"]["text"] == "己未"


@pytest.mark.parametrize("year_stem", range(10))
@pytest.mark.parametrize("month", range(12))
@pytest.mark.parametrize("hour", range(12))
def test_all_month_hour_year_combinations(year_stem, month, hour):
    # Synthetic valid pillars: tests branch arithmetic, not a birth calendar.
    year = sexagenary_pillar(year_stem)
    mp = next(sexagenary_pillar(i) for i in range(60) if sexagenary_pillar(i)[1] == MONTH_BRANCHES[month])
    hp = next(sexagenary_pillar(i) for i in range(60) if sexagenary_pillar(i)[1] == BRANCHES[hour])
    out = auxiliary_pillars(build_chart(year, mp, "甲子", hp))["pillars"]
    # Classical direction walk: 子起正月逆数，再由生时顺数至卯。
    position = 0
    for _ in range(month):
        position = (position - 1) % 12
    clock = hour
    while clock != 3:
        clock = (clock + 1) % 12
        position = (position + 1) % 12
    assert out["mingGong"]["text"][1] == BRANCHES[position]
    # Separate body walk in 寅-based cycle, hour counts 子=1 through 亥=12.
    body = month
    for _ in range(hour + 1):
        body = (body + 1) % 12
    assert out["shenGong"]["text"][1] == MONTH_BRANCHES[body]
    for key in ("mingGong", "shenGong"):
        value = out[key]["text"]
        start = "丙戊庚壬甲丙戊庚壬甲"[year_stem]
        offset = MONTH_BRANCHES.index(value[1])
        assert value[0] == STEMS[(STEMS.index(start) + offset) % 10]
        sexagenary_index(value)


@pytest.mark.parametrize("index", range(60))
def test_taiyuan_wrap(index):
    mp = sexagenary_pillar(index)
    out = auxiliary_pillars(build_chart("甲子", mp, "甲子", "甲子"))
    # +51 in the 60-cycle means +1 stem and +3 branch.
    assert out["pillars"]["taiYuan"]["text"] == sexagenary_pillar(index + 51)


@pytest.mark.parametrize("year,month,hour,expected", [
    ("乙亥", "戊子", "己巳", "壬午"),
    ("甲戌", "乙亥", "乙丑", "丁丑"),
    ("庚午", "戊子", "己卯", "庚辰"),
    ("癸酉", "丁巳", "甲寅", "庚申"),
])
def test_upstream_body_examples(year, month, hour, expected):
    # Year/month/hour branches corresponding to upstream test dates; day unused.
    assert auxiliary_pillars(build_chart(year, month, "甲子", hour))["pillars"]["shenGong"]["text"] == expected


def test_override_and_optional_relations():
    out = auxiliary_pillars(chart(), overrides={"mingGong": {"pillar": "甲子", "source": "手工校准"}}, include_relations=True)
    assert out["pillars"]["mingGong"]["origin"] == "override"
    assert out["pillars"]["mingGong"]["text"] == "甲子"
    assert out["pillars"]["mingGong"]["calculatedText"] == "丁卯"
    assert out["analysis"]["scoreContribution"] == 0
    assert not out["includedInNatalScoring"]
    assert len(chart().pillars) == 4


@pytest.mark.parametrize("bad", [None, 1, "true", [], {"unknown": 1}, {"method": "lunar"},
    {"includeRelations": 1}, {"overrides": []}, {"overrides": {"no": "甲子"}},
    {"overrides": {"mingGong": "甲子"}},
    {"overrides": {"mingGong": {"pillar": "甲丑", "source": "x"}}},
    {"overrides": {"mingGong": {"pillar": "甲子", "source": " "}}},
    {"overrides": {"mingGong": {"pillar": 1, "source": "x"}}}])
def test_protocol_invalid(bad):
    with pytest.raises(ValueError):
        analyze_v1(dict(BASE, auxiliary=bad))


@pytest.mark.parametrize("option", [True, {}, {"includeRelations": True},
    {"overrides": {"taiYuan": {"pillar": "甲子", "source": "另派"}}}])
def test_exact_score_and_protocol_isolation(option):
    before = copy.deepcopy(BASE)
    baseline = analyze_v1(BASE)
    augmented = analyze_v1(dict(BASE, auxiliary=option))
    assert augmented.pop("auxiliary")
    assert augmented == baseline
    assert analyze_v1(dict(BASE, auxiliary=False)) == baseline
    assert BASE == before


def test_cli():
    run = subprocess.run([sys.executable, "-m", "bazi_runtime.cli"],
                         input=json.dumps(dict(BASE, auxiliary=True)),
                         text=True, capture_output=True, check=True)
    assert json.loads(run.stdout)["auxiliary"]["pillars"]["mingGong"]["text"] == "丁卯"


@pytest.mark.parametrize("kind", ["year", "month", "day", "hour", "minute"])
def test_all_transit_layers_unchanged(kind):
    transit = {"kind": kind, "year": 2026, "monthPillar": "甲午",
               "dayPillar": "甲子", "hourPillar": "甲子", "minutePillar": "甲子"}
    payload = dict(BASE, transit=transit)
    baseline = analyze_v1(payload)
    augmented = analyze_v1(dict(payload, auxiliary={"includeRelations": True}))
    augmented.pop("auxiliary")
    assert baseline == augmented
