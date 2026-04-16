"""UI Components and theme configuration for See-through."""

from typing import Any, Callable, Tuple

import gradio as gr

from .config import CUSTOM_CSS
from .settings import load_settings, save_settings


def create_theme():
    """Create custom Gradio theme."""
    return gr.themes.Soft(
        primary_hue=gr.themes.Color(
            c50="#fef7f0", c100="#fde8d4", c200="#fbd0a8",
            c300="#f5b47a", c400="#f0a050", c500="#e8985a",
            c600="#d88a4e", c700="#c07838", c800="#a0632e",
            c900="#7a4c24", c950="#5a3818",
        ),
        secondary_hue="orange",
        neutral_hue=gr.themes.Color(
            c50="#f9f9f7", c100="#f3f3f0", c200="#ededea",
            c300="#d8d8d5", c400="#b0b0ad", c500="#9090a0",
            c600="#5c5c72", c700="#4a4a5e", c800="#2d2d3a",
            c900="#1e1e28", c950="#141420",
        ),
        font=[gr.themes.GoogleFont("Inter"), "system-ui", "sans-serif"],
        font_mono=["Consolas", "Fira Code", "monospace"],
    )


def build_ui(start_inference_fn: Callable, poll_inference_fn: Callable, open_folder_fn: Callable) -> Tuple[Any, Any, str]:
    """Build and return the Gradio UI Blocks and configuration."""
    theme = create_theme()
    saved = load_settings()

    with gr.Blocks(title="See-through UI") as demo:
        output_path_state = gr.State(value="")

        gr.Markdown(
            "# 🔍 See-through — Anime Illustration Layer Decomposition\n"
            "Performs semantic decomposition of one anime illustration into up to 24 layers.\n"
            "[GitHub](https://github.com/shitagaki-lab/see-through) | "
            "[Paper](https://arxiv.org/abs/2602.03749) | "
            "SIGGRAPH 2026",
            elem_classes=["header-text"],
        )

        with gr.Row():
            with gr.Column(scale=1, min_width=320):
                input_image = gr.Image(type="filepath", label="Input Image", height=350)

                with gr.Group():
                    mode = gr.Radio(
                        choices=[
                            "NF4 Quantized (Recommended・VRAM ~7GB)",
                            "Full bf16 (High Quality・VRAM ~10GB)",
                        ],
                        value=saved.get("mode", "NF4 Quantized (Recommended・VRAM ~7GB)"),
                        label="Inference Mode",
                    )
                    with gr.Row():
                        resolution = gr.Slider(
                            minimum=512, maximum=2048, step=64, value=saved.get("resolution", 768),
                            label="Resolution",
                            info="512: ~4GB / 768: ~5GB / 1024: ~7GB / 1280: ~9GB (NF4)",
                        )
                        resolution_preset = gr.Dropdown(
                            choices=["512", "768", "1024", "1280"],
                            value=str(saved.get("resolution", 768)),
                            label="Preset",
                            info="Quick select resolution",
                        )
                    inference_steps = gr.Slider(
                        minimum=10, maximum=50, step=5, value=saved.get("inference_steps", 20),
                        label="Inference Steps",
                        info="Lower = faster but lower quality",
                    )
                    cpu_offload = gr.Checkbox(
                        value=saved.get("cpu_offload", False), label="CPU Offload",
                        info="Offloads models to CPU for minimal VRAM (~4GB) but slower",
                    )
                    with gr.Row():
                        seed = gr.Number(value=saved.get("seed", 42), label="Seed Value", precision=0, minimum=0)
                        tblr_split = gr.Checkbox(
                            value=saved.get("tblr_split", True), label="Split Left/Right",
                            info="Separates hands, eyes, etc. left and right",
                        )

            with gr.Column(scale=2):
                gallery = gr.Gallery(
                    label="Layer Preview", columns=4,
                    height="auto", object_fit="contain",
                )

                run_btn = gr.Button("🚀 Start Decomposition", variant="primary", size="lg")

                status = gr.Textbox(
                    label="Status", interactive=False, lines=4,
                    elem_id="status-box",
                )

                open_folder_btn = gr.Button("📂 Open Output Folder", size="sm")

                gr.Markdown(
                    "---\n"
                    "**Output Destination**: `workspace/ui_output/` | "
                    "**Estimated Inference Time**: NF4 ~7min, Full ~7min (RTX 3090)",
                    elem_classes=["header-text"],
                )

                timer = gr.Timer(value=0.5, active=False)

        def start_run(image, mode_val, res, seed_val, split, steps, offload):
            save_settings(mode=mode_val, resolution=res, seed=seed_val, tblr_split=split, inference_steps=steps, cpu_offload=offload)
            save_dir, status = start_inference_fn(image, mode_val, res, seed_val, split, steps, offload)
            return save_dir, status, gr.Timer(active=True)

        def on_timer_tick(save_dir):
            layers, save_dir, status, timer_update = poll_inference_fn(save_dir)
            return layers, save_dir, status, timer_update

        resolution_preset.change(
            fn=lambda x: int(x),
            inputs=[resolution_preset],
            outputs=[resolution],
        )

        run_btn.click(
            fn=start_run,
            inputs=[input_image, mode, resolution, seed, tblr_split, inference_steps, cpu_offload],
            outputs=[output_path_state, status, timer],
        )

        timer.tick(
            fn=on_timer_tick,
            inputs=[output_path_state],
            outputs=[gallery, output_path_state, status, timer],
        )

        open_folder_btn.click(
            fn=open_folder_fn,
            inputs=[output_path_state],
        )

    return demo, theme, CUSTOM_CSS
