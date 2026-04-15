"""Inference execution and management for See-through UI."""

import os
import sys
import time
import subprocess
from pathlib import Path
from PIL import Image
import gradio as gr

from .config import SCRIPT_PATH, HF_CACHE_DIR, OUTPUT_BASE, SEETHROUGH_ROOT
from .utils import collect_layers, parse_log_status, get_vram_display, get_vram_used_mb
from .logger import logger


def validate_input(image_path, mode_str, resolution, seed_val, inference_steps):
    """Validate inference input parameters."""
    if image_path is None:
        raise gr.Error("Please upload an image")

    # Validate image file exists and is readable
    img_path = Path(image_path)
    if not img_path.exists():
        raise gr.Error("Image file not found")

    # Security check: file size limit (10MB)
    file_size_mb = img_path.stat().st_size / (1024 * 1024)
    if file_size_mb > 10:
        raise gr.Error(f"Image file too large: {file_size_mb:.1f}MB. Maximum allowed is 10MB.")

    try:
        from PIL import Image
        with Image.open(image_path) as img:
            if img.format.lower() not in ["png", "jpeg", "jpg", "webp"]:
                raise gr.Error(f"Unsupported image format: {img.format}. Please use PNG, JPG, or WebP.")

            # Validate image dimensions
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


def run_inference(image_path, mode_str, resolution, seed_val, tblr_split, inference_steps, cpu_offload):
    """Run See-through inference. Generator that yields progressive updates."""
    # Validate inputs
    seed_val, resolution, inference_steps = validate_input(
        image_path, mode_str, resolution, seed_val, inference_steps
    )
    logger.info(f"Starting inference for image: {image_path}")
    logger.info(f"Parameters: mode={mode_str}, resolution={resolution}, seed={seed_val}, steps={inference_steps}")

    # --- Setup ---
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

    yield [], str(save_dir), "⏳ Starting inference..."

    # --- Build command ---
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
    start_time = time.time()
    logger.debug(f"Running command: {' '.join(cmd)}")

    # Record baseline VRAM for tracking
    baseline_vram, _ = get_vram_used_mb()
    logger.info(f"Baseline VRAM: {baseline_vram}MB")

    # --- Run subprocess ---
    proc = None
    try:
        with open(log_path, "w", encoding="utf-8") as log_file:
            proc = subprocess.Popen(
                cmd,
                cwd=str(SEETHROUGH_ROOT),
                stdout=log_file,
                stderr=subprocess.STDOUT,
                env=env,
            )

        while proc.poll() is None:
            time.sleep(2)
            layers = collect_layers(layer_dir)
            elapsed = time.time() - start_time
            elapsed_str = f"{int(elapsed // 60)}:{int(elapsed % 60):02d}"

            # Parse log for detailed status
            log_status = parse_log_status(str(log_path))
            vram = get_vram_display(baseline_vram)
            status_text = f"{log_status}\n⏱️ Elapsed Time: {elapsed_str}"
            if layers:
                status_text += f" | Layers: {len(layers)}"
            if vram:
                status_text += f"\n{vram}"

            yield layers, str(save_dir), status_text
    except GeneratorExit:
        # Handle cancellation
        if proc and proc.poll() is None:
            try:
                proc.terminate()
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
        raise
    except Exception as e:
        if proc and proc.poll() is None:
            try:
                proc.terminate()
                proc.wait(timeout=3)
            except:
                pass
        raise gr.Error(f"Inference interrupted: {str(e)}")

    # --- Check result ---
    if proc.returncode != 0:
        err_tail = ""
        if log_path.exists():
            try:
                err_tail = log_path.read_text(encoding="utf-8")[-500:]
            except Exception:
                err_tail = "Could not read error log"
        logger.error(f"Inference failed with exit code {proc.returncode}")
        logger.debug(f"Error log tail: {err_tail}")
        raise gr.Error(f"Inference failed (exit code: {proc.returncode})\n{err_tail}")

    # --- Final results ---
    gallery = collect_layers(layer_dir)
    elapsed = time.time() - start_time
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)
    logger.info(f"Inference completed successfully in {minutes}m{seconds}s")
    logger.info(f"Generated {len(gallery)} layers")
    mode_label = "NF4" if is_nf4 else "Full bf16"
    if cpu_offload:
        mode_label += " + CPU Offload"

    # Count PSD files
    psd_count = sum(
        1 for f in os.listdir(str(save_dir))
        if f.endswith(".psd")
    ) if save_dir.exists() else 0

    # Read peak VRAM from stats.json
    import json as _json
    peak_vram_str = ""
    stats_path = save_dir / safe_name / "stats.json"
    if stats_path.exists():
        try:
            with open(stats_path, "r") as sf:
                stats_data = _json.load(sf)
            peak_gb = stats_data.get("peak_vram_gb", 0)
            peak_vram_str = f" | Peak VRAM: {peak_gb:.1f}GB"
        except Exception:
            pass

    status = (
        f"✅ Completed! ({minutes}m{seconds}s)\n"
        f"Mode: {mode_label} | Resolution: {resolution} | "
        f"Layers: {len(gallery)} | PSD: {psd_count} files{peak_vram_str}\n"
        f"📂 Output: {save_dir}"
    )

    yield gallery, str(save_dir), status