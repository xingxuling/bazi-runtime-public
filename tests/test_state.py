from bazi_runtime.core import build_chart
from bazi_runtime.state import compute_state

def chart(): return build_chart("甲子", "丙寅", "戊辰", "庚申",useful_elements=("金","水"),unfavorable_elements=("火","土"))

def test_state_metrics_and_boundary():
    s=compute_state(chart())
    assert "dayMasterCapacity" in s["metrics"]
    assert "structureActivation" in s["metrics"]
    assert "changePressure" in s["metrics"]
    assert "bindingPressure" in s["metrics"]
    assert s["elements"]["木"] > s["elements"]["水"]
    assert "not canonical" in s["boundary"]

def test_2028_activates_clash_or_relation():
    s=compute_state(chart(),extra_pillars=("乙卯","戊申"))
    assert s["metrics"]["eventActivation"]>0
    assert isinstance(s["interactions"]["branchClashes"],list)
