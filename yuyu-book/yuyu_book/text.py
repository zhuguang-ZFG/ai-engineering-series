"""Text-scanning constants shared by config and unit parsing."""
from __future__ import annotations

import re

HAN_RE = re.compile(r"[\u4e00-\u9fff]")
# the subject index files translated terms here instead of under a Latin
# letter; "中" sorts after Z, so the block lands last without a special case
INDEX_CN_LETTER = "中"
FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})(.*)$")
