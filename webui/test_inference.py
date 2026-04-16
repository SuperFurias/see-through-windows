"""Tests for See-through UI input validation."""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from webui.inference import validate_input
import gradio as gr


class TestValidateInput:
    def test_none_image_path(self):
        with pytest.raises(gr.Error, match="Please upload an image"):
            validate_input(None, "NF4", 768, 42, 20)

    def test_nonexistent_image(self, tmp_path):
        fake_path = tmp_path / "nonexistent.png"
        with pytest.raises(gr.Error, match="Image file not found"):
            validate_input(str(fake_path), "NF4", 768, 42, 20)

    def test_invalid_mode(self, tmp_path):
        img_path = tmp_path / "test.png"
        img_path.touch()
        with patch("PIL.Image.open") as mock_open:
            mock_img = MagicMock()
            mock_img.format = "PNG"
            mock_img.size = (512, 512)
            mock_img.__enter__ = MagicMock(return_value=mock_img)
            mock_img.__exit__ = MagicMock(return_value=False)
            mock_open.return_value = mock_img
            
            with pytest.raises(gr.Error, match="Invalid inference mode"):
                validate_input(str(img_path), "Invalid", 768, 42, 20)

    def test_negative_seed(self, tmp_path):
        img_path = tmp_path / "test.png"
        img_path.touch()
        with patch("PIL.Image.open") as mock_open:
            mock_img = MagicMock()
            mock_img.format = "PNG"
            mock_img.size = (512, 512)
            mock_img.__enter__ = MagicMock(return_value=mock_img)
            mock_img.__exit__ = MagicMock(return_value=False)
            mock_open.return_value = mock_img
            
            with pytest.raises(gr.Error, match="Invalid seed value"):
                validate_input(str(img_path), "NF4", 768, -1, 20)

    def test_resolution_out_of_range(self, tmp_path):
        img_path = tmp_path / "test.png"
        img_path.touch()
        with patch("PIL.Image.open") as mock_open:
            mock_img = MagicMock()
            mock_img.format = "PNG"
            mock_img.size = (512, 512)
            mock_img.__enter__ = MagicMock(return_value=mock_img)
            mock_img.__exit__ = MagicMock(return_value=False)
            mock_open.return_value = mock_img
            
            with pytest.raises(gr.Error, match="Invalid resolution"):
                validate_input(str(img_path), "NF4", 100, 42, 20)

    def test_inference_steps_out_of_range(self, tmp_path):
        img_path = tmp_path / "test.png"
        img_path.touch()
        with patch("PIL.Image.open") as mock_open:
            mock_img = MagicMock()
            mock_img.format = "PNG"
            mock_img.size = (512, 512)
            mock_img.__enter__ = MagicMock(return_value=mock_img)
            mock_img.__exit__ = MagicMock(return_value=False)
            mock_open.return_value = mock_img
            
            with pytest.raises(gr.Error, match="Invalid inference steps"):
                validate_input(str(img_path), "NF4", 768, 42, 100)

    def test_valid_input(self, tmp_path):
        img_path = tmp_path / "test.png"
        img_path.touch()
        with patch("PIL.Image.open") as mock_open:
            mock_img = MagicMock()
            mock_img.format = "PNG"
            mock_img.size = (512, 512)
            mock_img.__enter__ = MagicMock(return_value=mock_img)
            mock_img.__exit__ = MagicMock(return_value=False)
            mock_open.return_value = mock_img
            
            seed, resolution, steps = validate_input(str(img_path), "NF4", 768, 42, 20)
            assert seed == 42
            assert resolution == 768
            assert steps == 20

    def test_resolution_rounding(self, tmp_path):
        img_path = tmp_path / "test.png"
        img_path.touch()
        with patch("PIL.Image.open") as mock_open:
            mock_img = MagicMock()
            mock_img.format = "PNG"
            mock_img.size = (512, 512)
            mock_img.__enter__ = MagicMock(return_value=mock_img)
            mock_img.__exit__ = MagicMock(return_value=False)
            mock_open.return_value = mock_img
            
            _, resolution, _ = validate_input(str(img_path), "NF4", 700, 42, 20)
            assert resolution == 704


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
