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

# Browser configuration field names
BROWSER_CONFIG_FIELDS = [
    "user_agent",
    "viewport",
    "device_scale_factor",
    "color_scheme",
    "accept_downloads",
    "proxy",
    "client_certificates",
    "extra_http_headers",
    "http_credentials",
    "java_script_enabled",
    "geolocation",
    "timeout",
    "headers",
    "allowed_domains",
]

# Browser configuration templates
BROWSER_CONFIG_TEMPLATES = {
    "default": {
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
BROWSER_TYPES = [
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

# Viewport sizes
VIEWPORT_SIZES = [
    {"width": 1920, "height": 1080},
    {"width": 1366, "height": 768},
    {"width": 1440, "height": 900},
]
