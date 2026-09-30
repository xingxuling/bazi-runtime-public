"""Bazi Runtime (BZR) v0.4.0.

Traditional metaphysics interpretation-assist runtime. It deliberately avoids
closed-world life-event taxonomies. Numeric scores are internal assistive
features, not scientific probabilities or factual forecasts.
"""
from .core import BaziChart, Pillar, build_chart, generate_luck_cycles, generate_small_luck
from .state import compute_state
from .semantic import interpret
from .transit import run_year, run_month, run_day, run_hour, run_minute, run_event
from .assist import build_signal_graph, build_structure_frames, build_semantic_atoms

__version__ = "0.4.0"
__all__ = [
    "BaziChart", "Pillar", "build_chart", "generate_luck_cycles", "generate_small_luck",
    "compute_state", "interpret", "run_year", "run_month", "run_day", "run_hour", "run_minute", "run_event",
    "build_signal_graph", "build_structure_frames", "build_semantic_atoms",
]

from .auxiliary import auxiliary_pillars
__all__.append("auxiliary_pillars")
