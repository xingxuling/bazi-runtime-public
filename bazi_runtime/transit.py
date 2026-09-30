from __future__ import annotations
from .core import BaziChart, year_pillar
from .semantic import interpret
from .narrator import narrate


def _context(chart:BaziChart, *, year:int|None, life_context:dict|None, layers:list[dict])->dict:
    ctx=dict(life_context or {})
    if year is not None: ctx.setdefault("year",year)
    ctx["transitLayers"]=layers
    return ctx


def run_year(chart:BaziChart, year:int, *, luck_pillar:str|None=None, year_pillar_override:str|None=None, topic:str="general", question:str|None=None, life_context:dict|None=None)->dict:
    yp=year_pillar_override or year_pillar(year)
    layers=[]
    if luck_pillar: layers.append({"kind":"luck","pillar":luck_pillar})
    layers.append({"kind":"year","pillar":yp})
    extra=[x["pillar"] for x in layers]
    out=interpret(chart,extra_pillars=extra,topic=topic,question=question,analysis_context=_context(chart,year=year,life_context=life_context,layers=layers))
    out["transit"]={"kind":"year","year":year,"luckPillar":luck_pillar,"yearPillar":yp}
    out["narrative"]=narrate(out)
    return out


def run_month(chart:BaziChart, *, year:int, month_pillar:str, luck_pillar:str|None=None, year_pillar_override:str|None=None, topic:str="general", question:str|None=None, life_context:dict|None=None)->dict:
    yp=year_pillar_override or year_pillar(year)
    layers=[]
    if luck_pillar: layers.append({"kind":"luck","pillar":luck_pillar})
    layers.append({"kind":"year","pillar":yp})
    layers.append({"kind":"month","pillar":month_pillar})
    extra=[x["pillar"] for x in layers]
    out=interpret(chart,extra_pillars=extra,topic=topic,question=question,analysis_context=_context(chart,year=year,life_context=life_context,layers=layers))
    out["transit"]={"kind":"month","year":year,"luckPillar":luck_pillar,"yearPillar":yp,"monthPillar":month_pillar}
    out["narrative"]=narrate(out)
    return out


def run_event(chart:BaziChart, *, pillars=(), topic:str="general", question:str|None=None, life_context:dict|None=None)->dict:
    layers=[{"kind":f"event{i+1}","pillar":p} for i,p in enumerate(pillars)]
    out=interpret(chart,extra_pillars=pillars,topic=topic,question=question,analysis_context=_context(chart,year=None,life_context=life_context,layers=layers))
    out["transit"]={"kind":"event","pillars":list(pillars)}
    out["narrative"]=narrate(out)
    return out


def _run_fine_transit(chart, *, kind, year, supplied, luck_pillar,
                      year_pillar_override, pillar_sources, topic, question,
                      life_context):
    """Evaluate explicit layers; never infer day/hour/minute calendar rules."""
    from .core import sexagenary_index

    if type(year) is not int or not 1 <= year <= 9999:
        raise ValueError("year must be an integer in 1..9999")
    if pillar_sources is not None and not isinstance(pillar_sources, dict):
        raise ValueError("pillar_sources must be an object mapping layers to source descriptions")
    sources = dict(pillar_sources or {})
    yp = year_pillar(year) if year_pillar_override is None else year_pillar_override
    values = ([] if luck_pillar is None else [("luck", luck_pillar)])
    values += [("year", yp), *supplied]
    allowed = {name for name, _ in values}
    if any(key not in allowed for key in sources):
        raise ValueError("pillar_sources may only name included transit layers")
    if any(not isinstance(value, str) or not value.strip() for value in sources.values()):
        raise ValueError("pillar_sources values must be non-empty source/rule descriptions")
    if year_pillar_override is None and "year" in sources:
        raise ValueError("year source requires an explicit year_pillar_override")
    layers = []
    for name, pillar in values:
        if pillar is None:
            raise ValueError(f"{name}_pillar must be supplied; automatic {name} derivation is unsupported")
        if not isinstance(pillar, str):
            raise ValueError(f"{name}_pillar must be a valid sexagenary string")
        try:
            sexagenary_index(pillar)
        except ValueError as exc:
            raise ValueError(f"{name}_pillar: {exc}") from exc
        derived = name == "year" and year_pillar_override is None
        layers.append({"kind": name, "pillar": pillar,
                       "source": "gregorian-year-after-li-chun" if derived else "caller-supplied",
                       "rule": "year_pillar" if derived else sources.get(name, "unspecified")})
    out = interpret(chart, extra_pillars=[x["pillar"] for x in layers], topic=topic,
                    activation_policy="bounded-v1",
                    question=question, analysis_context=_context(
                        chart, year=year, life_context=life_context, layers=layers))
    out["transit"] = {"kind": kind, "year": year, "luckPillar": luck_pillar,
                      **{name + "Pillar": pillar for name, pillar in values},
                      "layers": layers,
                      "calendarDerivation": "explicit-pillars; year-only fallback assumes on/after Li Chun",
                      "boundary": "Day, hour and minute pillars are caller supplied. No automatic calendar, timezone, day-boundary or minute rule is applied. Finer layers do not establish greater real-world predictive accuracy."}
    out["narrative"] = narrate(out)
    return out


def run_day(chart:BaziChart, *, year:int, month_pillar:str, day_pillar:str|None=None,
            luck_pillar:str|None=None, year_pillar_override:str|None=None,
            pillar_sources:dict[str,str]|None=None, topic:str="general",
            question:str|None=None, life_context:dict|None=None)->dict:
    """Analyze year/month/day (+ optional luck) using caller-supplied pillars."""
    return _run_fine_transit(chart, kind="day", year=year,
        supplied=[("month", month_pillar), ("day", day_pillar)],
        luck_pillar=luck_pillar, year_pillar_override=year_pillar_override,
        pillar_sources=pillar_sources, topic=topic, question=question, life_context=life_context)


def run_hour(chart:BaziChart, *, year:int, month_pillar:str, day_pillar:str,
             hour_pillar:str|None=None, luck_pillar:str|None=None,
             year_pillar_override:str|None=None, pillar_sources:dict[str,str]|None=None,
             topic:str="general", question:str|None=None, life_context:dict|None=None)->dict:
    """Analyze year/month/day/hour (+ optional luck); no timestamp conversion."""
    return _run_fine_transit(chart, kind="hour", year=year,
        supplied=[("month", month_pillar), ("day", day_pillar), ("hour", hour_pillar)],
        luck_pillar=luck_pillar, year_pillar_override=year_pillar_override,
        pillar_sources=pillar_sources, topic=topic, question=question, life_context=life_context)


def run_minute(chart:BaziChart, *, year:int, month_pillar:str, day_pillar:str,
               hour_pillar:str, minute_pillar:str|None=None, luck_pillar:str|None=None,
               year_pillar_override:str|None=None, pillar_sources:dict[str,str]|None=None,
               topic:str="general", question:str|None=None, life_context:dict|None=None)->dict:
    """Analyze through 分运 using an explicit minute pillar, never an invented rule.

    pillar_sources records caller-provided source/rule descriptions by layer.
    Unspecified rules remain explicitly marked as such; they are not validated.
    """
    return _run_fine_transit(chart, kind="minute", year=year,
        supplied=[("month", month_pillar), ("day", day_pillar),
                  ("hour", hour_pillar), ("minute", minute_pillar)],
        luck_pillar=luck_pillar, year_pillar_override=year_pillar_override,
        pillar_sources=pillar_sources, topic=topic, question=question, life_context=life_context)
