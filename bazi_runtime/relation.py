from __future__ import annotations
from .core import BaziChart, ten_god

KINSHIP_BY_TEN_GOD = {
    "比肩":["同辈/同类主体"], "劫财":["同辈/竞争或共享资源主体"],
    "食神":["输出/作品/子女类象"], "伤官":["输出/表达/反约束类象"],
    "偏财":["资源/交易/男性命盘的伴侣类象"], "正财":["稳定资源/男性命盘的伴侣类象"],
    "七杀":["压力/竞争/约束/风险"], "正官":["制度/职位/责任/女性命盘的伴侣类象"],
    "偏印":["非标准知识/工具/支持"], "正印":["知识/教育/资质/保护"]
}

def relation_map(chart:BaziChart) -> dict:
    dm=chart.day_master
    stems={s:ten_god(dm,s) for s in "甲乙丙丁戊己庚辛壬癸"}
    return {
        "schema":"bazi.relation.v1",
        "dayMaster":dm,
        "stemTenGod":stems,
        "tenGodSemantics":KINSHIP_BY_TEN_GOD,
        "palaces":{p.name:{"palace":p.palace,"timeWindow":p.time_window} for p in chart.pillars},
        "note":"人物定位与事件类象分开；同一十神可承载多个语义，必须由问题和时空约束消歧。"
    }
