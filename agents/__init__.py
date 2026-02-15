"""
TrustGraph Multi-Agent System
Sistema de agentes inteligentes para gestión del conocimiento

Agentes:
- Callímaco (Καλλίμαχος): El bibliotecario que organiza y estructura
- Sócrates (Σωκράτης): El investigador que busca y sintetiza
- Morpheo (Μορφεύς): El guardián nocturno que optimiza y repara
"""

__version__ = "1.0.0"
__author__ = "TrustGraph Team"

from .callimaco import CallimacoAgent, CallimacoState
from .socrates import SocratesAgent, SocratesState
from .morpheo import MorpheoAgent, MorpheoState

__all__ = [
    "CallimacoAgent",
    "CallimacoState",
    "SocratesAgent",
    "SocratesState",
    "MorpheoAgent",
    "MorpheoState",
]