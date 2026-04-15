"""UI Components and theme configuration for See-through."""

import gradio as gr

from .config import CUSTOM_CSS


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


def build_ui(run_inference_fn, open_folder_fn):
    """Build and return the Gradio UI Blocks and configuration."""
    theme = create_theme()

    with gr.Blocks(title="See-through UI", theme=theme, css=CUSTOM_CSS) as demo:
        # State: output folder path
        output_path_state = gr.State(value="")

        gr.Markdown(
            "# 🔍 See-through — Anime Illustration Layer Decomposition\n"
            "Performs semantic decomposition of one anime illustration into up to 23 layers.\n"
            "[GitHub](https://github.com/shitagaki-lab/see-through) | "
            "[Paper](https://arxiv.org/abs/2602.03749) | "
            "SIGGRAPH 2026",
            elem_classes=["header-text"],
        )

        with gr.Row():
            # --- Left: Settings ---
            with gr.Column(scale=1, min_width=320):
                input_image = gr.Image(type="filepath", label="Input Image", height=350)

                with gr.Group():
                    mode = gr.Radio(
                        choices=[
                            "NF4 Quantized (Recommended・VRAM ~7GB)",
                            "Full bf16 (High Quality・VRAM ~10GB)",
                        ],
                        value="NF4 Quantized (Recommended・VRAM ~7GB)",
                        label="Inference Mode",
                    )
                    with gr.Row():
                        resolution = gr.Slider(
                            minimum=512, maximum=2048, step=64, value=768,
                            label="Resolution",
                            info="512: ~4GB / 768: ~5GB / 1024: ~7GB / 1280: ~9GB (NF4)",
                        )
                        resolution_preset = gr.Dropdown(
                            choices=["512", "768", "1024", "1280"],
                            value="768",
                            label="Preset",
                            info="Quick select resolution",
                        )
                    inference_steps = gr.Slider(
                        minimum=10, maximum=50, step=5, value=20,
                        label="Inference Steps",
                        info="Lower = faster but lower quality",
                    )
                    cpu_offload = gr.Checkbox(
                        value=False, label="CPU Offload",
                        info="Offloads models to CPU for minimal VRAM (~4GB) but slower",
                    )
                    with gr.Row():
                        seed = gr.Number(value=42, label="Seed Value", precision=0, minimum=0)
                        tblr_split = gr.Checkbox(
                            value=True, label="Split Left/Right",
                            info="Separates hands, eyes, etc. left and right",
                        )

            # --- Right: Gallery + Actions ---
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

            # --- Events ---
            resolution_preset.change(
                fn=lambda x: int(x),
                inputs=[resolution_preset],
                outputs=[resolution],
            )

            run_btn.click(
                fn=run_inference_fn,
                inputs=[input_image, mode, resolution, seed, tblr_split, inference_steps, cpu_offload],
                outputs=[gallery, output_path_state, status],
            )

            open_folder_btn.click(
                fn=open_folder_fn,
                inputs=[output_path_state],
            )

    return demo, theme, CUSTOM_CSS