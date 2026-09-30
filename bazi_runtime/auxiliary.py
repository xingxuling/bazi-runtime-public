"""Independent 胎元/命宫/身宫 coordinates; never inputs to natal scoring."""
from __future__ import annotations
from .core import (BaziChart, STEMS, BRANCHES, HIDDEN_STEMS, ten_god,
                   growth_stage, nayin, void_branches, sexagenary_index,
                   STEM_COMBINES, BRANCH_CLASHES, BRANCH_HARMONIES, BRANCH_HARMS)

METHOD = "jie-month-five-tigers-v1"
SOURCE = "https://github.com/6tail/lunar-python/blob/v1.4.8/lunar_python/EightChar.py"
MONTH_BRANCHES = "寅卯辰巳午未申酉戌亥子丑"
LABELS = {"taiYuan": "胎元", "mingGong": "命宫", "shenGong": "身宫"}


def auxiliary_pillars(chart: BaziChart, *, method: str = METHOD,
                      overrides: dict | None = None,
                      include_relations: bool = False) -> dict:
    """Use supplied jie-month/hour branches, with named, sourced overrides.

    Each override is {"pillar": "甲子", "source": "caller rule description"}.
    Calendar conversion, lunar-month/zhongqi methods and time corrections are
    deliberately not inferred. See docs/AUXILIARY_PILLARS.md.
    """
    if method != METHOD:
        raise ValueError(f"unsupported auxiliary method: {method!r}")
    if type(include_relations) is not bool:
        raise ValueError("include_relations must be boolean")
    if overrides is not None and not isinstance(overrides, dict):
        raise ValueError("overrides must be an object")
    overrides = dict(overrides or {})
    if any(key not in LABELS for key in overrides):
        raise ValueError("override keys must be taiYuan, mingGong or shenGong")
    for key, value in overrides.items():
        if not isinstance(value, dict) or set(value) != {"pillar", "source"}:
            raise ValueError(f"{key} override requires only pillar and source")
        if not isinstance(value["pillar"], str):
            raise ValueError(f"{key}.pillar must be a sexagenary string")
        sexagenary_index(value["pillar"])
        if not isinstance(value["source"], str) or not value["source"].strip():
            raise ValueError(f"{key}.source must be a non-empty rule description")

    month_number = MONTH_BRANCHES.index(chart.month.branch) + 1
    hour_number = MONTH_BRANCHES.index(chart.hour.branch) + 1
    # Palace indices are 1..12 in 寅..丑 order; wrap zero to twelve.
    ming_number = (13 - month_number - hour_number) % 12 + 1
    shen_number = (month_number + BRANCHES.index(chart.hour.branch)) % 12 + 1
    year_index = STEMS.index(chart.year.stem)

    def palace(number: int) -> str:
        return STEMS[(2 * (year_index + 1) + number - 1) % 10] + MONTH_BRANCHES[number - 1]

    calculated = {
        "taiYuan": STEMS[(STEMS.index(chart.month.stem) + 1) % 10]
                   + BRANCHES[(BRANCHES.index(chart.month.branch) + 3) % 12],
        "mingGong": palace(ming_number),
        "shenGong": palace(shen_number),
    }
    result = {
        "schema": "bazi.auxiliary.v1", "method": METHOD,
        "basis": {"yearPillar": chart.year.text, "monthPillar": chart.month.text,
                  "hourBranch": chart.hour.branch, "monthNumber": month_number,
                  "calendar": "supplied-jie-month-pillar",
                  "timeCorrection": "caller-responsibility-no-conversion"},
        "sources": [SOURCE], "includedInNatalScoring": False,
        "warnings": ["传统术数辅助坐标，不是已验证的命运预测或医学受孕日期。",
                     "节令月支口径；不是农历月序或中气过宫算法。",
                     "年柱与时支直接采用输入；不校正时区、夏令时、真太阳时或子时换日。"],
        "pillars": {},
    }
    for key, computed in calculated.items():
        override = overrides.get(key)
        value = override["pillar"] if override else computed
        stem, branch = value
        result["pillars"][key] = {
            "label": LABELS[key], "text": value, "calculatedText": computed,
            "origin": "override" if override else "calculated",
            "source": override["source"] if override else SOURCE,
            "stemTenGod": ten_god(chart.day_master, stem),
            "hidden": [{"stem": s, "tenGod": ten_god(chart.day_master, s)}
                       for s, _ in HIDDEN_STEMS[branch]],
            "growthStage": growth_stage(chart.day_master, branch),
            "nayin": nayin(value), "void": list(void_branches(value)),
        }
    if include_relations:
        relations = []
        for key, item in result["pillars"].items():
            for natal in chart.pillars:
                stem_pair = frozenset((item["text"][0], natal.stem))
                branch_pair = frozenset((item["text"][1], natal.branch))
                for kind, matches in (("stemCombine", stem_pair in STEM_COMBINES),
                                      ("branchClash", branch_pair in BRANCH_CLASHES),
                                      ("branchHarmony", branch_pair in BRANCH_HARMONIES),
                                      ("branchHarm", branch_pair in BRANCH_HARMS)):
                    if matches:
                        relations.append({"auxiliary": key, "natal": natal.name, "kind": kind})
        result["analysis"] = {"scope": "pairwise-to-natal-only", "relations": relations,
                              "scoreContribution": 0,
                              "note": "仅列传统合冲害关系；不判吉凶，不合化，不重复计分。"}
    return result
