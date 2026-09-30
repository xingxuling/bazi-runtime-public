from __future__ import annotations


def arbitrate(paths:list[dict]) -> dict:
    claims=[]
    for p in paths:
        for c in p.get("claims",[]):
            claims.append({"school":p["school"],**c})
    return {
      "schema":"bazi.arbitration.v2",
      "mode":"non-blending",
      "claims":claims,
      "rules":[
        "子平路径负责平衡、用忌、承载与结果倾向；盲派象法不覆盖其结论。",
        "人物/时空路径只提供定位坐标，不把十神或宫位硬编码成封闭现实事件。",
        "盲派与辅助项提供象义、重复、长生、空亡等修饰信号，不单独决定现实事件。",
        "冲突保留为并列结构；具体事件由问题语境与解释器根据证据生成，而不是由运行时枚举。"
      ]
    }
