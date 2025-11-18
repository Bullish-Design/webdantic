# src/webdantic/config/models.py
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field, field_validator


class BrowserConfig(BaseModel):
    """Configuration for browser connection."""
    
    host: str = Field(default="localhost", description="CDP host address")
    port: int = Field(default=9222, ge=1024, le=65535, description="CDP port number")
    timeout: int = Field(default=30000, ge=0, description="Default timeout in milliseconds")
    headless: bool = Field(default=False, description="Run browser in headless mode")
    slow_mo: int = Field(default=0, ge=0, description="Slow down operations by milliseconds")
    
    @field_validator("port")
    @classmethod
    def validate_port(cls, v: int) -> int:
        if not (1024 <= v <= 65535):
            raise ValueError("Port must be between 1024 and 65535")
        return v
    
    @property
    def endpoint_url(self) -> str:
        """Get the CDP endpoint URL."""
        return f"http://{self.host}:{self.port}"


class PageConfig(BaseModel):
    """Configuration for page operations."""
    
    default_timeout: int = Field(default=30000, ge=0, description="Default timeout for operations")
    default_navigation_timeout: int = Field(default=30000, ge=0, description="Default navigation timeout")
    viewport_width: Optional[int] = Field(default=1280, ge=1, description="Viewport width")
    viewport_height: Optional[int] = Field(default=720, ge=1, description="Viewport height")
    user_agent: Optional[str] = Field(default=None, description="Custom user agent")


class ScreenshotConfig(BaseModel):
    """Configuration for screenshots."""
    
    full_page: bool = Field(default=False, description="Capture full scrollable page")
    omit_background: bool = Field(default=False, description="Hide default white background")
    quality: Optional[int] = Field(default=None, ge=0, le=100, description="JPEG quality (0-100)")
    type: str = Field(default="png", description="Screenshot type: png or jpeg")
    
    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        if v not in ("png", "jpeg"):
            raise ValueError("type must be 'png' or 'jpeg'")
        return v