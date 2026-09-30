from __future__ import annotations
from collections import defaultdict, Counter
from .core import BaziChart, ELEMENT, GENERATES, CONTROLS, GENERATED_BY, HIDDEN_STEMS, interactions

SEASONAL = {
    "寅":{"木":1.35,"火":1.10,"水":0.90,"金":0.70,"土":0.90}, "卯":{"木":1.45,"火":1.10,"水":0.85,"金":0.65,"土":0.85},
    "辰":{"土":1.25,"木":1.05,"水":0.95,"金":0.90,"火":0.95}, "巳":{"火":1.40,"土":1.10,"木":0.90,"金":0.75,"水":0.65},
    "午":{"火":1.50,"土":1.15,"木":0.85,"金":0.70,"水":0.55}, "未":{"土":1.30,"火":1.10,"木":0.95,"金":0.85,"水":0.70},
    "申":{"金":1.40,"水":1.10,"土":1.00,"火":0.70,"木":0.70}, "酉":{"金":1.50,"水":1.05,"土":0.95,"火":0.65,"木":0.65},
    "戌":{"土":1.30,"金":1.00,"火":0.95,"水":0.80,"木":0.75}, "亥":{"水":1.45,"木":1.10,"金":0.90,"土":0.75,"火":0.60},
    "子":{"水":1.50,"木":1.05,"金":0.90,"土":0.70,"火":0.55}, "丑":{"土":1.25,"水":1.10,"金":1.00,"木":0.80,"火":0.65},
}

def _clamp(x,a=-100,b=100): return max(a,min(b,round(x,1)))
def _scale01(x): return _clamp(x,0,100)

def element_profile(chart:BaziChart, extra_pillars=()) -> dict:
    score=defaultdict(float)
    # visible stems and branch main+hidden qi; natal gets unit weight, transits 0.65
    all_text=[(p.text,1.0) for p in chart.pillars]+[(x,0.65) for x in extra_pillars]
    for text,w0 in all_text:
        s,b=text
        score[ELEMENT[s]] += 1.0*w0
        for hs,w in HIDDEN_STEMS[b]: score[ELEMENT[hs]] += 1.2*w*w0
    season=SEASONAL[chart.month.branch]
    for e in "木火土金水": score[e]*=season[e]
    total=sum(score.values()) or 1
    return {e:round(score[e],3) for e in "木火土金水"} | {"normalized":{e:round(score[e]/total,4) for e in "木火土金水"}}

def compute_state(chart:BaziChart, *, extra_pillars=(), focus:str|None=None, activation_policy:str="legacy") -> dict:
    if activation_policy not in ("legacy", "bounded-v1"):
        raise ValueError("unsupported activation_policy")
    prof=element_profile(chart,extra_pillars)
    norm=prof["normalized"]; dm=ELEMENT[chart.day_master]
    resource=GENERATED_BY[dm]; output=GENERATES[dm]; wealth=CONTROLS[dm]; pressure=next(e for e,v in CONTROLS.items() if v==dm)
    support=(norm[dm]+norm[resource])*100
    drain=(norm[output]+norm[wealth])*100
    control=norm[pressure]*100
    capacity=(support - 0.62*drain - 0.85*control)*1.55
    useful=sum(norm[e] for e in chart.useful_elements)*100 if chart.useful_elements else 0
    unfav=sum(norm[e] for e in chart.unfavorable_elements)*100 if chart.unfavorable_elements else 0
    inter=interactions(chart,extra_pillars)
    activation_raw=22*len(extra_pillars)+12*len(inter["branchClashes"])+9*len(inter["branchHarmonies"])+10*len(inter["stemCombines"])+8*len(inter["trines"])
    activation = (100 * activation_raw / (100 + activation_raw)
                  if activation_policy == "bounded-v1" else min(100, activation_raw))
    friction=min(100, 18*len(inter["branchClashes"])+10*len(inter["branchHarms"])+max(0,unfav-useful)*0.35)
    # Generic change/binding/resonance features. They describe structure, not event categories.
    all_pillars=[p.text for p in chart.pillars]+list(extra_pillars)
    stems=Counter(x[0] for x in all_pillars); branches=Counter(x[1] for x in all_pillars)
    repetition=sum(v-1 for v in stems.values() if v>1)+sum(v-1 for v in branches.values() if v>1)
    horse_groups={frozenset("申子辰"):"寅",frozenset("寅午戌"):"申",frozenset("巳酉丑"):"亥",frozenset("亥卯未"):"巳"}
    horse={h for g,h in horse_groups.items() if chart.year.branch in g or chart.day.branch in g}
    horse_hits=sum(1 for x in extra_pillars if x[1] in horse)
    change_pressure=min(100, 14*len(inter["branchClashes"])+9*len(inter["branchHarms"])+12*horse_hits+6*len(extra_pillars))
    binding_pressure=min(100, 13*len(inter["branchHarmonies"])+11*len(inter["stemCombines"])+16*len(inter["trines"]))
    resonance=min(100, repetition*14)
    flow=100-abs(max(norm.values())-min(norm.values()))*120
    stability=100-min(90, len(inter["branchClashes"])*16+len(inter["branchHarms"])*10+abs(capacity)*0.15)
    # climate axis: positive warm/dry, negative cold/wet. deliberately heuristic.
    climate=(norm["火"]-norm["水"])*100 + (norm["土"]-norm["木"])*25
    manifestation=_scale01(45+0.35*activation+0.28*useful-0.22*friction)
    maturity=_scale01(30+0.40*activation+0.25*manifestation-0.18*friction)
    result={
      "schema":"bazi.state.v1","focus":focus,
      "metrics":{
        "dayMasterCapacity":_clamp(capacity),"elementSupport":_scale01(support),"controlPressure":_scale01(control),
        "climateWarmDry":_clamp(climate),"flow":_scale01(flow),"usefulElementAccess":_scale01(useful),
        "unfavorablePressure":_scale01(unfav),"structuralStability":_scale01(stability),"eventActivation":_scale01(activation),
        "structureActivation":_scale01(activation),"changePressure":_scale01(change_pressure),"bindingPressure":_scale01(binding_pressure),"resonance":_scale01(resonance),
        "manifestation":manifestation,"timingMaturity":maturity,
      },
      "elements":prof,"roles":{"self":dm,"resource":resource,"output":output,"wealth":wealth,"pressure":pressure},
      "interactions":inter,
      "boundary":"Scores are interpretation-assist features, not canonical Bazi quantities, probabilities, or scientific measurements."
    }
    if activation_policy == "bounded-v1":
        result["scoringPolicy"] = {
            "activation": "bounded-v1", "rawActivation": activation_raw,
            "formula": "100 * raw / (100 + raw)",
            "scope": "structureActivation/eventActivation and their dependent metrics; other formulas unchanged",
            "boundary": "Transparent computational normalization, not a traditional rule or validated predictive confidence. Do not compare bounded-v1 activation scores directly with legacy API scores.",
        }
    return result
