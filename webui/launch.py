"""See-through WebUI Launcher

Gradio-based web interface for See-through layer decomposition.
"""

import sys
from pathlib import Path

# Add the parent directory (containing webui) to path
webui_dir = Path(__file__).resolve().parent
if str(webui_dir) not in sys.path:
    sys.path.insert(0, str(webui_dir))

from webui import build_ui, run_inference, open_output_folder, OUTPUT_BASE


def open_folder_wrapper(output_path):
    """Wrapper for open_output_folder with base path."""
    return open_output_folder(output_path, OUTPUT_BASE)


if __name__ == "__main__":
    demo, theme, css = build_ui(run_inference, open_folder_wrapper)
    demo.queue()
    demo.launch(
        inbrowser=True,
        server_name="127.0.0.1",
        server_port=7860,
    )