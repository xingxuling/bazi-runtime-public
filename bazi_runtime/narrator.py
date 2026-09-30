from __future__ import annotations


def narrate(result:dict)->str:
    m=result["state"]["metrics"]
    lines=[]
    if result.get("question"):
        lines.append(f"问题：{result['question']}")
    frames=result.get("structureFrames") or []
    if frames:
        top=frames[0]
        lines.append(f"主结构：{top['label']}（结构强度 {top['strength']}）。")
        if len(frames)>1:
            lines.append("次结构："+"；".join(f"{x['label']}（{x['strength']}）" for x in frames[1:4])+"。")
    lines.append(
        f"状态：结构激活 {m['structureActivation']}；变化压力 {m['changePressure']}；绑定压力 {m['bindingPressure']}；"
        f"兑现 {m['manifestation']}；稳定 {m['structuralStability']}；用神通道 {m['usefulElementAccess']}。"
    )
    if m['unfavorablePressure']>=55:
        lines.append("约束：忌神压力偏高；出现强信号不等于顺利兑现。")
    if m['dayMasterCapacity']<=-25:
        lines.append("承载：当前承载偏弱，强变化更依赖外部支撑或节奏控制。")
    elif m['dayMasterCapacity']>=25:
        lines.append("承载：当前承载较强，具备主动响应结构变化的条件。")
    if m['changePressure']>=50:
        lines.append("变化：冲、害、刑、驿马等切换类信号明显，具体落到何种现实事件需结合问题语境。")
    if m['bindingPressure']>=50:
        lines.append("牵制：合、三合等聚合/绑定信号明显，可能表现为聚合、绑定、牵连或难以立即脱开。")
    lines.append(f"解释一致度：{result['evidenceCoherence']}（仅表示运行时内部证据一致性，不是概率）。")
    lines.append("事件边界：Runtime 不预设封闭的人生事件清单，只提供盘面结构、作用关系与辅助语义。")
    return "\n".join(lines)
