"""
Constants for CRUD schemas to eliminate code duplication.
"""

from typing import Any, Dict, List

# Action types used across all action schemas
ACTION_TYPES = [
    "done",
    "search_google",
    "go_to_url",
    "go_back",
    "wait",
    "click_element_by_index",
    "input_text",
    "save_pdf",
    "switch_tab",
    "open_tab",
    "close_tab",
    "extract_content",
    "get_ax_tree",
    "scroll_down",
    "scroll_up",
    "send_keys",
    "scroll_to_text",
    "get_dropdown_options",
    "select_dropdown_option",
    "drag_drop",
    "third_party_authentication_wait",
]

# Common action data templates
ACTION_DATA_TEMPLATES: List[Dict[str, Dict[str, Any]]] = [
    {"go_to_url": {"url": "https://{domain}"}},
    {"click_element_by_index": {"index": "{index}", "xpath": None}},
    {"input_text": {"index": "{index}", "text": "{text}", "xpath": None}},
    {"done": {"text": "{text}", "success": "{success}"}},
    {"scroll_down": {}},
    {"wait": {"duration": "{duration}"}},
    {"extract_content": {"selector": "{selector}"}},
    {"get_ax_tree": {}},
]

# DOM element tag names
DOM_TAG_NAMES = ["input", "button", "a", "div", "span", "form", "p", "h1", "h2", "section"]

# DOM element types for different contexts
DOM_ELEMENT_TYPES = {
    "input": ["text", "email", "password", "submit", "button"],
    "button": ["submit", "button"],
    "form": ["submit", "button", "text", "email"],
}


# Browser configuration templates
BROWSER_CONFIG_TEMPLATES = {
    "default": {
        "browser_channel": "{browser_channel}",
        "user_agent": "{user_agent}",
        "viewport": {"width": 1920, "height": 1080},
        "device_scale_factor": 1.0,
        "color_scheme": "{color_scheme}",
        "accept_downloads": True,
        "proxy": None,
        "client_certificates": [],
        "extra_http_headers": {},
        "http_credentials": None,
        "java_script_enabled": True,
        "geolocation": None,
        "timeout": 30000.0,
        "headers": None,
        "allowed_domains": "{allowed_domains}",
    },
    "alternative": {
        "browser_channel": "{browser_channel}",
        "user_agent": "{user_agent}",
        "viewport": {"width": 1366, "height": 768},
        "device_scale_factor": 1.25,
        "color_scheme": "{color_scheme}",
        "accept_downloads": False,
        "proxy": None,
        "client_certificates": [],
        "extra_http_headers": {"Accept-Language": "en-US,en;q=0.9"},
        "http_credentials": None,
        "java_script_enabled": False,
        "geolocation": {"latitude": 40.7128, "longitude": -74.0060},
        "timeout": 60000.0,
        "headers": {"User-Agent": "{user_agent}"},
        "allowed_domains": "{allowed_domains}",
    },
    "response": {
        "browser_channel": "{browser_channel}",
        "user_agent": "{user_agent}",
        "viewport": {"width": 1440, "height": 900},
        "device_scale_factor": 1.0,
        "color_scheme": "light",
        "accept_downloads": True,
        "proxy": None,
        "client_certificates": [],
        "extra_http_headers": {},
        "http_credentials": None,
        "java_script_enabled": True,
        "geolocation": None,
        "timeout": 45000.0,
        "headers": None,
        "allowed_domains": ["example.com", "test.org", "demo.net"],
    },
}

# Browser types based on Playwright configuration
BROWSER_CHANNELS = [
    "Chromium",
    "Firefox",
    "Webkit",
    "Mobile Chrome",
    "Mobile Safari",
    "Google Chrome",
    "Microsoft Edge",
]

# Color scheme options
COLOR_SCHEMES = ["light", "dark"]

USER_AGENTS = [
    # Desktop - Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    # Desktop - macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
    # Desktop - Linux
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
    # Tablets - iPad
    "Mozilla/5.0 (iPad; CPU OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/120.0.6099.119 Mobile/15E148 Safari/604.1",
    # Tablets - Android
    "Mozilla/5.0 (Linux; Android 13; SM-T870) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; Pixel Tablet) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    # Mobile - iPhone
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/120.0.6099.119 Mobile/15E148 Safari/604.1",
    # Mobile - Android
    "Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
]

# Viewport sizes
VIEWPORT_SIZES = [
    # Desktop - Common laptop/desktop resolutions
    {"width": 1920, "height": 1080},  # Full HD
    {"width": 1366, "height": 768},  # Common laptop
    {"width": 1440, "height": 900},  # MacBook Air 13"
    {"width": 1536, "height": 864},  # Surface Laptop
    {"width": 1600, "height": 900},  # Wide laptop
    {"width": 2560, "height": 1440},  # QHD/2K
    {"width": 3840, "height": 2160},  # 4K
    # Tablets
    {"width": 1024, "height": 768},  # iPad landscape
    {"width": 768, "height": 1024},  # iPad portrait
    {"width": 1194, "height": 834},  # iPad Pro 11" landscape
    {"width": 834, "height": 1194},  # iPad Pro 11" portrait
    {"width": 1024, "height": 1366},  # iPad Pro 12.9" portrait
    {"width": 800, "height": 1280},  # Android tablet portrait
    {"width": 1280, "height": 800},  # Android tablet landscape
    # Mobile phones
    {"width": 375, "height": 667},  # iPhone SE
    {"width": 375, "height": 812},  # iPhone 12/13 mini
    {"width": 390, "height": 844},  # iPhone 12/13/14
    {"width": 414, "height": 896},  # iPhone 11/XR
    {"width": 428, "height": 926},  # iPhone 12/13/14 Pro Max
    {"width": 360, "height": 640},  # Android small
    {"width": 412, "height": 892},  # Pixel 6
    {"width": 384, "height": 854},  # Samsung Galaxy S21
]
