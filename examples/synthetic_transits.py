"""Synthetic symbols for API demonstration; not a birth calendar or personal case."""
from bazi_runtime import build_chart, run_month, run_year

chart = build_chart("甲子", "丙寅", "戊辰", "庚申",
                    metadata={"fixture": "synthetic-symbols-only"})
print(run_month(chart, year=2030, month_pillar="戊申", luck_pillar="乙卯",
                question="Which symbolic structures are activated?")["narrative"])
for year in (2030, 2031, 2032):
    print(run_year(chart, year, luck_pillar="乙卯")["transit"])
