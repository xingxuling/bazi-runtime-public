from __future__ import annotations
from collections import Counter
from itertools import combinations
from typing import Any

from .core import (
    BaziChart, BRANCHES, ELEMENT, HIDDEN_STEMS, STEMS,
    STEM_COMBINES, BRANCH_CLASHES, BRANCH_HARMONIES, BRANCH_HARMS,
    TRINES, ten_god, growth_stage,
)

TEN_GOD_ATOMS = {
    "比肩": ["自体", "同类", "并行", "竞争"],
    "劫财": ["同类", "分流", "争夺", "助身"],
    "食神": ["输出", "舒展", "生成", "缓冲"],
    "伤官": ["输出", "突破", "反约束", "显化"],
    "偏财": ["外部资源", "流动", "机会", "现实投入"],
    "正财": ["稳定资源", "占有", "现实责任", "落地"],
    "七杀": ["压力", "约束", "挑战", "强制"],
    "正官": ["规则", "秩序", "身份", "责任"],
    "偏印": ["非标准支持", "知识", "保护", "转译"],
    "正印": ["支持", "学习", "保护", "承载"],
}

GROWTH_ATOMS = {
    "长生": ["启动", "生长", "恢复"],
    "沐浴": ["暴露", "敏感", "不稳定"],
    "冠带": ["成形", "包装", "进入结构"],
    "临官": ["成熟", "执行", "承担"],
    "帝旺": ["峰值", "强驱动", "放大"],
    "衰": ["减弱", "退潮", "承载下降"],
    "病": ["失衡", "低效", "卡顿"],
    "死": ["耗尽", "停滞", "终止倾向"],
    "墓": ["收束", "封存", "积压"],
    "绝": ["切断", "脱离", "断点"],
    "胎": ["潜伏", "未成形", "胚胎"],
    "养": ["培养", "修复", "准备"],
}

INTERACTION_ATOMS = {
    "stem_combine": ["耦合", "牵制", "转化倾向"],
    "branch_clash": ["冲突", "切换", "分离", "位移"],
    "branch_harmony": ["绑定", "聚合", "协同"],
    "branch_harm": ["暗耗", "不协调", "隐性牵扯"],
    "trine": ["聚局", "协同放大", "结构成团"],
    "self_punish": ["自我反馈", "反复", "内耗"],
    "punishment": ["摩擦", "约束", "损耗"],
    "resonance": ["重复", "共振", "主题放大"],
    "horse": ["移动", "切换", "外部变化"],
}

HORSE = {
    frozenset("申子辰"): "寅",
    frozenset("寅午戌"): "申",
    frozenset("巳酉丑"): "亥",
    frozenset("亥卯未"): "巳",
}

# Penalty relations are kept symbolic; they do not carry an automatic good/bad verdict.
PUNISH_PAIRS = {
    frozenset(("子", "卯")),
    frozenset(("寅", "巳")), frozenset(("巳", "申")), frozenset(("申", "寅")),
    frozenset(("丑", "戌")), frozenset(("戌", "未")), frozenset(("未", "丑")),
}
SELF_PUNISH = {"辰", "午", "酉", "亥"}


def _family(god: str) -> str:
    if god in ("正印", "偏印"): return "印"
    if god in ("正财", "偏财"): return "财"
    if god in ("正官", "七杀"): return "官杀"
    if god in ("食神", "伤官"): return "食伤"
    if god in ("比肩", "劫财"): return "比劫"
    return god


def _horse_for(branch: str) -> str | None:
    for group, horse in HORSE.items():
        if branch in group:
            return horse
    return None


def _layer_records(extra_pillars: list[str], analysis_context: dict[str, Any] | None) -> list[dict]:
    ctx = analysis_context or {}
    layers = list(ctx.get("transitLayers") or [])
    if layers and len(layers) == len(extra_pillars):
        return [{"kind": x.get("kind", f"extra{i+1}"), "pillar": x.get("pillar", p), "index": i + 4}
                for i, (x, p) in enumerate(zip(layers, extra_pillars))]
    return [{"kind": f"extra{i+1}", "pillar": p, "index": i + 4} for i, p in enumerate(extra_pillars)]


