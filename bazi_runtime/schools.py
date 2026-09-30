from __future__ import annotations
from collections import Counter
from .core import BaziChart, ELEMENT, interactions

STEM_IMAGE={"甲":"树木/直立/生发","乙":"花草/柔曲/细部","丙":"太阳/显照/外放","丁":"灯火/细光/文明","戊":"厚土/平台","己":"田园/承载","庚":"金属/道路/决断","辛":"精金/器具/精细","壬":"江河/流动","癸":"雨露/隐流"}
BRANCH_IMAGE={"子":"水/流动/夜","丑":"湿土/库","寅":"大木/启动","卯":"花木/伸展","辰":"湿土/水库","巳":"火/声音/显化","午":"旺火/显露","未":"土库/收纳","申":"金/移动","酉":"精金/工具","戌":"火库/燥土","亥":"水/远流"}

def ziping_path(chart:BaziChart, state:dict) -> dict:
    m=state["metrics"]
    claims=[]
    if chart.useful_elements:
        claims.append({"claim":"用神通道可访问度","value":m["usefulElementAccess"],"basis":"configured useful elements + current elemental profile"})
    claims.append({"claim":"日主承载状态","value":m["dayMasterCapacity"],"basis":"season-weighted support/drain/control heuristic"})
    claims.append({"claim":"结构稳定度","value":m["structuralStability"],"basis":"冲害 + 承载偏移"})
    return {"school":"ziping","claims":claims,"priority":"primary_for_balance_and_outcome"}

def coordinate_path(chart:BaziChart, state:dict) -> dict:
    return {"school":"coordinate","claims":[
        {"claim":"时间分层","value":{p.name:p.time_window for p in chart.pillars},"basis":"four-pillar temporal mapping in source tutorial"},
        {"claim":"结构激活","value":state["metrics"]["structureActivation"],"basis":"transit + relation activation heuristic"}
    ],"priority":"actor_time_space_coordinates_only"}

def blind_image_path(chart:BaziChart, state:dict) -> dict:
    stems=Counter(p.stem for p in chart.pillars); branches=Counter(p.branch for p in chart.pillars)
    images=[]
    for p in chart.pillars:
        images.append({"pillar":p.name,"text":p.text,"stemImage":STEM_IMAGE[p.stem],"branchImage":BRANCH_IMAGE[p.branch],"palace":p.palace})
    repeated={"stems":{k:v for k,v in stems.items() if v>1},"branches":{k:v for k,v in branches.items() if v>1}}
    return {"school":"blind_image","claims":[{"claim":"柱象","value":images,"basis":"干支物象+宫位"},{"claim":"重复信息","value":repeated,"basis":"same-symbol recurrence"}],"priority":"parallel_symbolic_path","warning":"does not override balance/useful-element path"}

def auxiliary_path(chart:BaziChart, state:dict) -> dict:
    return {"school":"auxiliary","claims":[
        {"claim":"纳音", "value":{p.name:p.nayin for p in chart.pillars},"basis":"60 Jiazi Nayin"},
        {"claim":"十二长生", "value":{p.name:p.growth_stage for p in chart.pillars},"basis":"day-master growth stage"},
        {"claim":"空亡", "value":{p.name:list(p.void) for p in chart.pillars},"basis":"xun void"}
    ],"priority":"supporting_only"}

def run_school_paths(chart:BaziChart,state:dict)->list[dict]:
    return [ziping_path(chart,state),coordinate_path(chart,state),blind_image_path(chart,state),auxiliary_path(chart,state)]
