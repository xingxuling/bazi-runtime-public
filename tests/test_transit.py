from bazi_runtime.core import build_chart
from bazi_runtime.transit import run_year, run_month


def test_year_incremental():
    c=build_chart("甲子", "丙寅", "戊辰", "庚申",useful_elements=("金","水"),unfavorable_elements=("火","土"))
    r=run_year(c,2028,luck_pillar="乙卯",topic="事业问题，但不预设事件类型")
    assert r["transit"]["yearPillar"]=="戊申"
    assert "主结构" in r["narrative"]
    assert "事件边界" in r["narrative"]


def test_month_incremental():
    c=build_chart("甲子", "丙寅", "戊辰", "庚申")
    r=run_month(c,year=2027,month_pillar="辛亥",luck_pillar="乙卯")
    assert r["transit"]["monthPillar"]=="辛亥"
