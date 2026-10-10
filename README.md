# See-through Windows (WebUI Wrapper)

> **Unofficial Windows installer + Gradio WebUI wrapper** for [See-through](https://github.com/shitagaki-lab/see-through), *"Single-image Layer Decomposition for Anime Characters"* (SIGGRAPH 2026). Turn one anime illustration into a fully-inpainted, layered PSD ready for Live2D/VTuber rigging.

**What this repo is:** portable `.bat` setup, a Gradio WebUI, and low-VRAM launchers for Windows. **What it is not:** a fork of the models. The installer clones the original upstream repo into `see-through/` at install time, so you always run genuine upstream code. This wrapper only launches it in a friendlier way.

## Quick Start

### Step 1: Install
Double-click `install_seethrough.bat` and wait for completion. This will:
- Check for Git (required, install from https://git-scm.com if missing)
- Install uv (fast Python package manager) if not present
- Clone the upstream see-through repository into `see-through/` folder
- Create a Python 3.12 virtual environment
- Install all dependencies (PyTorch with CUDA 12.8, mmcv, detectron2, SAM2, etc.)
- Install WebUI dependencies (Gradio)

**First run takes 10-30 minutes** depending on internet speed. Re-running the installer later also pulls the latest upstream code (`git pull`).

### Step 2: Run
After installation completes, launch the WebUI:
```
run_seethrough_webui.bat
```
Then open http://127.0.0.1:7860 in your browser.

## Available Scripts

| Script | Description | Usage |
|--------|-------------|-------|
| `install_seethrough.bat` | **One-time installer** (also updates upstream on re-run) | Run once to set up everything |
| `run_seethrough_webui.bat` | **Recommended** - Gradio WebUI | Double-click to launch, opens browser automatically |
| `run_seethrough.bat` | Qt UI (Live2D annotation tool, upstream) | Double-click to launch |
| `run_seethrough_cli.bat` | CLI inference (full quality) | Drag image onto file or `run_seethrough_cli.bat [image] [resolution]` |
| `run_seethrough_lowmem.bat` | CLI inference (low VRAM, NF4) | Drag image onto file or `run_seethrough_lowmem.bat [image] [resolution]` |
| `run_seethrough_blockswap.bat` | CLI inference (ultra-low VRAM bf16 blockswap, slowest) | `run_seethrough_blockswap.bat [image] [resolution]` |
| `run_seethrough_demo.bat` | Jupyter notebook demo (upstream) | Double-click to launch |

## Requirements

- **Git** - Must be installed on the system (https://git-scm.com/download/win)
- **Windows 10/11** with an **NVIDIA GPU** with CUDA support
- **VRAM Requirements**:
  - WebUI NF4 mode: ~5-7GB
  - WebUI Full bf16: ~10GB
  - WebUI Blockswap mode: lowest VRAM of all, but slowest
  - CPU Offload checkbox (NF4/Full only): ~4GB, slower
- Disk: ~30GB free (models + dependencies + cache)

## WebUI Features

- **Image Upload**: Drag & drop or click to upload PNG, JPG, or WebP (max 10MB, 4096x4096)
- **Inference Modes**:
  - NF4 Quantized (Recommended) - Lower VRAM, good quality
  - Full bf16 - Higher quality, more VRAM
  - Blockswap (Low-VRAM bf16) - Minimal VRAM, slowest; CPU-offload built in
- **Resolution**: 512-2048 (presets: 512, 768, 1024, 1280)
- **Inference Steps**: 10-50 (lower = faster, higher = better quality)
- **CPU Offload**: For minimal VRAM (~4GB) in NF4/Full modes; ignored in Blockswap (built-in)
- **Split Left/Right**: Separates eyes, ears, handwear, etc. into distinct layers
- **Seed Value**: Reproducible results with same seed
- **Real-time Progress**: Live status updates during inference (LayerDiff body/head passes, depth, PSD assembly)
- **Layer Preview Gallery**: Visual preview of all generated layers
- **Cancel Button**: Stop inference mid-process
- **Settings Persistence**: Remembers your last used settings
- **Open Output Folder**: Quick access to results

## Directory Structure

```
see-through-windows/            # THIS repo (the wrapper)
├── install_seethrough.bat      # One-time installer (run first)
├── common_setup.bat            # Shared setup for launch scripts (internal)
├── run_seethrough_webui.bat    # Launch WebUI (recommended)
├── run_seethrough.bat          # Launch Qt UI (upstream tool)
├── run_seethrough_cli.bat      # CLI inference (full quality)
├── run_seethrough_lowmem.bat   # CLI inference (low VRAM, NF4)
├── run_seethrough_blockswap.bat# CLI inference (ultra-low VRAM blockswap)
├── run_seethrough_demo.bat     # Jupyter demo (upstream)
├── uv/                         # Portable uv package manager (auto-downloaded, git-ignored)
└── webui/                      # Gradio WebUI source (the wrapper's own code)
    ├── launch.py               # Entry point
    ├── config.py               # Paths and configuration
    ├── inference.py            # Inference execution
    ├── ui_components.py        # UI layout and theme
    ├── utils.py                # Utility functions
    ├── logger.py               # Logging setup
    ├── settings.py             # Settings persistence
    └── test_inference.py       # Input validation tests (run: pytest webui/test_inference.py)
```

After installation, `see-through/` appears alongside these files. That is the **upstream repository** (cloned, git-ignored here). To update it manually: `git -C see-through pull`.

## Output

All WebUI outputs saved to: `see-through/workspace/ui_output/[image_name]_[timestamp]/`

Each run creates:
- `[layer_name].png` - Individual layer images
- `[image_name].psd` - Photoshop file with all layers
- `ui.log` - Inference log
- `stats.json` - Performance statistics

## Troubleshooting

**"Virtual environment not found"** - Run `install_seethrough.bat` first.

**CUDA out of memory** - Try in order:
- Use NF4 mode instead of Full bf16
- Lower resolution (512 or 768)
- Enable CPU Offload (NF4/Full modes)
- Switch to Blockswap mode (WebUI) or `run_seethrough_blockswap.bat` (CLI)

**Slow inference** - Normal on first run (model download + loading). Subsequent runs are faster. Blockswap and CPU-offload modes trade speed for VRAM, so expect a noticeably slower run.

**WebUI port in use** - Close the other instance or edit the port in `webui/launch.py`.

## Credits

- **Original project**: [See-through](https://github.com/shitagaki-lab/see-through) by shitagaki-lab, SIGGRAPH 2026 paper *"Single-image Layer Decomposition for Anime Characters"* ([arXiv:2602.03749](https://arxiv.org/abs/2602.03749)). All model code, weights, and research belong to them.
- **HuggingFace demo**: [24yearsold/see-through-demo](https://huggingface.co/spaces/24yearsold/see-through-demo)
- This wrapper only adds the Windows installer, Gradio WebUI, and launcher scripts on top. Please star and cite the original project.

## License

Apache License 2.0 - Same as the original See-through project.
