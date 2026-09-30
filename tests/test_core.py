from bazi_runtime.core import build_chart, ten_god, growth_stage, nayin, void_branches, year_pillar, generate_luck_cycles, generate_small_luck

def test_synthetic_chart_core():
    c=build_chart("甲子", "丙寅", "戊辰", "庚申",useful_elements=("金","水"),unfavorable_elements=("火","土"))
    assert c.day_master=="戊"
    assert c.year.stem_ten_god=="七杀"
    assert c.month.stem_ten_god=="偏印"
    assert c.hour.stem_ten_god=="食神"
    assert c.month.hidden[0][0]=="甲"
    assert c.day.growth_stage=="冠带"
    assert c.year.nayin=="海中金"
    assert c.month.nayin=="炉中火"
    assert set(c.day.void)==set(("戌","亥"))

def test_ten_gods_and_year():
    assert ten_god("壬","辛")=="正印"
    assert ten_god("壬","戊")=="七杀"
    assert year_pillar(2026)=="丙午"
    assert year_pillar(2027)=="丁未"
    assert year_pillar(2028)=="戊申"


def test_cycle_generators():
    cycles=generate_luck_cycles("丙寅",forward=True,count=3,start_age=6.0)
    assert [x["pillar"] for x in cycles]==["丁卯","戊辰","己巳"]
    small=generate_small_luck("癸未",forward=True,count=3,start_age=1)
    assert [x["pillar"] for x in small]==["癸未","甲申","乙酉"]
