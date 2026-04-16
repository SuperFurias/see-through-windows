# See-through Windows Installer

Portable installer for [See-through](https://github.com/shitagaki-lab/see-through) - Single-image Layer Decomposition for Anime Characters.

## Quick Start

### Step 1: Install
Double-click `install_seethrough.bat` and wait for completion. This will:
- Check for Git (required, install from https://git-scm.com if missing)
- Install uv (fast Python package manager) if not present
- Clone the see-through repository into `see-through/` folder
- Create a Python 3.12 virtual environment
- Install all dependencies (PyTorch with CUDA 12.8, mmcv, detectron2, SAM2, etc.)
- Install WebUI dependencies (Gradio)

**First run takes 10-30 minutes** depending on internet speed.

### Step 2: Run
After installation completes, launch the WebUI:
```
run_seethrough_webui.bat
```
Then open http://127.0.0.1:7860 in your browser.

## Available Scripts

| Script | Description | Usage |
|--------|-------------|-------|
| `install_seethrough.bat` | **One-time installer** | Run once to set up everything |
| `run_seethrough_webui.bat` | **Recommended** - Gradio WebUI | Double-click to launch, opens browser automatically |
| `run_seethrough.bat` | Qt UI (Live2D annotation tool) | Double-click to launch |
| `run_seethrough_cli.bat` | CLI inference (full quality) | Drag image onto file or run with path argument |
| `run_seethrough_lowmem.bat` | CLI inference (low VRAM) | Drag image onto file or run with path argument |
| `run_seethrough_demo.bat` | Jupyter notebook demo | Double-click to launch |

## Requirements

- **Git** - Must be installed on the system (https://git-scm.com/download/win)
- **NVIDIA GPU** with CUDA support
- **VRAM Requirements**:
  - WebUI NF4 mode: ~5-7GB
  - WebUI Full bf16: ~10GB
  - CLI lowmem: ~8GB
  - CPU Offload mode: ~4GB (slower)

## WebUI Features

- **Image Upload**: Drag & drop or click to upload PNG, JPG, or WebP (max 10MB, 4096x4096)
- **Inference Modes**:
  - NF4 Quantized (Recommended) - Lower VRAM, good quality
  - Full bf16 - Higher quality, more VRAM
- **Resolution**: 512-2048 (presets: 512, 768, 1024, 1280)
- **Inference Steps**: 10-50 (lower = faster, higher = better quality)
- **CPU Offload**: For minimal VRAM (~4GB), slower but works on weaker GPUs
- **Split Left/Right**: Separates hands, eyes, etc. into distinct layers
- **Seed Value**: Reproducible results with same seed
- **Real-time Progress**: Live status updates during inference
- **Layer Preview Gallery**: Visual preview of all generated layers
- **Cancel Button**: Stop inference mid-process
- **Settings Persistence**: Remembers your last used settings
- **Open Output Folder**: Quick access to results

## Directory Structure

```
see-through-windows/
├── install_seethrough.bat    # One-time installer (run first)
├── common_setup.bat          # Shared setup for launch scripts (internal)
├── run_seethrough_webui.bat  # Launch WebUI (recommended)
├── run_seethrough.bat        # Launch Qt UI
├── run_seethrough_cli.bat    # CLI inference (full quality)
├── run_seethrough_lowmem.bat # CLI inference (low VRAM)
├── run_seethrough_demo.bat   # Jupyter demo
└── webui/                    # Gradio WebUI source
    ├── launch.py             # Entry point
    ├── config.py             # Paths and configuration
    ├── inference.py          # Inference execution
    ├── ui_components.py      # UI layout and theme
    ├── utils.py              # Utility functions
    ├── logger.py             # Logging setup
    ├── settings.py           # Settings persistence
    └── test_inference.py     # Input validation tests
```

After installation, `see-through/` folder is created containing the actual repository.

## Output

All outputs saved to: `see-through/workspace/ui_output/[image_name]_[timestamp]/`

Each run creates:
- `[layer_name].png` - Individual layer images
- `[image_name].psd` - Photoshop file with all layers
- `ui.log` - Inference log
- `stats.json` - Performance statistics

## Troubleshooting

**"Virtual environment not found"** - Run `install_seethrough.bat` first.

**CUDA out of memory** - Try:
- Use NF4 mode instead of Full bf16
- Lower resolution (512 or 768)
- Enable CPU Offload
- Use `run_seethrough_lowmem.bat` for CLI

**Slow inference** - Normal on first run (model loading). Subsequent runs are faster.

## Credits

- [See-through](https://github.com/shitagaki-lab/see-through) by shitagaki-lab
- SIGGRAPH 2026 paper: "Single-image Layer Decomposition for Anime Characters"

## License

Apache License 2.0 - Same as the original See-through project.