def _pillar_record(chart: BaziChart, kind: str, pillar: str, index: int, *, natal: bool) -> dict:
    stem, branch = pillar
    stem_god = ten_god(chart.day_master, stem)
    branch_main = HIDDEN_STEMS[branch][0][0]
    branch_god = ten_god(chart.day_master, branch_main)
    return {
        "id": f"{kind}:{pillar}:{index}",
        "kind": kind,
        "pillar": pillar,
        "stem": stem,
        "branch": branch,
        "stemElement": ELEMENT[stem],
        "branchElement": ELEMENT[branch],
        "stemTenGod": stem_god,
        "stemFamily": _family(stem_god),
        "branchMainStem": branch_main,
        "branchMainTenGod": branch_god,
        "branchFamily": _family(branch_god),
        "growthStage": growth_stage(chart.day_master, branch),
        "growthAtoms": list(GROWTH_ATOMS[growth_stage(chart.day_master, branch)]),
        "stemAtoms": list(TEN_GOD_ATOMS.get(stem_god, [])),
        "branchAtoms": list(TEN_GOD_ATOMS.get(branch_god, [])),
        "usefulStem": ELEMENT[stem] in chart.useful_elements,
        "usefulBranch": ELEMENT[branch] in chart.useful_elements,
        "unfavorableStem": ELEMENT[stem] in chart.unfavorable_elements,
        "unfavorableBranch": ELEMENT[branch] in chart.unfavorable_elements,
        "natal": natal,
    }


def build_signal_graph(chart: BaziChart, extra_pillars=(), analysis_context: dict[str, Any] | None = None) -> dict:
    natal = [
        _pillar_record(chart, "year", chart.year.text, 0, natal=True),
        _pillar_record(chart, "month", chart.month.text, 1, natal=True),
        _pillar_record(chart, "day", chart.day.text, 2, natal=True),
        _pillar_record(chart, "hour", chart.hour.text, 3, natal=True),
    ]
    extras = [_pillar_record(chart, r["kind"], r["pillar"], r["index"], natal=False)
              for r in _layer_records(list(extra_pillars), analysis_context)]
    nodes = natal + extras
    edges: list[dict] = []

    for a, b in combinations(nodes, 2):
        spair = frozenset((a["stem"], b["stem"]))
        bpair = frozenset((a["branch"], b["branch"]))
        if spair in STEM_COMBINES:
            edges.append({"kind": "stem_combine", "from": a["id"], "to": b["id"], "symbols": a["stem"] + b["stem"], "atoms": INTERACTION_ATOMS["stem_combine"]})
        if bpair in BRANCH_CLASHES:
            edges.append({"kind": "branch_clash", "from": a["id"], "to": b["id"], "symbols": a["branch"] + b["branch"], "atoms": INTERACTION_ATOMS["branch_clash"]})
        if bpair in BRANCH_HARMONIES:
            edges.append({"kind": "branch_harmony", "from": a["id"], "to": b["id"], "symbols": a["branch"] + b["branch"], "atoms": INTERACTION_ATOMS["branch_harmony"]})
        if bpair in BRANCH_HARMS:
            edges.append({"kind": "branch_harm", "from": a["id"], "to": b["id"], "symbols": a["branch"] + b["branch"], "atoms": INTERACTION_ATOMS["branch_harm"]})
        if a["branch"] == b["branch"] and a["branch"] in SELF_PUNISH:
            edges.append({"kind": "self_punish", "from": a["id"], "to": b["id"], "symbols": a["branch"] * 2, "atoms": INTERACTION_ATOMS["self_punish"]})
        elif bpair in PUNISH_PAIRS:
            edges.append({"kind": "punishment", "from": a["id"], "to": b["id"], "symbols": a["branch"] + b["branch"], "atoms": INTERACTION_ATOMS["punishment"]})

    branch_set = set(n["branch"] for n in nodes)
    for group, elem in TRINES.items():
        if group.issubset(branch_set):
            members = [n["id"] for n in nodes if n["branch"] in group]
            edges.append({"kind": "trine", "members": members, "element": elem, "atoms": INTERACTION_ATOMS["trine"]})

    # Repetition/resonance is important for interpretation but does not itself decide outcome.
    stem_counts = Counter(n["stem"] for n in nodes)
    branch_counts = Counter(n["branch"] for n in nodes)
    resonance = []
    for s, c in stem_counts.items():
        if c > 1:
            resonance.append({"kind": "stem", "symbol": s, "count": c, "atoms": INTERACTION_ATOMS["resonance"]})
    for b, c in branch_counts.items():
        if c > 1:
            resonance.append({"kind": "branch", "symbol": b, "count": c, "atoms": INTERACTION_ATOMS["resonance"]})

    # Horse is a universal movement/change cue, not a career/travel verdict.
    horses = {x for x in (_horse_for(chart.year.branch), _horse_for(chart.day.branch)) if x}
    horse_hits = [n for n in extras if n["branch"] in horses]

    return {
        "schema": "bazi.signal-graph.v1",
        "nodes": nodes,
        "edges": edges,
        "resonance": resonance,
        "horseHits": [{"node": n["id"], "branch": n["branch"], "atoms": INTERACTION_ATOMS["horse"]} for n in horse_hits],
        "boundary": "Graph edges are symbolic structural relations. They do not name or guarantee a real-world event category."
    }


