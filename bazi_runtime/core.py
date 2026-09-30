from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Iterable, Optional

STEMS = "甲乙丙丁戊己庚辛壬癸"
BRANCHES = "子丑寅卯辰巳午未申酉戌亥"
ELEMENT = {
    "甲":"木","乙":"木","丙":"火","丁":"火","戊":"土","己":"土","庚":"金","辛":"金","壬":"水","癸":"水",
    "子":"水","丑":"土","寅":"木","卯":"木","辰":"土","巳":"火","午":"火","未":"土","申":"金","酉":"金","戌":"土","亥":"水",
}
POLARITY = {c:("阳" if i%2==0 else "阴") for i,c in enumerate(STEMS)}
BRANCH_POLARITY = {c:("阳" if i%2==0 else "阴") for i,c in enumerate(BRANCHES)}
HIDDEN_STEMS = {
    "子":[("癸",1.0)], "丑":[("己",0.6),("癸",0.25),("辛",0.15)], "寅":[("甲",0.6),("丙",0.25),("戊",0.15)],
    "卯":[("乙",1.0)], "辰":[("戊",0.6),("乙",0.25),("癸",0.15)], "巳":[("丙",0.6),("戊",0.25),("庚",0.15)],
    "午":[("丁",0.7),("己",0.3)], "未":[("己",0.6),("丁",0.25),("乙",0.15)], "申":[("庚",0.6),("壬",0.25),("戊",0.15)],
    "酉":[("辛",1.0)], "戌":[("戊",0.6),("辛",0.25),("丁",0.15)], "亥":[("壬",0.7),("甲",0.3)],
}
GENERATES = {"木":"火","火":"土","土":"金","金":"水","水":"木"}
CONTROLS = {"木":"土","土":"水","水":"火","火":"金","金":"木"}
CONTROLLED_BY = {v:k for k,v in CONTROLS.items()}
GENERATED_BY = {v:k for k,v in GENERATES.items()}
TEN_GODS = ("比肩","劫财","食神","伤官","偏财","正财","七杀","正官","偏印","正印")

NAYIN_60 = [
"海中金","海中金","炉中火","炉中火","大林木","大林木","路旁土","路旁土","剑锋金","剑锋金",
"山头火","山头火","涧下水","涧下水","城头土","城头土","白蜡金","白蜡金","杨柳木","杨柳木",
"泉中水","泉中水","屋上土","屋上土","霹雳火","霹雳火","松柏木","松柏木","长流水","长流水",
"沙中金","沙中金","山下火","山下火","平地木","平地木","壁上土","壁上土","金箔金","金箔金",
"覆灯火","覆灯火","天河水","天河水","大驿土","大驿土","钗钏金","钗钏金","桑柘木","桑柘木",
"大溪水","大溪水","沙中土","沙中土","天上火","天上火","石榴木","石榴木","大海水","大海水"]

STAGE_NAMES = ["长生","沐浴","冠带","临官","帝旺","衰","病","死","墓","绝","胎","养"]
STAGE_START = {"甲":"亥","乙":"午","丙":"寅","丁":"酉","戊":"寅","己":"酉","庚":"巳","辛":"子","壬":"申","癸":"卯"}

STEM_COMBINES = {frozenset(x) for x in [("甲","己"),("乙","庚"),("丙","辛"),("丁","壬"),("戊","癸")]}
BRANCH_CLASHES = {frozenset(x) for x in [("子","午"),("丑","未"),("寅","申"),("卯","酉"),("辰","戌"),("巳","亥")]}
BRANCH_HARMONIES = {frozenset(x) for x in [("子","丑"),("寅","亥"),("卯","戌"),("辰","酉"),("巳","申"),("午","未")]}
BRANCH_HARMS = {frozenset(x) for x in [("子","未"),("丑","午"),("寅","巳"),("卯","辰"),("申","亥"),("酉","戌")]}
TRINES = {frozenset("申子辰"):"水",frozenset("亥卯未"):"木",frozenset("寅午戌"):"火",frozenset("巳酉丑"):"金"}

PALACE = {"year":"祖上/父母/早年","month":"门户/父母兄弟/青年","day":"本人/配偶/中年","hour":"子女/晚辈/晚景"}
TIME_WINDOWS = {"year":"0-16","month":"16-32","day":"32-45","hour":"45+"}


def sexagenary_index(pillar: str) -> int:
    if len(pillar)!=2 or pillar[0] not in STEMS or pillar[1] not in BRANCHES:
        raise ValueError(f"invalid pillar: {pillar}")
    for i in range(60):
        if STEMS[i%10]+BRANCHES[i%12] == pillar:
            return i
    raise ValueError(f"non-sexagenary pillar: {pillar}")


def sexagenary_pillar(index: int) -> str:
    i=index%60
    return STEMS[i%10]+BRANCHES[i%12]


def year_pillar(year: int) -> str:
    """Year pillar for a Gregorian year assuming the date is on/after Li Chun.
    Before Li Chun callers should explicitly provide the previous year's pillar.
    """
    return sexagenary_pillar(year-1984)


def nayin(pillar: str) -> str:
    return NAYIN_60[sexagenary_index(pillar)]


