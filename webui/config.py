"""Configuration constants and paths for See-through UI."""

from pathlib import Path

# Root paths - points to the see-through installation (same level as webui)
SEETHROUGH_ROOT = Path(__file__).resolve().parent.parent / "see-through"
SCRIPT_PATH = SEETHROUGH_ROOT / "inference" / "scripts" / "inference_psd_quantized.py"
HF_CACHE_DIR = SEETHROUGH_ROOT / ".hf_cache"
OUTPUT_BASE = SEETHROUGH_ROOT / "workspace" / "ui_output"

# Layer configuration
SKIP_TAGS = {"src_img", "src_head", "reconstruction"}

LAYER_ORDER = [
    "front hair", "back hair", "head", "neck", "neckwear",
    "topwear", "handwear", "bottomwear", "legwear", "footwear",
    "tail", "wings", "objects",
    "headwear", "face", "irides", "eyebrow", "eyewhite",
    "eyelash", "eyewear", "ears", "earwear", "nose", "mouth",
]

# Stage detection markers for log parsing
STAGE_MARKERS = [
    ("Quantized inference:", "📋 Inference Settings"),
    ("Building LayerDiff", "🔨 Building LayerDiff Pipeline..."),
    ("[NF4 fix]", "🔧 Fixing NF4 Text Encoder..."),
    ("Running LayerDiff", "🎨 Running LayerDiff Inference (body + head)..."),
    ("LayerDiff3D done", "✅ LayerDiff Completed"),
    ("layerdiff pipeline freed", "♻️ Releasing VRAM..."),
    ("Building Marigold", "🔨 Building Marigold Pipeline..."),
    ("Running Marigold", "🏔️ Running Marigold Depth Inference..."),
    ("Marigold done", "✅ Marigold Completed"),
    ("Running PSD assembly", "📦 Assembling PSD..."),
    ("PSD assembly done", "✅ PSD Completed"),
]

# UI Theme configuration
CUSTOM_CSS = """
/* Checkerboard for transparent layer previews */
.gallery-item img,
div[data-testid="image"] img {
    background-image:
        linear-gradient(45deg, #ddd 25%, transparent 25%),
        linear-gradient(-45deg, #ddd 25%, transparent 25%),
        linear-gradient(45deg, transparent 75%, #ddd 75%),
        linear-gradient(-45deg, transparent 75%, #ddd 75%);
    background-size: 16px 16px;
    background-position: 0 0, 0 8px, 8px -8px, -8px 0;
    background-color: #e8e8ed;
}
.header-text { text-align: center; padding: 0.5rem 0; }
#status-box textarea {
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 0.85rem;
    line-height: 1.4;
}
"""