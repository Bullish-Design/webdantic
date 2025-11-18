# tests/unit/test_config.py
import pytest
from pydantic import ValidationError
from webdantic.config import BrowserConfig, PageConfig, ScreenshotConfig


class TestBrowserConfig:
    def test_default_values(self):
        config = BrowserConfig()
        assert config.host == "localhost"
        assert config.port == 9222
        assert config.timeout == 30000
        assert config.headless is False
    
    def test_custom_values(self):
        config = BrowserConfig(port=9223, headless=True)
        assert config.port == 9223
        assert config.headless is True
    
    def test_invalid_port_low(self):
        with pytest.raises(ValidationError):
            BrowserConfig(port=1023)
    
    def test_invalid_port_high(self):
        with pytest.raises(ValidationError):
            BrowserConfig(port=65536)
    
    def test_endpoint_url(self):
        config = BrowserConfig(host="127.0.0.1", port=9222)
        assert config.endpoint_url == "http://127.0.0.1:9222"


class TestPageConfig:
    def test_default_values(self):
        config = PageConfig()
        assert config.default_timeout == 30000
        assert config.viewport_width == 1280
        assert config.viewport_height == 720
    
    def test_custom_values(self):
        config = PageConfig(viewport_width=1920, viewport_height=1080)
        assert config.viewport_width == 1920
        assert config.viewport_height == 1080


class TestScreenshotConfig:
    def test_default_values(self):
        config = ScreenshotConfig()
        assert config.full_page is False
        assert config.type == "png"
    
    def test_invalid_type(self):
        with pytest.raises(ValidationError):
            ScreenshotConfig(type="gif")
    
    def test_quality_validation(self):
        config = ScreenshotConfig(type="jpeg", quality=85)
        assert config.quality == 85
        
        with pytest.raises(ValidationError):
            ScreenshotConfig(quality=101)