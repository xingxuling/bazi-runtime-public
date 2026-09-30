from __future__ import annotations
from .core import BaziChart
from .state import compute_state
from .schools import run_school_paths
from .arbiter import arbitrate
from .assist import build_signal_graph, build_structure_frames, build_semantic_atoms


def interpret(chart:BaziChart, *, extra_pillars=(), topic:str="general", question:str|None=None, analysis_context:dict|None=None, activation_policy:str="legacy")->dict:
    extra=list(extra_pillars)
    state=compute_state(chart,extra_pillars=extra,focus=topic,activation_policy=activation_policy)
    paths=run_school_paths(chart,state)
    graph=build_signal_graph(chart,extra,analysis_context=analysis_context)
    frames=build_structure_frames(chart,graph,state)
    atoms=build_semantic_atoms(graph)

    # Internal interpretation consistency only. Count independent structural cues,
    # then discount overt tension; never treat as real-world probability.
    evidence_count=sum(len(p.get("claims",[])) for p in paths) + len(graph.get("edges",[])) + len(graph.get("resonance",[])) + len(frames)
    contradiction=(
        state["metrics"]["unfavorablePressure"]*0.22
        + state["metrics"]["changePressure"]*0.20
        + max(0, state["metrics"]["bindingPressure"]-state["metrics"]["changePressure"])*0.08
    )
    coherence=max(0,min(100, 32+evidence_count*1.9+state["metrics"]["manifestation"]*0.18-contradiction*0.22))

    return {
      "schema":"bazi.interpretation.v2",
      "question":question,
      "topic":topic,
      "chart":chart.as_dict(),
      "state":state,
      "signalGraph":graph,
      "structureFrames":frames,
      "semanticAtoms":atoms,
      "schoolPaths":paths,
      "arbitration":arbitrate(paths),
      "evidenceCoherence":round(coherence,1),
      "contradictionIndex":round(contradiction,1),
      "boundary":(
          "BZR does not enumerate or rank a closed list of life-event categories. "
          "It exposes structural signals, causal tensions and symbolic atoms for contextual interpretation. "
          "Scores are internal interpretation aids, not real-world probabilities or scientific measurements."
      )
    }
