"""Inference execution and management for See-through UI."""

import json
import os
import sys
import time
import subprocess
import threading
from pathlib import Path
from typing import Generator, List, Tuple, Optional, Dict, Any
from PIL import Image
import gradio as gr

from .config import SCRIPT_PATH, HF_CACHE_DIR, OUTPUT_BASE, SEETHROUGH_ROOT
from .utils import collect_layers, parse_log_status, get_vram_display, get_vram_used_mb
from .logger import logger


_inference_state: Dict[str, Any] = {
    "running": False,
    "proc": None,
    "log_file": None,
    "save_dir": None,
    "layer_dir": None,
    "log_path": None,
    "baseline_vram": 0,
    "start_time": 0,
    "is_nf4": True,
    "cpu_offload": False,
    "resolution": 512,
}


def validate_input(image_path: Optional[str], mode_str: str, resolution: int, seed_val: int, inference_steps: int) -> Tuple[int, int, int]:
    """Validate inference input parameters."""
    if image_path is None:
        raise gr.Error("Please upload an image")

    img_path = Path(image_path)
    if not img_path.exists():
        raise gr.Error("Image file not found")

    file_size_mb = img_path.stat().st_size / (1024 * 1024)
    if file_size_mb > 10:
        raise gr.Error(f"Image file too large: {file_size_mb:.1f}MB. Maximum allowed is 10MB.")

    try:
        with Image.open(image_path) as img:
            if img.format.lower() not in ["png", "jpeg", "jpg", "webp"]:
                raise gr.Error(f"Unsupported image format: {img.format}. Please use PNG, JPG, or WebP.")
            width, height = img.size
            if width < 128 or height < 128:
                raise gr.Error(f"Image too small: {width}x{height}. Minimum required is 128x128.")
            if width > 4096 or height > 4096:
                raise gr.Error(f"Image too large: {width}x{height}. Maximum allowed is 4096x4096.")
    except Exception as e:
        raise gr.Error(f"Invalid image file: {str(e)}")

    if not mode_str or not any(m in mode_str for m in ["NF4", "Full bf16"]):
        raise gr.Error("Invalid inference mode selected")

    try:
        seed_val = int(seed_val)
        if seed_val < 0:
            raise ValueError("Seed must be a non-negative integer")
    except (ValueError, TypeError):
        raise gr.Error("Invalid seed value. Must be a non-negative integer.")

    try:
        resolution = int(resolution)
        resolution = max(512, min(2048, round(resolution / 64) * 64))
    except (ValueError, TypeError):
        raise gr.Error("Invalid resolution value. Must be between 512 and 2048.")

    try:
        inference_steps = int(inference_steps)
        if not (10 <= inference_steps <= 50):
            raise ValueError("Inference steps must be between 10 and 50")
    except (ValueError, TypeError):
        raise gr.Error("Invalid inference steps value. Must be between 10 and 50.")

    return seed_val, resolution, inference_steps


def start_inference(image_path: str, mode_str: str, resolution: int, seed_val: int, tblr_split: bool, inference_steps: int, cpu_offload: bool) -> Tuple[str, str]:
    """Start inference in background. Returns (save_dir, status)."""
    global _inference_state
    
    seed_val, resolution, inference_steps = validate_input(image_path, mode_str, resolution, seed_val, inference_steps)
    
    logger.info(f"Starting inference for image: {image_path}")
    logger.info(f"Parameters: mode={mode_str}, resolution={resolution}, seed={seed_val}, steps={inference_steps}")

    is_nf4 = "NF4" in mode_str
    img_stem = Path(image_path).stem

    safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in img_stem)
    if not safe_name:
        safe_name = "image"

    run_id = f"{safe_name}_{int(time.time())}"
    save_dir = OUTPUT_BASE / run_id
    save_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Created output directory: {save_dir}")

    input_path = save_dir / f"{safe_name}.png"
    try:
        Image.open(image_path).convert("RGBA").save(str(input_path))
        logger.debug(f"Saved processed input to: {input_path}")
    except Exception as e:
        logger.error(f"Failed to process input image: {e}")
        raise gr.Error(f"Failed to process input image: {str(e)}")

    layer_dir = str(save_dir / safe_name)
    log_path = save_dir / "ui.log"

    cmd = [
        sys.executable, str(SCRIPT_PATH),
        "--srcp", str(input_path),
        "--save_to_psd",
        "--save_dir", str(save_dir),
        "--seed", str(seed_val),
        "--resolution", str(resolution),
        "--num_inference_steps", str(inference_steps),
        "--quant_mode", "nf4" if is_nf4 else "none",
        "--no_group_offload",
    ]
    if not tblr_split:
        cmd.append("--no_tblr_split")
    if cpu_offload:
        cmd.append("--cpu_offload")

    env = {
        **os.environ,
        "HF_HOME": str(HF_CACHE_DIR),
        "PYTHONPATH": str(SEETHROUGH_ROOT) + os.pathsep + str(SEETHROUGH_ROOT / "common") + os.pathsep + os.environ.get("PYTHONPATH", "")
    }
    
    logger.debug(f"Running command: {' '.join(cmd)}")
    start_time = time.time()
    baseline_vram, _ = get_vram_used_mb()
    logger.info(f"Baseline VRAM: {baseline_vram}MB")

    log_file = open(log_path, "w", encoding="utf-8")
    proc = subprocess.Popen(
        cmd,
        cwd=str(SEETHROUGH_ROOT),
        stdout=log_file,
        stderr=subprocess.STDOUT,
        env=env,
    )

    _inference_state = {
        "running": True,
        "proc": proc,
        "log_file": log_file,
        "save_dir": str(save_dir),
        "layer_dir": layer_dir,
        "log_path": str(log_path),
        "baseline_vram": baseline_vram,
        "start_time": start_time,
        "is_nf4": is_nf4,
        "cpu_offload": cpu_offload,
        "resolution": resolution,
        "safe_name": safe_name,
    }

    return str(save_dir), "⏳ Inference started..."