def build_structure_frames(chart: BaziChart, graph: dict, state: dict) -> list[dict]:
    """Compose generic mechanism frames without enumerating life-event types."""
    extras = [n for n in graph["nodes"] if not n["natal"]]
    frames: list[dict] = []

    def add(kind: str, label: str, strength: float, atoms: list[str], evidence: list[str], direction: str = "mixed"):
        frames.append({
            "kind": kind,
            "label": label,
            "strength": round(max(0, min(100, strength)), 1),
            "atoms": list(dict.fromkeys(atoms)),
            "evidence": evidence,
            "direction": direction,
        })

    # One frame per transit pillar: what enters, how it behaves, whether it is useful/unfavorable.
    for n in extras:
        atoms = n["stemAtoms"] + n["branchAtoms"] + n["growthAtoms"]
        strength = 42
        if n["usefulStem"] or n["usefulBranch"]: strength += 14
        if n["unfavorableStem"] or n["unfavorableBranch"]: strength += 8
        local_edges = [e for e in graph["edges"] if e.get("from") == n["id"] or e.get("to") == n["id"] or n["id"] in e.get("members", [])]
        strength += min(28, len(local_edges) * 6)
        add(
            "transit_entry",
            f"{n['kind']} {n['pillar']}：{n['stemTenGod']} / {n['branchMainTenGod']} 入场",
            strength,
            atoms + [a for e in local_edges for a in e.get("atoms", [])],
            [f"{n['pillar']} 天干{n['stem']}={n['stemTenGod']}", f"地支{n['branch']}主气={n['branchMainTenGod']}", f"十二长生={n['growthStage']}"] + [f"{e['kind']}:{e.get('symbols', e.get('element',''))}" for e in local_edges],
        )

    # Cross-layer mechanism: output vs officer = expression/constraint tension, not a job verdict.
    output = [n for n in extras if n["stemFamily"] == "食伤" or n["branchFamily"] == "食伤"]
    officers = [n for n in extras if n["stemFamily"] == "官杀" or n["branchFamily"] == "官杀"]
    if output and officers:
        add(
            "output_rule_tension",
            "输出/突破力量与规则/压力力量同时被激活",
            68 + 5 * min(4, len(output) + len(officers)),
            ["输出", "突破", "规则", "压力", "张力", "重组"],
            [f"{n['kind']} {n['pillar']}={n['stemTenGod']}/{n['branchMainTenGod']}" for n in output + officers],
            "tension",
        )

    # Support vs pressure coactivation.
    support = [n for n in extras if n["stemFamily"] in {"印", "比劫"} or n["branchFamily"] in {"印", "比劫"}]
    pressure = [n for n in extras if n["stemFamily"] == "官杀" or n["branchFamily"] == "官杀"]
    if support and pressure:
        add(
            "support_under_pressure",
            "压力与承载/支持同时出现，容易形成‘被压力推动而获得支撑’的结构",
            62 + 4 * min(5, len(support) + len(pressure)),
            ["压力", "承载", "支持", "推动", "转译"],
            [f"支持侧:{n['kind']} {n['pillar']}" for n in support] + [f"压力侧:{n['kind']} {n['pillar']}" for n in pressure],
            "mixed",
        )

    # Change mechanics from clashes/horse.
    change_edges = [e for e in graph["edges"] if e["kind"] in {"branch_clash", "branch_harm", "punishment", "self_punish"}]
    horse_hits = graph.get("horseHits", [])
    if change_edges or horse_hits:
        atoms = [a for e in change_edges for a in e.get("atoms", [])] + [a for h in horse_hits for a in h.get("atoms", [])]
        add(
            "change_mechanism",
            "切换/分离/位移类结构被显著激活",
            50 + min(42, len(change_edges) * 9 + len(horse_hits) * 12),
            atoms,
            [f"{e['kind']}:{e.get('symbols','')}" for e in change_edges] + [f"horse:{h['branch']}" for h in horse_hits],
            "transition",
        )

    # Binding mechanics.
    bind_edges = [e for e in graph["edges"] if e["kind"] in {"stem_combine", "branch_harmony", "trine"}]
    if bind_edges:
        add(
            "binding_mechanism",
            "绑定/聚合/牵制类结构增强",
            48 + min(38, len(bind_edges) * 8),
            [a for e in bind_edges for a in e.get("atoms", [])],
            [f"{e['kind']}:{e.get('symbols', e.get('element',''))}" for e in bind_edges],
            "binding",
        )

    # Repetition/resonance.
    if graph.get("resonance"):
        add(
            "resonance",
            "重复符号形成共振，相关主题容易被反复放大",
            45 + min(40, sum(x["count"] - 1 for x in graph["resonance"]) * 9),
            ["重复", "共振", "放大", "反复"],
            [f"{x['kind']}:{x['symbol']}×{x['count']}" for x in graph["resonance"]],
            "amplify",
        )

    # Global state frame, no event category.
    m = state["metrics"]
    add(
        "global_state",
        "当前结构的承载、激活、稳定与兑现条件",
        max(m["structureActivation"], m["eventActivation"]),
        ["承载", "激活", "稳定", "兑现", "时机"],
        [
            f"dayMasterCapacity={m['dayMasterCapacity']}",
            f"structureActivation={m['structureActivation']}",
            f"structuralStability={m['structuralStability']}",
            f"manifestation={m['manifestation']}",
            f"timingMaturity={m['timingMaturity']}",
        ],
        "state",
    )

    return sorted(frames, key=lambda x: x["strength"], reverse=True)


def build_semantic_atoms(graph: dict) -> list[dict]:
    """Flat symbolic atoms for LLM/human interpretation. No event classes."""
    out = []
    for n in graph["nodes"]:
        out.append({
            "source": n["id"],
            "pillar": n["pillar"],
            "layer": n["kind"],
            "atoms": list(dict.fromkeys(n["stemAtoms"] + n["branchAtoms"] + n["growthAtoms"])),
            "tenGod": n["stemTenGod"],
            "branchTenGod": n["branchMainTenGod"],
            "growthStage": n["growthStage"],
        })
    for e in graph["edges"]:
        out.append({"source": e["kind"], "relation": e, "atoms": e.get("atoms", [])})
    for r in graph.get("resonance", []):
        out.append({"source": "resonance", "relation": r, "atoms": r.get("atoms", [])})
    for h in graph.get("horseHits", []):
        out.append({"source": "horse", "relation": h, "atoms": h.get("atoms", [])})
    return out