def void_branches(pillar: str) -> tuple[str,str]:
    idx = sexagenary_index(pillar)
    xun_start = (idx//10)*10
    start_branch_idx = xun_start % 12
    used = {(start_branch_idx+i)%12 for i in range(10)}
    missing = [BRANCHES[i] for i in range(12) if i not in used]
    return tuple(missing)  # type: ignore[return-value]


def ten_god(day_stem: str, other_stem: str) -> str:
    dm_e, o_e = ELEMENT[day_stem], ELEMENT[other_stem]
    same_pol = POLARITY[day_stem] == POLARITY[other_stem]
    if o_e == dm_e:
        return "比肩" if same_pol else "劫财"
    if GENERATED_BY[o_e] == dm_e:  # dm generates other
        return "食神" if same_pol else "伤官"
    if CONTROLS[dm_e] == o_e:
        return "偏财" if same_pol else "正财"
    if CONTROLS[o_e] == dm_e:
        return "七杀" if same_pol else "正官"
    if GENERATES[o_e] == dm_e:
        return "偏印" if same_pol else "正印"
    raise AssertionError((day_stem, other_stem))


def growth_stage(day_stem: str, branch: str) -> str:
    start = BRANCHES.index(STAGE_START[day_stem])
    cur = BRANCHES.index(branch)
    direction = 1 if POLARITY[day_stem] == "阳" else -1
    step = ((cur-start)*direction) % 12
    return STAGE_NAMES[step]

@dataclass(frozen=True)
class Pillar:
    name: str
    stem: str
    branch: str
    stem_ten_god: str
    hidden: tuple[tuple[str,float,str], ...]
    growth_stage: str
    nayin: str
    void: tuple[str,str]
    palace: str
    time_window: str

    @property
    def text(self) -> str:
        return self.stem+self.branch

    def as_dict(self) -> dict:
        d=asdict(self)
        d["text"]=self.text
        return d

@dataclass(frozen=True)
class BaziChart:
    year: Pillar
    month: Pillar
    day: Pillar
    hour: Pillar
    gender: Optional[str] = None
    useful_elements: tuple[str,...] = ()
    unfavorable_elements: tuple[str,...] = ()
    metadata: Optional[dict] = None

    @property
    def day_master(self) -> str:
        return self.day.stem

    @property
    def pillars(self) -> tuple[Pillar,...]:
        return (self.year,self.month,self.day,self.hour)

    def as_dict(self) -> dict:
        return {
            "schema":"bazi.chart.v1","dayMaster":self.day_master,"gender":self.gender,
            "usefulElements":list(self.useful_elements),"unfavorableElements":list(self.unfavorable_elements),
            "pillars":{p.name:p.as_dict() for p in self.pillars},"metadata":self.metadata or {}
        }


def generate_luck_cycles(month_pillar: str, *, forward: bool, count: int = 8, start_age: float | None = None) -> list[dict]:
    """Generate pillar sequence for Da Yun from the natal month pillar.

    This function intentionally does not calculate start_age from solar-term
    distance; pass a calibrated start_age when known.
    """
    base=sexagenary_index(month_pillar)
    step=1 if forward else -1
    out=[]
    for n in range(1,count+1):
        item={"index":n,"pillar":sexagenary_pillar(base+step*n)}
        if start_age is not None:
            item["startAge"]=round(start_age+(n-1)*10,3)
            item["endAge"]=round(start_age+n*10,3)
        out.append(item)
    return out

def generate_small_luck(start_pillar: str, *, forward: bool, count: int = 10, start_age: int = 1) -> list[dict]:
    """Generate an explicitly-calibrated Xiao Yun sequence from start_pillar."""
    base=sexagenary_index(start_pillar); step=1 if forward else -1
    return [{"age":start_age+i,"pillar":sexagenary_pillar(base+step*i)} for i in range(count)]


def _make_pillar(name:str, text:str, day_stem:str) -> Pillar:
    sexagenary_index(text)
    stem, branch = text
    hidden = tuple((s,w,ten_god(day_stem,s)) for s,w in HIDDEN_STEMS[branch])
    return Pillar(name,stem,branch,"日主" if name=="day" else ten_god(day_stem,stem),hidden,growth_stage(day_stem,branch),nayin(text),void_branches(text),PALACE[name],TIME_WINDOWS[name])


def build_chart(year:str, month:str, day:str, hour:str, *, gender:Optional[str]=None,
                useful_elements:Iterable[str]=(), unfavorable_elements:Iterable[str]=(), metadata:Optional[dict]=None) -> BaziChart:
    day_stem=day[0]
    if day_stem not in STEMS:
        raise ValueError("invalid day stem")
    for e in list(useful_elements)+list(unfavorable_elements):
        if e not in "木火土金水": raise ValueError(f"invalid element {e}")
    return BaziChart(
        _make_pillar("year",year,day_stem), _make_pillar("month",month,day_stem),
        _make_pillar("day",day,day_stem), _make_pillar("hour",hour,day_stem), gender,
        tuple(useful_elements), tuple(unfavorable_elements), metadata or {})


def interactions(chart:BaziChart, extra_pillars:Iterable[str]=()) -> dict:
    pillars=[p.text for p in chart.pillars]+list(extra_pillars)
    stems=[p[0] for p in pillars]; branches=[p[1] for p in pillars]
    out={"stemCombines":[],"branchClashes":[],"branchHarmonies":[],"branchHarms":[],"trines":[]}
    for i in range(len(pillars)):
        for j in range(i+1,len(pillars)):
            if frozenset((stems[i],stems[j])) in STEM_COMBINES: out["stemCombines"].append([i,j,stems[i]+stems[j]])
            pair=frozenset((branches[i],branches[j]))
            if pair in BRANCH_CLASHES: out["branchClashes"].append([i,j,branches[i]+branches[j]])
            if pair in BRANCH_HARMONIES: out["branchHarmonies"].append([i,j,branches[i]+branches[j]])
            if pair in BRANCH_HARMS: out["branchHarms"].append([i,j,branches[i]+branches[j]])
    bset=set(branches)
    for group,elem in TRINES.items():
        if group.issubset(bset): out["trines"].append({"branches":"".join(sorted(group,key=BRANCHES.index)),"element":elem})
    return out
