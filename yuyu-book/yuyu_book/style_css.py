"""The single inlined stylesheet, assembled from four styling sources."""

from __future__ import annotations

from .style_components import COMPONENTS_CSS
from .style_print import PRINT_CSS
from .style_screen import SCREEN_CSS
from .style_tokens import TOKENS_CSS

# Order is the cascade: tokens, base screen rules, component rules, print.
CSS = TOKENS_CSS + SCREEN_CSS + COMPONENTS_CSS + PRINT_CSS

__all__ = ["CSS", "TOKENS_CSS", "SCREEN_CSS", "COMPONENTS_CSS", "PRINT_CSS"]
