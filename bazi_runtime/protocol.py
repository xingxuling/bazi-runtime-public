from __future__ import annotations
from .core import build_chart, sexagenary_index
from .transit import run_year, run_month, run_day, run_hour, run_minute, run_event

def _analyze_core(payload:dict)->dict:
    if not isinstance(payload, dict):
        raise ValueError("payload must be an object")
    p=payload["pillars"]
    if not isinstance(p, dict):
        raise ValueError("pillars must be an object")
    for name in ("year", "month", "day", "hour"):
        value = p.get(name)
        if not isinstance(value, str):
            raise ValueError(f"pillars.{name} must be a sexagenary string")
        sexagenary_index(value)
    if "transit" in payload and payload["transit"] is not None and not isinstance(payload["transit"], dict):
        raise ValueError("transit must be an object")
    if payload.get("lifeContext") is not None and not isinstance(payload["lifeContext"], dict):
        raise ValueError("lifeContext must be an object")
    chart=build_chart(p["year"],p["month"],p["day"],p["hour"],gender=payload.get("gender"),
                      useful_elements=payload.get("usefulElements",()),unfavorable_elements=payload.get("unfavorableElements",()),metadata=payload.get("metadata"))
    transit=payload.get("transit") or {}
    kind=transit.get("kind","event")
    if not isinstance(kind, str):
        raise ValueError("transit.kind must be a string")
    common={"topic":payload.get("topic","general"),"question":payload.get("question"),"life_context":payload.get("lifeContext")}
    if kind=="year":
        return run_year(chart,transit["year"],luck_pillar=transit.get("luckPillar"),year_pillar_override=transit.get("yearPillar"),**common)
    if kind=="month":
        return run_month(chart,year=transit["year"],month_pillar=transit["monthPillar"],luck_pillar=transit.get("luckPillar"),year_pillar_override=transit.get("yearPillar"),**common)
    if kind in ("day", "hour", "minute"):
        fields = {"month_pillar": transit.get("monthPillar"),
                  "day_pillar": transit.get("dayPillar")}
        if kind in ("hour", "minute"):
            fields["hour_pillar"] = transit.get("hourPillar")
        if kind == "minute":
            fields["minute_pillar"] = transit.get("minutePillar")
        return {"day": run_day, "hour": run_hour, "minute": run_minute}[kind](
            chart, year=transit["year"], **fields,
            luck_pillar=transit.get("luckPillar"),
            year_pillar_override=transit.get("yearPillar"),
            pillar_sources=transit.get("pillarSources"), **common)
    if kind != "event":
        raise ValueError(f"unsupported transit kind: {kind!r}")
    return run_event(chart,pillars=transit.get("pillars",()),**common)


def analyze_v1(payload: dict) -> dict:
    """Compatible v1 protocol; auxiliary coordinates are explicit opt-in."""
    from .auxiliary import auxiliary_pillars, METHOD
    if not isinstance(payload, dict):
        raise ValueError("payload must be an object")
    config = payload.get("auxiliary", False)
    if type(config) is not bool and not isinstance(config, dict):
        raise ValueError("auxiliary must be boolean or an options object")
    options = config if isinstance(config, dict) else {}
    if any(k not in {"method", "overrides", "includeRelations"} for k in options):
        raise ValueError("unknown auxiliary option")
    out = _analyze_core(payload)
    if config is not False:
        p = payload["pillars"]
        chart = build_chart(p["year"], p["month"], p["day"], p["hour"])
        out["auxiliary"] = auxiliary_pillars(
            chart, method=options.get("method", METHOD),
            overrides=options.get("overrides"),
            include_relations=options.get("includeRelations", False))
    return out
