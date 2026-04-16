"""Utility functions for See-through WebUI."""

import os
import platform
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .config import LAYER_ORDER, SKIP_TAGS, STAGE_MARKERS, OUTPUT_BASE

_LAYER_ORDER_MAP: Dict[str, int] = {tag: i for i, tag in enumerate(LAYER_ORDER)}

_last_vram_check: Tuple[float, Tuple[int, int]] = (0.0, (0, 0))
_VRAM_CACHE_SECONDS: float = 1.0

_pass_state: Dict[str, any] = {
    "stage": "",
    "last_progress_pct": -1,
    "pass_count": 0,
}


def _tag_sort_key(tag: str) -> int:
    return _LAYER_ORDER_MAP.get(tag, len(LAYER_ORDER))


def collect_layers(output_dir: str) -> List[Tuple[str, str]]:
    """Collect layer PNGs as (filepath, label) tuples for the gallery."""
    if not os.path.isdir(output_dir):
        return []
    layers = []
    for f in os.listdir(output_dir):
        if not f.endswith(".png"):
            continue
        tag = f[:-4]
        if tag.endswith("_depth") or tag in SKIP_TAGS:
            continue
        layers.append((os.path.join(output_dir, f), tag))
    layers.sort(key=lambda x: _tag_sort_key(x[1]))
    return layers


def parse_log_status(log_path: str) -> str:
    """Parse log file tail to extract current stage and progress bar."""
    if not os.path.exists(log_path):
        return "⏳ Initializing model... (May take a few minutes first time)"

    try:
        size = os.path.getsize(log_path)
        with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
            f.seek(max(0, size - 15000))
            tail = f.read()
    except Exception:
        return "⏳ Initializing model..."

    # Strip ANSI escape codes
    tail = re.sub(r"\x1b\[[0-9;]*[a-zA-Z]", "", tail)

    # Detect current stage (last match wins)
    current_stage = "⏳ Initializing model... (May take a few minutes first time)"
    current_stage_keyword = ""
    for keyword, label in STAGE_MARKERS:
        if keyword in tail:
            current_stage = label
            current_stage_keyword = keyword

    # Track LayerDiff passes (body -> head)
    if "Running LayerDiff" in current_stage:
        # Check if stage changed
        if _pass_state["stage"] != current_stage_keyword:
            _pass_state["stage"] = current_stage_keyword
            _pass_state["last_progress_pct"] = -1
            _pass_state["pass_count"] = 0
    elif current_stage_keyword and _pass_state.get("stage"):
        # Reset when moving to a different stage
        _pass_state["stage"] = ""
        _pass_state["last_progress_pct"] = -1
        _pass_state["pass_count"] = 0

    # Extract progress from AFTER the current stage marker
    progress_line = ""
    if current_stage_keyword:
        stage_pos = tail.rfind(current_stage_keyword)
        if stage_pos >= 0:
            tail_after_stage = tail[stage_pos:]
        else:
            tail_after_stage = tail
    else:
        tail_after_stage = tail

    # Find all percentage matches and take the LAST one (most recent)
    # Format: "0%| | 0/20" or "5%|5 | 1/20" or "100%|##########| 20/20"
    matches = list(re.finditer(r"(\d+)%\|[^|]*\|\s*(\d+)/(\d+)", tail_after_stage))
    if matches:
        last_match = matches[-1]
        pct = last_match.group(1)
        cur = last_match.group(2)
        total = last_match.group(3)
        pct_int = int(pct)
        
        # Detect pass transitions for LayerDiff (body -> head)
        if "Running LayerDiff" in current_stage:
            last_pct = _pass_state.get("last_progress_pct", -1)
            
            # Detect progress reset (100% -> 0% means new pass started)
            if last_pct >= 95 and pct_int <= 5 and _pass_state["pass_count"] == 0:
                _pass_state["pass_count"] = 1
            
            _pass_state["last_progress_pct"] = pct_int
            
            # Update stage label based on pass count
            if _pass_state["pass_count"] == 0:
                current_stage = "🎨 Running LayerDiff - Body Pass (hair, clothes, etc.)"
            else:
                current_stage = "🎨 Running LayerDiff - Head Pass (face, eyes, etc.)"
        
        filled = pct_int // 5
        empty = 20 - filled
        progress_bar = "█" * filled + "·" * empty
        progress_line = f"{pct}% [{progress_bar}] {cur}/{total}"

    # If no progress found, show indeterminate state
    if not progress_line and current_stage_keyword:
        progress_line = "⏳ Processing..."
    
    if progress_line:
        return f"{current_stage}\n{progress_line}"
    return current_stage


def open_output_folder(output_path: Optional[str], output_base: Optional[Path] = None) -> None:
    """Open the output folder in the system file manager (cross-platform)."""
    if output_base is None:
        output_base = OUTPUT_BASE

    if output_path:
        output_path = Path(output_path).resolve()
        output_base = Path(output_base).resolve()

        if not str(output_path).startswith(str(output_base)):
            output_path = None

    target = str(output_path) if output_path and os.path.isdir(output_path) else str(output_base)
    os.makedirs(target, exist_ok=True)

    system = platform.system()
    if system == "Windows":
        os.startfile(target)
    elif system == "Darwin":
        subprocess.run(["open", target], check=False)
    else:
        subprocess.run(["xdg-open", target], check=False)


def get_vram_used_mb() -> Tuple[int, int]:
    """Get total VRAM used in MB via nvidia-smi (cached to reduce overhead)."""
    global _last_vram_check
    
    current_time = time.time()
    cached_time, cached_values = _last_vram_check
    
    if current_time - cached_time < _VRAM_CACHE_SECONDS:
        return cached_values
    
    try:
        r = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.used,memory.total", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=3,
        )
        if r.returncode == 0:
            parts = r.stdout.strip().split(", ")
            if len(parts) == 2:
                result = (int(parts[0]), int(parts[1]))
                _last_vram_check = (current_time, result)
                return result
    except Exception:
        pass
    return 0, 0


def get_vram_display(baseline_mb: int) -> str:
    """Show VRAM usage: See-through delta + total."""
    used, total = get_vram_used_mb()
    if total == 0:
        return ""
    st_vram = max(0, used - baseline_mb)
    return f"🔍 See-through: ~{st_vram}MB | Total: {used}/{total}MB"