def poll_inference(save_dir: str) -> Tuple[List, str, str, Any]:
    """Poll inference status. Returns (layers, save_dir, status, timer_update)."""
    global _inference_state
    
    if not _inference_state.get("running", False):
        return [], save_dir, "❌ No inference running", gr.Timer(active=False)

    proc = _inference_state.get("proc")
    if proc is None:
        return [], save_dir, "❌ No process found", gr.Timer(active=False)

    log_file = _inference_state.get("log_file")
    if log_file:
        log_file.flush()
        os.fsync(log_file.fileno())

    layer_dir = _inference_state.get("layer_dir", "")
    log_path = _inference_state.get("log_path", "")
    log_path = _inference_state.get("log_path", "")
    baseline_vram = _inference_state.get("baseline_vram", 0)
    start_time = _inference_state.get("start_time", time.time())

    if proc.poll() is not None:
        _inference_state["running"] = False
        if log_file:
            log_file.close()

        if proc.returncode != 0:
            err_tail = ""
            if log_path and Path(log_path).exists():
                try:
                    with open(log_path, "r", encoding="utf-8") as f:
                        f.seek(0, 2)
                        f.seek(max(0, f.tell() - 500))
                        err_tail = f.read()
                except Exception:
                    err_tail = "Could not read error log"
            logger.error(f"Inference failed with exit code {proc.returncode}")
            return [], save_dir, f"❌ Inference failed (exit code: {proc.returncode})\n{err_tail}", gr.Timer(active=False)

        elapsed = time.time() - start_time
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        
        gallery = collect_layers(layer_dir)
        logger.info(f"Inference completed successfully in {minutes}m{seconds}s")
        logger.info(f"Generated {len(gallery)} layers")

        save_dir_path = Path(save_dir)
        psd_count = sum(1 for f in os.listdir(save_dir) if f.endswith(".psd")) if save_dir_path.exists() else 0

        peak_vram_str = ""
        safe_name = _inference_state.get("safe_name", "")
        stats_path = save_dir_path / safe_name / "stats.json"
        if stats_path.exists():
            try:
                with open(stats_path, "r") as sf:
                    stats_data = json.load(sf)
                peak_gb = stats_data.get("peak_vram_gb", 0)
                peak_vram_str = f" | Peak VRAM: {peak_gb:.1f}GB"
            except Exception:
                pass

        mode_label = "NF4" if _inference_state.get("is_nf4", True) else "Full bf16"
        if _inference_state.get("cpu_offload", False):
            mode_label += " + CPU Offload"

        status = (
            f"✅ Completed! ({minutes}m{seconds}s)\n"
            f"Mode: {mode_label} | Resolution: {_inference_state.get('resolution', 512)} | "
            f"Layers: {len(gallery)} | PSD: {psd_count} files{peak_vram_str}\n"
            f"📂 Output: {save_dir}"
        )

        return gallery, save_dir, status, gr.Timer(active=False)

    layers = collect_layers(layer_dir)
    elapsed = time.time() - start_time
    elapsed_str = f"{int(elapsed // 60)}:{int(elapsed % 60):02d}"

    log_status = parse_log_status(log_path)
    vram = get_vram_display(baseline_vram)
    status_text = f"{log_status}\n⏱️ Elapsed Time: {elapsed_str}"
    if layers:
        status_text += f" | Layers: {len(layers)}"
    if vram:
        status_text += f"\n{vram}"

    logger.debug(f"Poll: elapsed={elapsed:.1f}s, start_time={start_time}, layers={len(layers)}")

    return layers, save_dir, status_text, gr.Timer()
