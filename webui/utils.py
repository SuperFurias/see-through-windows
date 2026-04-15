"""Utility functions for See-through WebUI."""

import os
import re
import subprocess
from pathlib import Path

from .config import LAYER_ORDER, SKIP_TAGS, STAGE_MARKERS, OUTPUT_BASE


def _tag_sort_key(tag):
    try:
        return LAYER_ORDER.index(tag)
    except ValueError:
        return len(LAYER_ORDER)


def collect_layers(output_dir):
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


def parse_log_status(log_path):
    """Parse log file tail to extract current stage and progress bar."""
    if not os.path.exists(log_path):
        return "⏳ Initializing model... (May take a few minutes first time)"

    try:
        size = os.path.getsize(log_path)
        with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
            f.seek(max(0, size - 6000))
            tail = f.read()
    except Exception:
        return "⏳ Initializing model..."

    # Strip ANSI escape codes
    tail = re.sub(r"\x1b\[[0-9;]*[a-zA-Z]", "", tail)

    # Detect current stage (last match wins)
    current_stage = "⏳ Initializing model... (May take a few minutes first time)"
    for keyword, label in STAGE_MARKERS:
        if keyword in tail:
            current_stage = label

    # Extract latest tqdm / loading progress from \r-delimited segments
    progress_line = ""
    parts = tail.split("\r")
    for part in reversed(parts):
        part = part.strip()
        if not part:
            continue

        # tqdm diffusion steps: " 50%|█████     | 15/30 [01:38<01:40, 6.69s/it]"
        m = re.search(
            r"(\d+)%\|([^|]+)\|\s*(\d+)/(\d+)\s*\[([^\]<]+)<([^\]]+)\]", part
        )
        if m:
            pct, bar, cur, total, elapsed, eta = m.groups()
            progress_line = f"{pct}% |{bar.strip()}| {cur}/{total} | ⏱️ {elapsed} | ⏳ ETA: {eta}"
            break

        # Fallback for format without ETA
        m = re.search(
            r"(\d+)%\|([^|]+)\|\s*(\d+)/(\d+)\s*\[([^\]]+)\]", part
        )
        if m:
            pct, bar, cur, total, timing = m.groups()
            progress_line = f"{pct}% |{bar.strip()}| {cur}/{total} [{timing}]"
            break

        # Loading weights / pipeline components
        m = re.search(r"Loading (\w+).*?(\d+)%\|([^|]+)\|\s*(\d+)/(\d+)", part)
        if m:
            what, pct, bar, cur, total = m.groups()
            label = "Loading Weights" if what == "weights" else "Loading Pipeline"
            progress_line = f"{label}: {pct}% |{bar.strip()}| {cur}/{total}"
            break

    if progress_line:
        return f"{current_stage}\n{progress_line}"
    return current_stage


def open_output_folder(output_path, output_base=None):
    """Open the output folder in Windows Explorer."""
    if output_base is None:
        output_base = OUTPUT_BASE

    # Sanitize path and prevent directory traversal
    if output_path:
        output_path = Path(output_path).resolve()
        output_base = Path(output_base).resolve()

        # Ensure path is within output base
        if not str(output_path).startswith(str(output_base)):
            output_path = None

    target = output_path if output_path and os.path.isdir(output_path) else str(output_base)
    os.makedirs(target, exist_ok=True)
    os.startfile(target)


def get_vram_used_mb():
    """Get total VRAM used in MB via nvidia-smi."""
    try:
        r = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.used,memory.total",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=3,
        )
        if r.returncode == 0:
            used, total = r.stdout.strip().split(", ")
            return int(used), int(total)
    except Exception:
        pass
    return 0, 0


def get_vram_display(baseline_mb):
    """Show VRAM usage: See-through delta + total."""
    used, total = get_vram_used_mb()
    if total == 0:
        return ""
    st_vram = max(0, used - baseline_mb)
    return f"🔍 See-through: ~{st_vram}MB | Total: {used}/{total}MB"