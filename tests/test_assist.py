from bazi_runtime.core import build_chart
from bazi_runtime.transit import run_month


def synthetic():
    return build_chart(
        "甲子", "丙寅", "戊辰", "庚申",
        useful_elements=("金","水"),unfavorable_elements=("火","土"),
        metadata={"fixture": "synthetic-symbols-only"}
    )


def test_synthetic_transit_exposes_structure_without_closed_event_class():
    r=run_month(synthetic(),year=2030,month_pillar="辛酉",luck_pillar="甲寅",topic="general")
    assert r["schema"]=="bazi.interpretation.v2"
    assert "eventHypotheses" not in r
    assert "lifeContext" not in r
    labels=[x["label"] for x in r["structureFrames"]]
    assert any("输出/突破力量与规则/压力力量" in x for x in labels)
    assert any("切换/分离/位移" in x for x in labels)
    assert r["state"]["metrics"]["changePressure"]>0
    assert r["signalGraph"]["horseHits"]


def test_semantic_atoms_are_open_ended_symbols_not_event_names():
    r=run_month(synthetic(),year=2030,month_pillar="辛酉",luck_pillar="甲寅")
    atoms={a for x in r["semanticAtoms"] for a in x.get("atoms",[])}
    assert "突破" in atoms
    assert "压力" in atoms
    assert "切换" in atoms or "位移" in atoms
    assert "辞职/离职" not in str(r)
