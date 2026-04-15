# See-through Windows Installer

Portable installer for [See-through](https://github.com/shitagaki-lab/see-through) - Single-image Layer Decomposition for Anime Characters.

## Quick Start

1. Run `install_seethrough.bat` - This will:
   - Check for Git (required)
   - Install uv (fast Python package manager) if not present
   - Clone the see-through repository
   - Create a virtual environment with Python 3.12
   - Install all dependencies including PyTorch with CUDA 12.8
   - Install the WebUI dependencies

2. After installation, use one of the following:

## Available Scripts

| Script | Description |
|--------|-------------|
| `run_seethrough_webui.bat` | **Recommended** - Launch Gradio WebUI (browser-based interface) |
| `run_seethrough.bat` | Launch Qt UI (Live2D annotation tool) |
| `run_seethrough_cli.bat image.png` | Run CLI inference (full quality) |
| `run_seethrough_lowmem.bat image.png` | Run CLI inference (low VRAM, ~8GB) |
| `run_seethrough_demo.bat` | Launch Jupyter notebook demo |

## Requirements

- **Git** - Must be installed on the system
- **NVIDIA GPU** with CUDA support
- **VRAM**:
  - WebUI (NF4 mode): ~5-7GB
  - WebUI (Full bf16): ~10GB
  - CLI lowmem: ~8GB

## WebUI Features

The Gradio WebUI provides:
- Upload image interface
- Resolution slider (512-2048)
- Inference mode selection (NF4 Quantized / Full bf16)
- CPU offload option for minimal VRAM
- Real-time progress display
- Layer preview gallery
- One-click output folder access

## Directory Structure

```
see-through-windows/
├── install_seethrough.bat      # Main installer
├── run_seethrough_webui.bat    # Launch WebUI
├── run_seethrough.bat          # Launch Qt UI
├── run_seethrough_cli.bat      # CLI inference
├── run_seethrough_lowmem.bat   # CLI inference (low VRAM)
├── run_seethrough_demo.bat     # Jupyter demo
└── webui/                      # Gradio WebUI source
    ├── launch.py
    ├── config.py
    ├── inference.py
    ├── ui_components.py
    ├── utils.py
    └── logger.py
```

After installation, a `see-through/` folder will be created containing the actual repository.

## Credits

- [See-through](https://github.com/shitagaki-lab/see-through) by shitagaki-lab
- SIGGRAPH 2026 paper: "Single-image Layer Decomposition for Anime Characters"

## License

Apache License 2.0 - Same as the original See-through project.
