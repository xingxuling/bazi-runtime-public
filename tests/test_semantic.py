from bazi_runtime.core import build_chart
from bazi_runtime.semantic import interpret


def test_school_isolation_and_open_interpretation_assist():
    c=build_chart("甲子", "丙寅", "戊辰", "庚申",useful_elements=("金","水"),unfavorable_elements=("火","土"))
    r=interpret(c,extra_pillars=("戊申",),topic="freeform",question="发生了什么？")
    names=[x["school"] for x in r["schoolPaths"]]
    assert names==["ziping","coordinate","blind_image","auxiliary"]
    assert r["arbitration"]["mode"]=="non-blending"
    assert "signalGraph" in r and "structureFrames" in r and "semanticAtoms" in r
    assert "closed list" in r["boundary"]
    assert "eventHypotheses" not in r
