"""The single inlined stylesheet, assembled from five styling sources."""

from __future__ import annotations

from .style_components import COMPONENTS_CSS
from .style_print import PRINT_CSS
from .style_screen import SCREEN_CSS
from .style_tokens import TOKENS_CSS
from .style_agents import AGENT_CSS

# Cascade order: tokens, screen rules, components, volume themes, print.
CSS = TOKENS_CSS + SCREEN_CSS + COMPONENTS_CSS + AGENT_CSS + PRINT_CSS

__all__ = ["CSS", "TOKENS_CSS", "SCREEN_CSS", "COMPONENTS_CSS", "AGENT_CSS", "PRINT_CSS"]
