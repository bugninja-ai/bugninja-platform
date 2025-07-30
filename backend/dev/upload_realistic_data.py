"""
Realistic Data Upload Script

This script creates comprehensive realistic test data based on actual web services.
It creates a complete hierarchy of entities with proper relationships:
- 1 Project (IMDB & Amazon Testing)
- 1 Document
- 2 Test Cases (IMDB movie search, Amazon product purchase)
- 3 Browser Configs (Chrome, Firefox, Safari)
- 6 Secret Values (credentials, API keys)
- 6 Test Traversals (2×3 cross product)
- 30-36 Brain States (5-6 per traversal)
- 90-108 Actions (3 per brain state)
- 6 Test Runs (one per traversal)
- 6 Cost records
- 90-108 History Elements (one per action in test runs)
- TestCase-BrowserConfig associations
- SecretValue-TestCase associations
"""

import os
import shutil
from typing import Any, Dict, List

from rich import print as rich_print

from app.db.action import Action
from app.db.base import QuinoContextManager
from app.db.brain_state import BrainState
from app.db.browser_config import BrowserConfig
from app.db.history_element import HistoryElementState
from app.db.secret_value import SecretValue
from app.db.secret_value_test_case import SecretValueTestCase
from app.db.test_case import TestCase, TestCasePriority
from app.db.test_case_browser_config import TestCaseBrowserConfig
from app.db.test_run import RunOrigin, RunState, RunType, TestRun
from app.db.test_traversal import TestTraversal
from app.repo import (
    ActionRepo,
    BrainStateRepo,
    BrowserConfigRepo,
    CostRepo,
    DocumentRepo,
    HistoryElementRepo,
    ProjectRepo,
    SecretValueRepo,
    TestCaseRepo,
    TestRunRepo,
    TestTraversalRepo,
)
from app.schemas.crud.action import CreateAction
from app.schemas.crud.brain_state import CreateBrainState
from app.schemas.crud.browser_config import CreateBrowserConfig
from app.schemas.crud.cost import CreateCost
from app.schemas.crud.document import CreateDocument
from app.schemas.crud.history_element import CreateHistoryElement
from app.schemas.crud.project import CreateProject
from app.schemas.crud.secret_value import CreateSecretValue
from app.schemas.crud.test_case import CreateTestCase
from app.schemas.crud.test_run import CreateTestRun
from app.schemas.crud.test_traversal import CreateTestTraversal


def setup_content_folders() -> None:
    """
    Create the content folder structure for storing images and GIFs.

    Creates:
    - content/
    - content/run_gifs/
    - content/run_he_screenshots/
    """
    content_dir = "content"
    run_gifs_dir = os.path.join(content_dir, "run_gifs")
    run_he_screenshots_dir = os.path.join(content_dir, "run_he_screenshots")

    # Create content directory if it doesn't exist
    if not os.path.exists(content_dir):
        os.makedirs(content_dir)
        rich_print(f"✓ Created directory: {content_dir}")

    # Create run_gifs directory if it doesn't exist
    if not os.path.exists(run_gifs_dir):
        os.makedirs(run_gifs_dir)
        rich_print(f"✓ Created directory: {run_gifs_dir}")

    # Create run_he_screenshots directory if it doesn't exist
    if not os.path.exists(run_he_screenshots_dir):
        os.makedirs(run_he_screenshots_dir)
        rich_print(f"✓ Created directory: {run_he_screenshots_dir}")


def copy_images_for_history_elements(history_element_ids: List[str]) -> Dict[str, str]:
    """
    Copy polar_bear.png for each history element with the correct naming convention.

    Args:
        history_element_ids: List of history element IDs

    Returns:
        Dict mapping history element ID to its image path
    """
    source_image = "dev/polar_bear.png"
    image_mapping = {}

    if not os.path.exists(source_image):
        rich_print(f"⚠️ Warning: Source image {source_image} not found")
        return image_mapping

    for history_element_id in history_element_ids:
        # Create filename with .jpg extension as requested
        filename = f"{history_element_id}.jpg"
        destination_path = os.path.join("content", "run_he_screenshots", filename)

        try:
            shutil.copy2(source_image, destination_path)
            image_mapping[history_element_id] = f"content/run_he_screenshots/{filename}"
            rich_print(f"✓ Copied image for history element {history_element_id}")
        except Exception as e:
            rich_print(f"❌ Error copying image for history element {history_element_id}: {e}")

    return image_mapping


def copy_images_for_test_runs(test_run_ids: List[str]) -> Dict[str, str]:
    """
    Copy baby_polar_bear.gif for each test run with the correct naming convention.

    Args:
        test_run_ids: List of test run IDs

    Returns:
        Dict mapping test run ID to its GIF path
    """
    source_gif = "dev/baby_polar_bear.gif"
    gif_mapping = {}

    if not os.path.exists(source_gif):
        rich_print(f"⚠️ Warning: Source GIF {source_gif} not found")
        return gif_mapping

    for test_run_id in test_run_ids:
        # Create filename with .gif extension as requested
        filename = f"{test_run_id}.gif"
        destination_path = os.path.join("content", "run_gifs", filename)

        try:
            shutil.copy2(source_gif, destination_path)
            gif_mapping[test_run_id] = f"content/run_gifs/{filename}"
            rich_print(f"✓ Copied GIF for test run {test_run_id}")
        except Exception as e:
            rich_print(f"❌ Error copying GIF for test run {test_run_id}: {e}")

    return gif_mapping


def generate_unique_ids(count: int) -> List[str]:
    """
    Generate unique IDs for history elements and test runs.

    Args:
        count: Number of IDs to generate

    Returns:
        List of unique IDs
    """
    from cuid2 import Cuid as CUID

    return [CUID().generate() for _ in range(count)]


def create_realistic_browser_configs() -> List[Dict[str, Any]]:
    """Create realistic browser configurations matching the sample JSON format."""
    return [
        {
            "name": "Chrome Desktop",
            "browser_config": {
                "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "viewport": {"width": 1280, "height": 960},
                "device_scale_factor": None,
                "color_scheme": "light",
                "accept_downloads": True,
                "proxy": True,
                "client_certificates": [],
                "extra_http_headers": {},
                "http_credentials": None,
                "java_script_enabled": True,
                "geolocation": "US",
                "timeout": 30000.0,
                "headers": {
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept-Encoding": "gzip, deflate, br",
                    "DNT": "1",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1",
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "none",
                    "Sec-Fetch-User": "?1",
                    "Cache-Control": "max-age=0",
                },
                "allowed_domains": ["imdb.com", "www.imdb.com"],
            },
        },
        {
            "name": "Firefox Desktop",
            "browser_config": {
                "user_agent": "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
                "viewport": {"width": 1280, "height": 960},
                "device_scale_factor": None,
                "color_scheme": "dark",
                "accept_downloads": False,
                "proxy": True,
                "client_certificates": [],
                "extra_http_headers": {},
                "http_credentials": None,
                "java_script_enabled": True,
                "geolocation": "US",
                "timeout": 45000.0,
                "headers": {
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Accept-Encoding": "gzip, deflate",
                    "DNT": "1",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1",
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "none",
                    "Sec-Fetch-User": "?1",
                    "Cache-Control": "max-age=0",
                },
                "allowed_domains": ["amazon.com", "www.amazon.com"],
            },
        },
        {
            "name": "Safari Desktop",
            "browser_config": {
                "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
                "viewport": {"width": 1280, "height": 960},
                "device_scale_factor": None,
                "color_scheme": "light",
                "accept_downloads": True,
                "proxy": True,
                "client_certificates": [],
                "extra_http_headers": {},
                "http_credentials": None,
                "java_script_enabled": False,
                "geolocation": "US",
                "timeout": 60000.0,
                "headers": {
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": "en-us",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1",
                },
                "allowed_domains": [
                    "netflix.com",
                    "www.netflix.com",
                    "github.com",
                    "www.github.com",
                ],
            },
        },
    ]


def create_realistic_secrets() -> List[Dict[str, str]]:
    """Create realistic secret values matching the sample JSON format."""
    return [
        {"secret_name": "IMDB_API_KEY", "secret_value": "k_1234567890abcdef"},
        {"secret_name": "AMAZON_EMAIL", "secret_value": "testuser@example.com"},
        {"secret_name": "AMAZON_PASSWORD", "secret_value": "SecurePassword123!"},
        {"secret_name": "PAYMENT_CARD_NUMBER", "secret_value": "4111111111111111"},
        {"secret_name": "NETFLIX_CREDENTIALS", "secret_value": "netflix_user:streaming_pass_2024"},
        {"secret_name": "GITHUB_TOKEN", "secret_value": "ghp_9876543210abcdefghijklmnopqrstuvwxyz"},
    ]


def create_imdb_brain_states() -> List[Dict[str, str]]:
    """Create realistic brain states for IMDB movie search scenario."""
    return [
        {
            "evaluation_previous_goal": "Unknown - Starting fresh browser session. No previous actions to evaluate.",
            "memory": "New session initiated. Objective: Search for movie information on IMDB. Progress: 0/4 milestones. Steps: 1) Access IMDB homepage, 2) Perform movie search, 3) Examine movie details, 4) Verify ratings and reviews.",
            "next_goal": "Launch browser and navigate to https://www.imdb.com to begin movie search process.",
        },
        {
            "evaluation_previous_goal": "Achieved - Successfully loaded IMDB homepage. Navigation bar and search functionality are accessible.",
            "memory": "IMDB homepage loaded successfully. Search interface is ready. Progress: 1/4 milestones. Steps: 1) Access IMDB homepage ✓, 2) Perform movie search, 3) Examine movie details, 4) Verify ratings and reviews.",
            "next_goal": "Locate search field and enter 'The Dark Knight' to find the specific movie.",
        },
        {
            "evaluation_previous_goal": "Completed - Search query executed. Results page displays multiple movie options including the target film.",
            "memory": "Search results obtained successfully. Multiple entries found for 'The Dark Knight'. Progress: 2/4 milestones. Steps: 1) Access IMDB homepage ✓, 2) Perform movie search ✓, 3) Examine movie details, 4) Verify ratings and reviews.",
            "next_goal": "Select 'The Dark Knight (2008)' from search results to access detailed movie information.",
        },
        {
            "evaluation_previous_goal": "Successful - Movie details page loaded. Complete information including cast, director, and plot summary is visible.",
            "memory": "Movie details page accessed successfully. All relevant information is displayed. Progress: 3/4 milestones. Steps: 1) Access IMDB homepage ✓, 2) Perform movie search ✓, 3) Examine movie details ✓, 4) Verify ratings and reviews.",
            "next_goal": "Scroll through page content to locate and review user ratings and audience feedback.",
        },
        {
            "evaluation_previous_goal": "Accomplished - Successfully reviewed ratings and plot information. Movie details match expectations and ratings are satisfactory.",
            "memory": "All objectives completed successfully. Movie information verified and ratings confirmed. Progress: 4/4 milestones. Steps: 1) Access IMDB homepage ✓, 2) Perform movie search ✓, 3) Examine movie details ✓, 4) Verify ratings and reviews ✓.",
            "next_goal": "Mission accomplished. Movie search and verification process completed successfully.",
        },
    ]


def create_amazon_brain_states() -> List[Dict[str, str]]:
    """Create realistic brain states for Amazon product purchase scenario."""
    return [
        {
            "evaluation_previous_goal": "None - Fresh browser session started. No previous actions to assess.",
            "memory": "New shopping session initiated. Goal: Complete product purchase on Amazon. Progress: 0/5 objectives. Steps: 1) Navigate to Amazon, 2) Search for desired product, 3) Add item to cart, 4) Proceed to checkout, 5) Complete purchase transaction.",
            "next_goal": "Open browser and navigate to https://www.amazon.com to begin shopping process.",
        },
        {
            "evaluation_previous_goal": "Successful - Amazon homepage loaded correctly. Site navigation and search features are functional.",
            "memory": "Amazon homepage accessed successfully. Ready to begin product search. Progress: 1/5 objectives. Steps: 1) Navigate to Amazon ✓, 2) Search for desired product, 3) Add item to cart, 4) Proceed to checkout, 5) Complete purchase transaction.",
            "next_goal": "Use search bar to find 'wireless headphones' and execute search query.",
        },
        {
            "evaluation_previous_goal": "Completed - Search results displayed successfully. Multiple headphone options are available for selection.",
            "memory": "Product search completed. Various wireless headphone models found. Progress: 2/5 objectives. Steps: 1) Navigate to Amazon ✓, 2) Search for desired product ✓, 3) Add item to cart, 4) Proceed to checkout, 5) Complete purchase transaction.",
            "next_goal": "Click on first product listing to view detailed specifications and pricing information.",
        },
        {
            "evaluation_previous_goal": "Achieved - Product page loaded successfully. Product details, pricing, and purchase options are clearly visible.",
            "memory": "Product details page accessed. Ready to add item to shopping cart. Progress: 3/5 objectives. Steps: 1) Navigate to Amazon ✓, 2) Search for desired product ✓, 3) Add item to cart, 4) Proceed to checkout, 5) Complete purchase transaction.",
            "next_goal": "Click 'Add to Cart' button to include selected headphones in shopping cart.",
        },
        {
            "evaluation_previous_goal": "Successful - Product added to cart successfully. Confirmation message indicates successful cart addition.",
            "memory": "Item successfully added to shopping cart. Ready to proceed with checkout process. Progress: 4/5 objectives. Steps: 1) Navigate to Amazon ✓, 2) Search for desired product ✓, 3) Add item to cart ✓, 4) Proceed to checkout, 5) Complete purchase transaction.",
            "next_goal": "Click 'Proceed to Checkout' to begin payment and shipping process.",
        },
        {
            "evaluation_previous_goal": "Completed - Checkout page loaded. Login form and payment options are displayed for user authentication.",
            "memory": "Checkout process initiated. Login required to complete purchase. Progress: 4/5 objectives. Steps: 1) Navigate to Amazon ✓, 2) Search for desired product ✓, 3) Add item to cart ✓, 4) Proceed to checkout ✓, 5) Complete purchase transaction.",
            "next_goal": "Enter account credentials and proceed with payment to finalize purchase.",
        },
    ]


def create_netflix_brain_states() -> List[Dict[str, str]]:
    """Create realistic brain states for Netflix content search scenario."""
    return [
        {
            "evaluation_previous_goal": "None - New browser session initiated. No previous actions to evaluate.",
            "memory": "Fresh Netflix session started. Objective: Search for and watch content on Netflix. Progress: 0/4 tasks. Steps: 1) Access Netflix homepage, 2) Search for specific show, 3) View show details, 4) Begin playback.",
            "next_goal": "Navigate to https://www.netflix.com to access streaming platform.",
        },
        {
            "evaluation_previous_goal": "Successful - Netflix homepage loaded. Login interface and content categories are visible.",
            "memory": "Netflix homepage accessed successfully. Ready to search for content. Progress: 1/4 tasks. Steps: 1) Access Netflix homepage ✓, 2) Search for specific show, 3) View show details, 4) Begin playback.",
            "next_goal": "Use search function to find 'Stranger Things' series.",
        },
        {
            "evaluation_previous_goal": "Completed - Search results displayed. Multiple seasons and episodes of Stranger Things are available.",
            "memory": "Content search successful. Stranger Things series found with multiple seasons. Progress: 2/4 tasks. Steps: 1) Access Netflix homepage ✓, 2) Search for specific show ✓, 3) View show details, 4) Begin playback.",
            "next_goal": "Click on Stranger Things to view series details and episode list.",
        },
        {
            "evaluation_previous_goal": "Achieved - Series details page loaded. Episode information and cast details are displayed.",
            "memory": "Series details accessed successfully. Ready to begin watching. Progress: 3/4 tasks. Steps: 1) Access Netflix homepage ✓, 2) Search for specific show ✓, 3) View show details ✓, 4) Begin playback.",
            "next_goal": "Click play button to start watching the first episode.",
        },
        {
            "evaluation_previous_goal": "Accomplished - Video player loaded successfully. Content is ready for playback.",
            "memory": "All objectives completed. Netflix content is ready for viewing. Progress: 4/4 tasks. Steps: 1) Access Netflix homepage ✓, 2) Search for specific show ✓, 3) View show details ✓, 4) Begin playback ✓.",
            "next_goal": "Content playback initiated successfully. Mission completed.",
        },
    ]


def create_github_brain_states() -> List[Dict[str, str]]:
    """Create realistic brain states for GitHub repository search scenario."""
    return [
        {
            "evaluation_previous_goal": "None - New session started. No previous actions to assess.",
            "memory": "Fresh GitHub session initiated. Goal: Search for and explore repositories. Progress: 0/4 objectives. Steps: 1) Access GitHub homepage, 2) Search for repositories, 3) View repository details, 4) Examine code and documentation.",
            "next_goal": "Navigate to https://github.com to access code hosting platform.",
        },
        {
            "evaluation_previous_goal": "Successful - GitHub homepage loaded. Search bar and trending repositories are visible.",
            "memory": "GitHub homepage accessed successfully. Ready to search for repositories. Progress: 1/4 objectives. Steps: 1) Access GitHub homepage ✓, 2) Search for repositories, 3) View repository details, 4) Examine code and documentation.",
            "next_goal": "Use search function to find 'machine learning' repositories.",
        },
        {
            "evaluation_previous_goal": "Completed - Search results displayed. Multiple machine learning repositories are listed.",
            "memory": "Repository search successful. Various ML projects found. Progress: 2/4 objectives. Steps: 1) Access GitHub homepage ✓, 2) Search for repositories ✓, 3) View repository details, 4) Examine code and documentation.",
            "next_goal": "Click on first repository to view detailed information and code structure.",
        },
        {
            "evaluation_previous_goal": "Achieved - Repository page loaded. README, code files, and project statistics are visible.",
            "memory": "Repository details accessed successfully. Ready to examine code. Progress: 3/4 objectives. Steps: 1) Access GitHub homepage ✓, 2) Search for repositories ✓, 3) View repository details ✓, 4) Examine code and documentation.",
            "next_goal": "Browse through repository files and documentation to understand project structure.",
        },
        {
            "evaluation_previous_goal": "Accomplished - Successfully examined repository contents. Project structure and documentation reviewed.",
            "memory": "All objectives completed. Repository exploration finished successfully. Progress: 4/4 objectives. Steps: 1) Access GitHub homepage ✓, 2) Search for repositories ✓, 3) View repository details ✓, 4) Examine code and documentation ✓.",
            "next_goal": "Repository exploration completed. Mission accomplished.",
        },
    ]


def create_varied_cost_data() -> List[Dict[str, Any]]:
    """Create varied cost data for different test runs."""
    return [
        {
            "model_type": "gpt-4",
            "cost_per_token": 0.00003,
            "input_token_num": 2500,
            "completion_token_num": 800,
            "cost_in_dollars": 0.099,
        },
        {
            "model_type": "gpt-3.5-turbo",
            "cost_per_token": 0.000002,
            "input_token_num": 1800,
            "completion_token_num": 600,
            "cost_in_dollars": 0.0048,
        },
        {
            "model_type": "claude-3",
            "cost_per_token": 0.000015,
            "input_token_num": 3200,
            "completion_token_num": 1200,
            "cost_in_dollars": 0.066,
        },
        {
            "model_type": "gpt-4",
            "cost_per_token": 0.00003,
            "input_token_num": 1500,
            "completion_token_num": 400,
            "cost_in_dollars": 0.057,
        },
        {
            "model_type": "gpt-3.5-turbo",
            "cost_per_token": 0.000002,
            "input_token_num": 2200,
            "completion_token_num": 900,
            "cost_in_dollars": 0.0062,
        },
        {
            "model_type": "claude-3",
            "cost_per_token": 0.000015,
            "input_token_num": 2800,
            "completion_token_num": 1000,
            "cost_in_dollars": 0.057,
        },
    ]


def create_varied_run_data() -> List[Dict[str, Any]]:
    """Create varied test run data."""
    return [
        {
            "run_type": RunType.AGENTIC,
            "origin": RunOrigin.USER,
            "repair_was_needed": False,
            "current_state": RunState.FINISHED,
        },
        {
            "run_type": RunType.REPLAY,
            "origin": RunOrigin.CICD,
            "repair_was_needed": True,
            "current_state": RunState.FAILED,
        },
        {
            "run_type": RunType.REPLAY_WITH_HEALING,
            "origin": RunOrigin.USER,
            "repair_was_needed": True,
            "current_state": RunState.FINISHED,
        },
        {
            "run_type": RunType.AGENTIC,
            "origin": RunOrigin.CICD,
            "repair_was_needed": False,
            "current_state": RunState.PENDING,
        },
        {
            "run_type": RunType.REPLAY,
            "origin": RunOrigin.USER,
            "repair_was_needed": False,
            "current_state": RunState.FAILED,
        },
        {
            "run_type": RunType.REPLAY_WITH_HEALING,
            "origin": RunOrigin.CICD,
            "repair_was_needed": True,
            "current_state": RunState.PENDING,
        },
    ]


def create_realistic_actions(brain_states: List[Dict], scenario: str) -> List[Dict[str, Any]]:
    """Create realistic actions based on brain states and scenario with complete DOM element data."""
    actions: List[Dict[str, Any]] = []

    if scenario == "imdb":
        # IMDB scenario actions with complete DOM data
        action_data = [
            {
                "action_type": "go_to_url",
                "action_data": {"url": "https://www.imdb.com"},
                "dom_element": None,
            },
            {
                "action_type": "input_text",
                "action_data": {"index": 1, "text": "<secret>IMDB_API_KEY</secret>", "xpath": None},
                "dom_element": {
                    "tag_name": "input",
                    "xpath": "html/body/div[1]/div/div[1]/div/div[2]/div[2]/form/div[1]/input",
                    "attributes": {
                        "type": "text",
                        "class": "flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",
                        "id": "suggestion-search",
                        "placeholder": "Search IMDb",
                        "required": "",
                        "value": "",
                    },
                    "is_visible": True,
                    "is_interactive": True,
                    "is_top_element": True,
                    "is_in_viewport": True,
                    "shadow_root": False,
                    "highlight_index": 1,
                    "viewport_coordinates": None,
                    "page_coordinates": None,
                    "children": [],
                    "alternative_relative_xpaths": [
                        "//input[@id='suggestion-search']",
                        "//form/div[1]/input",
                        "//form[contains(@class, 'space-y-4')]/div[1]/input",
                        "//div[contains(@class, 'rounded-lg')]/div[2]/form/div[1]/input",
                        "//body/div[1]/div/div[1]/div/div[2]/div[2]/form/div[1]/input",
                    ],
                },
            },
            {
                "action_type": "click_element_by_index",
                "action_data": {"index": 2, "xpath": None},
                "dom_element": {
                    "tag_name": "button",
                    "xpath": "html/body/div[1]/div/div[1]/div/div[2]/div[2]/form/button",
                    "attributes": {
                        "class": "inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground shadow hover:bg-primary/90 dark:text-white h-9 px-4 py-2 w-full",
                        "type": "submit",
                        "data-umami-event": "search_button_click",
                    },
                    "is_visible": True,
                    "is_interactive": True,
                    "is_top_element": True,
                    "is_in_viewport": True,
                    "shadow_root": False,
                    "highlight_index": 2,
                    "viewport_coordinates": None,
                    "page_coordinates": None,
                    "children": [{"text": "Search", "type": "TEXT_NODE"}],
                    "alternative_relative_xpaths": [
                        "//button[text()='Search']",
                        "//button[contains(@class, 'bg-primary')]",
                        "//form/button",
                        "//body/div[1]/div/div[1]/div/div[2]/div[2]/form/button",
                    ],
                },
            },
            {
                "action_type": "click_element_by_index",
                "action_data": {"index": 3, "xpath": None},
                "dom_element": {
                    "tag_name": "a",
                    "xpath": "html/body/div[1]/div/div[2]/main/div/div/div[2]/div/div[1]/a",
                    "attributes": {
                        "class": "ipc-title-link-wrapper",
                        "href": "/title/tt0468569/",
                        "data-testid": "title-link",
                    },
                    "is_visible": True,
                    "is_interactive": True,
                    "is_top_element": True,
                    "is_in_viewport": True,
                    "shadow_root": False,
                    "highlight_index": 3,
                    "viewport_coordinates": None,
                    "page_coordinates": None,
                    "children": [{"text": "The Dark Knight (2008)", "type": "TEXT_NODE"}],
                    "alternative_relative_xpaths": [
                        "//a[contains(@href, '/title/tt0468569/')]",
                        "//a[text()='The Dark Knight (2008)']",
                        "//body/div[1]/div/div[2]/main/div/div/div[2]/div/div[1]/a",
                    ],
                },
            },
            {
                "action_type": "done",
                "action_data": {
                    "text": "Successfully found and viewed The Dark Knight movie details with ratings and plot information",
                    "success": True,
                },
                "dom_element": None,
            },
        ]
    elif scenario == "amazon":
        # Amazon scenario actions with complete DOM data
        action_data = [
            {
                "action_type": "go_to_url",
                "action_data": {"url": "https://www.amazon.com"},
                "dom_element": None,
            },
            {
                "action_type": "input_text",
                "action_data": {"index": 1, "text": "<secret>AMAZON_EMAIL</secret>", "xpath": None},
                "dom_element": {
                    "tag_name": "input",
                    "xpath": "html/body/div[1]/div/div[1]/div/div[2]/div[2]/form/div[1]/input",
                    "attributes": {
                        "type": "text",
                        "class": "flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",
                        "id": "twotabsearchtextbox",
                        "placeholder": "Search Amazon",
                        "required": "",
                        "value": "",
                    },
                    "is_visible": True,
                    "is_interactive": True,
                    "is_top_element": True,
                    "is_in_viewport": True,
                    "shadow_root": False,
                    "highlight_index": 1,
                    "viewport_coordinates": None,
                    "page_coordinates": None,
                    "children": [],
                    "alternative_relative_xpaths": [
                        "//input[@id='twotabsearchtextbox']",
                        "//form/div[1]/input",
                        "//body/div[1]/div/div[1]/div/div[2]/div[2]/form/div[1]/input",
                    ],
                },
            },
            {
                "action_type": "click_element_by_index",
                "action_data": {"index": 2, "xpath": None},
                "dom_element": {
                    "tag_name": "input",
                    "xpath": "html/body/div[1]/div/div[1]/div/div[2]/div[2]/form/div[2]/input",
                    "attributes": {
                        "class": "nav-input",
                        "type": "submit",
                        "id": "nav-search-submit-button",
                        "value": "Go",
                    },
                    "is_visible": True,
                    "is_interactive": True,
                    "is_top_element": True,
                    "is_in_viewport": True,
                    "shadow_root": False,
                    "highlight_index": 2,
                    "viewport_coordinates": None,
                    "page_coordinates": None,
                    "children": [],
                    "alternative_relative_xpaths": [
                        "//input[@id='nav-search-submit-button']",
                        "//form/div[2]/input",
                        "//body/div[1]/div/div[1]/div/div[2]/div[2]/form/div[2]/input",
                    ],
                },
            },
            {
                "action_type": "click_element_by_index",
                "action_data": {"index": 3, "xpath": None},
                "dom_element": {
                    "tag_name": "a",
                    "xpath": "html/body/div[1]/div/div[2]/main/div/div/div[2]/div/div[1]/a",
                    "attributes": {
                        "class": "a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal",
                        "href": "/dp/B08N5WRWNW",
                        "data-testid": "product-link",
                    },
                    "is_visible": True,
                    "is_interactive": True,
                    "is_top_element": True,
                    "is_in_viewport": True,
                    "shadow_root": False,
                    "highlight_index": 3,
                    "viewport_coordinates": None,
                    "page_coordinates": None,
                    "children": [
                        {"text": "Sony WH-1000XM4 Wireless Headphones", "type": "TEXT_NODE"}
                    ],
                    "alternative_relative_xpaths": [
                        "//a[contains(@class, 'a-link-normal')]",
                        "//a[contains(@href, '/dp/')]",
                        "//body/div[1]/div/div[2]/main/div/div/div[2]/div/div[1]/a",
                    ],
                },
            },
            {
                "action_type": "click_element_by_index",
                "action_data": {"index": 4, "xpath": None},
                "dom_element": {
                    "tag_name": "input",
                    "xpath": "html/body/div[1]/div/div[2]/main/div/div/div[2]/div/form/div[1]/input",
                    "attributes": {
                        "class": "a-button-input",
                        "type": "submit",
                        "id": "add-to-cart-button",
                        "value": "Add to Cart",
                    },
                    "is_visible": True,
                    "is_interactive": True,
                    "is_top_element": True,
                    "is_in_viewport": True,
                    "shadow_root": False,
                    "highlight_index": 4,
                    "viewport_coordinates": None,
                    "page_coordinates": None,
                    "children": [],
                    "alternative_relative_xpaths": [
                        "//input[@id='add-to-cart-button']",
                        "//form/div[1]/input",
                        "//body/div[1]/div/div[2]/main/div/div/div[2]/div/form/div[1]/input",
                    ],
                },
            },
            {
                "action_type": "click_element_by_index",
                "action_data": {"index": 5, "xpath": None},
                "dom_element": {
                    "tag_name": "input",
                    "xpath": "html/body/div[1]/div/div[2]/main/div/div/div[2]/div/form/div[2]/input",
                    "attributes": {
                        "class": "a-button-input",
                        "type": "submit",
                        "name": "proceedToRetailCheckout",
                        "value": "Proceed to Checkout",
                    },
                    "is_visible": True,
                    "is_interactive": True,
                    "is_top_element": True,
                    "is_in_viewport": True,
                    "shadow_root": False,
                    "highlight_index": 5,
                    "viewport_coordinates": None,
                    "page_coordinates": None,
                    "children": [],
                    "alternative_relative_xpaths": [
                        "//input[@name='proceedToRetailCheckout']",
                        "//form/div[2]/input",
                        "//body/div[1]/div/div[2]/main/div/div/div[2]/div/form/div[2]/input",
                    ],
                },
            },
        ]
    elif scenario == "netflix":
        # Netflix scenario actions with complete DOM data
        action_data = [
            {
                "action_type": "go_to_url",
                "action_data": {"url": "https://www.netflix.com"},
                "dom_element": None,
            },
            {
                "action_type": "input_text",
                "action_data": {
                    "index": 1,
                    "text": "<secret>NETFLIX_CREDENTIALS</secret>",
                    "xpath": None,
                },
                "dom_element": {
                    "tag_name": "input",
                    "xpath": "html/body/div[1]/div/div[1]/div/div[2]/div[2]/form/div[1]/input",
                    "attributes": {
                        "type": "text",
                        "class": "search-input",
                        "data-uia": "search-box-input",
                        "placeholder": "Search for titles, genres",
                        "value": "",
                    },
                    "is_visible": True,
                    "is_interactive": True,
                    "is_top_element": True,
                    "is_in_viewport": True,
                    "shadow_root": False,
                    "highlight_index": 1,
                    "viewport_coordinates": None,
                    "page_coordinates": None,
                    "children": [],
                    "alternative_relative_xpaths": [
                        "//input[@data-uia='search-box-input']",
                        "//form/div[1]/input",
                        "//body/div[1]/div/div[1]/div/div[2]/div[2]/form/div[1]/input",
                    ],
                },
            },
            {
                "action_type": "click_element_by_index",
                "action_data": {"index": 2, "xpath": None},
                "dom_element": {
                    "tag_name": "a",
                    "xpath": "html/body/div[1]/div/div[2]/main/div/div/div[2]/div/div[1]/a",
                    "attributes": {
                        "class": "title-link",
                        "href": "/title/80057281",
                        "data-uia": "title-link",
                    },
                    "is_visible": True,
                    "is_interactive": True,
                    "is_top_element": True,
                    "is_in_viewport": True,
                    "shadow_root": False,
                    "highlight_index": 2,
                    "viewport_coordinates": None,
                    "page_coordinates": None,
                    "children": [{"text": "Stranger Things", "type": "TEXT_NODE"}],
                    "alternative_relative_xpaths": [
                        "//a[contains(@href, '/title/80057281')]",
                        "//a[text()='Stranger Things']",
                        "//body/div[1]/div/div[2]/main/div/div/div[2]/div/div[1]/a",
                    ],
                },
            },
            {
                "action_type": "click_element_by_index",
                "action_data": {"index": 3, "xpath": None},
                "dom_element": {
                    "tag_name": "button",
                    "xpath": "html/body/div[1]/div/div[2]/main/div/div/div[2]/div/div[1]/button",
                    "attributes": {
                        "class": "play-button",
                        "data-uia": "play-button",
                        "type": "button",
                    },
                    "is_visible": True,
                    "is_interactive": True,
                    "is_top_element": True,
                    "is_in_viewport": True,
                    "shadow_root": False,
                    "highlight_index": 3,
                    "viewport_coordinates": None,
                    "page_coordinates": None,
                    "children": [{"text": "Play", "type": "TEXT_NODE"}],
                    "alternative_relative_xpaths": [
                        "//button[@data-uia='play-button']",
                        "//button[text()='Play']",
                        "//body/div[1]/div/div[2]/main/div/div/div[2]/div/div[1]/button",
                    ],
                },
            },
            {
                "action_type": "done",
                "action_data": {
                    "text": "Successfully started Stranger Things playback on Netflix",
                    "success": True,
                },
                "dom_element": None,
            },
        ]
    else:  # github
        # GitHub scenario actions with complete DOM data
        action_data = [
            {
                "action_type": "go_to_url",
                "action_data": {"url": "https://github.com"},
                "dom_element": None,
            },
            {
                "action_type": "input_text",
                "action_data": {"index": 1, "text": "<secret>GITHUB_TOKEN</secret>", "xpath": None},
                "dom_element": {
                    "tag_name": "input",
                    "xpath": "html/body/div[1]/div/div[1]/div/div[2]/div[2]/form/div[1]/input",
                    "attributes": {
                        "type": "search",
                        "class": "search-input",
                        "name": "q",
                        "placeholder": "Search or jump to...",
                        "value": "",
                    },
                    "is_visible": True,
                    "is_interactive": True,
                    "is_top_element": True,
                    "is_in_viewport": True,
                    "shadow_root": False,
                    "highlight_index": 1,
                    "viewport_coordinates": None,
                    "page_coordinates": None,
                    "children": [],
                    "alternative_relative_xpaths": [
                        "//input[@name='q']",
                        "//form/div[1]/input",
                        "//body/div[1]/div/div[1]/div/div[2]/div[2]/form/div[1]/input",
                    ],
                },
            },
            {
                "action_type": "click_element_by_index",
                "action_data": {"index": 2, "xpath": None},
                "dom_element": {
                    "tag_name": "a",
                    "xpath": "html/body/div[1]/div/div[2]/main/div/div/div[2]/div/div[1]/a",
                    "attributes": {
                        "class": "repo-link",
                        "href": "/tensorflow/tensorflow",
                        "data-testid": "repo-link",
                    },
                    "is_visible": True,
                    "is_interactive": True,
                    "is_top_element": True,
                    "is_in_viewport": True,
                    "shadow_root": False,
                    "highlight_index": 2,
                    "viewport_coordinates": None,
                    "page_coordinates": None,
                    "children": [{"text": "tensorflow/tensorflow", "type": "TEXT_NODE"}],
                    "alternative_relative_xpaths": [
                        "//a[contains(@href, '/tensorflow/tensorflow')]",
                        "//a[text()='tensorflow/tensorflow']",
                        "//body/div[1]/div/div[2]/main/div/div/div[2]/div/div[1]/a",
                    ],
                },
            },
            {
                "action_type": "click_element_by_index",
                "action_data": {"index": 3, "xpath": None},
                "dom_element": {
                    "tag_name": "a",
                    "xpath": "html/body/div[1]/div/div[2]/main/div/div/div[2]/div/div[1]/a",
                    "attributes": {
                        "class": "file-link",
                        "href": "/blob/main/README.md",
                        "data-testid": "file-link",
                    },
                    "is_visible": True,
                    "is_interactive": True,
                    "is_top_element": True,
                    "is_in_viewport": True,
                    "shadow_root": False,
                    "highlight_index": 3,
                    "viewport_coordinates": None,
                    "page_coordinates": None,
                    "children": [{"text": "README.md", "type": "TEXT_NODE"}],
                    "alternative_relative_xpaths": [
                        "//a[contains(@href, '/blob/main/README.md')]",
                        "//a[text()='README.md']",
                        "//body/div[1]/div/div[2]/main/div/div/div[2]/div/div[1]/a",
                    ],
                },
            },
            {
                "action_type": "done",
                "action_data": {
                    "text": "Successfully explored TensorFlow repository on GitHub",
                    "success": True,
                },
                "dom_element": None,
            },
        ]

    # Create actions for each brain state
    for i, brain_state in enumerate(brain_states):
        if i < len(action_data):
            action = {
                "brain_state_id": f"brain_state_{i}",
                "action_type": action_data[i]["action_type"],
                "action_data": action_data[i]["action_data"],
                "dom_element": action_data[i]["dom_element"],
            }
            actions.append(action)

    return actions


def upload_realistic_data() -> None:
    """
    Upload comprehensive realistic data to the database.

    Creates a complete test dataset with all required relationships
    and proper foreign key constraints based on real web services.

    Raises:
        RuntimeError: If there are existing projects in the database
    """
    with QuinoContextManager() as db:
        try:
            rich_print("Starting realistic data upload...")

            # Check if there are existing projects
            existing_projects = ProjectRepo.get_all(db)
            if not existing_projects:
                rich_print("✓ Database is empty, proceeding with realistic data upload...")

                # Phase 1: Core entities
                rich_print("Creating core entities...")

                # Create Project
                project_data = CreateProject(
                    name="Web Service Testing Platform", default_start_url="https://www.google.com"
                )
                project = ProjectRepo.create(db, project_data)
                rich_print(f"✓ Created project: {project.name}")
                db.commit()

                # Create Document
                document_data = CreateDocument(
                    project_id=project.id,
                    name="Test Documentation",
                    content="Comprehensive test documentation for web service testing including IMDB and Amazon scenarios.",
                )
                document = DocumentRepo.create(db, document_data)
                rich_print(f"✓ Created document: {document.name}")
                db.commit()

                # Phase 2: Test Cases
                rich_print("Creating test cases...")

                # Create 4 Test Cases
                test_cases: List[TestCase] = []

                # IMDB Test Case
                imdb_test_case = TestCaseRepo.create(
                    db,
                    CreateTestCase(
                        project_id=project.id,
                        document_id=document.id,
                        test_name="IMDB Movie Search and Details",
                        test_description="Search for a specific movie on IMDB, view its details, and verify ratings and plot information.",
                        test_goal="Successfully navigate to IMDB, search for 'The Dark Knight', view movie details, and verify information.",
                        extra_rules=[
                            "Must verify the correct movie is found and check user ratings.",
                            "Ensure movie details are accurate and up-to-date.",
                        ],
                        url_route="https://www.imdb.com",
                        allowed_domains=["imdb.com", "www.imdb.com"],
                        priority=TestCasePriority.HIGH,
                        category="entertainment",
                    ),
                )
                test_cases.append(imdb_test_case)
                rich_print(f"✓ Created test case 1: {imdb_test_case.test_name}")

                # Amazon Test Case
                amazon_test_case = TestCaseRepo.create(
                    db,
                    CreateTestCase(
                        project_id=project.id,
                        document_id=None,
                        test_name="Amazon Product Purchase Flow",
                        test_description="Search for a product on Amazon, add it to cart, and proceed to checkout.",
                        test_goal="Successfully navigate to Amazon, search for wireless headphones, add to cart, and reach checkout.",
                        extra_rules=[
                            "Must verify product details before adding to cart.",
                            "Check product availability and pricing.",
                        ],
                        url_route="https://www.amazon.com",
                        allowed_domains=["amazon.com", "www.amazon.com"],
                        priority=TestCasePriority.MEDIUM,
                        category="ecommerce",
                    ),
                )
                test_cases.append(amazon_test_case)
                rich_print(f"✓ Created test case 2: {amazon_test_case.test_name}")

                # Netflix Test Case
                netflix_test_case = TestCaseRepo.create(
                    db,
                    CreateTestCase(
                        project_id=project.id,
                        document_id=document.id,
                        test_name="Netflix Content Search and Playback",
                        test_description="Search for a specific show on Netflix and initiate playback.",
                        test_goal="Successfully navigate to Netflix, search for 'Stranger Things', and start watching.",
                        extra_rules=[
                            "Must verify the correct show is found and playback begins.",
                            "Ensure streaming quality is acceptable.",
                        ],
                        url_route="https://www.netflix.com",
                        allowed_domains=["netflix.com", "www.netflix.com"],
                        priority=TestCasePriority.LOW,
                        category="streaming",
                    ),
                )
                test_cases.append(netflix_test_case)
                rich_print(f"✓ Created test case 3: {netflix_test_case.test_name}")

                # GitHub Test Case
                github_test_case = TestCaseRepo.create(
                    db,
                    CreateTestCase(
                        project_id=project.id,
                        document_id=None,
                        test_name="GitHub Repository Exploration",
                        test_description="Search for repositories on GitHub and examine their contents.",
                        test_goal="Successfully navigate to GitHub, search for machine learning repositories, and explore code.",
                        extra_rules=[
                            "Must verify repository details and examine documentation.",
                            "Check code quality and documentation completeness.",
                        ],
                        url_route="https://github.com",
                        allowed_domains=["github.com", "www.github.com"],
                        priority=TestCasePriority.CRITICAL,
                        category="development",
                    ),
                )
                test_cases.append(github_test_case)
                rich_print(f"✓ Created test case 4: {github_test_case.test_name}")

                db.commit()

                # Create 3 Browser Configs
                browser_configs: List[BrowserConfig] = []
                browser_config_data = create_realistic_browser_configs()
                for i, config in enumerate(browser_config_data):
                    # Assign browser configs to specific test cases
                    # Chrome for IMDB, Firefox for Amazon, Safari for Netflix/GitHub
                    if i == 0:  # Chrome
                        test_case_id = imdb_test_case.id
                    elif i == 1:  # Firefox
                        test_case_id = amazon_test_case.id
                    else:  # Safari
                        test_case_id = netflix_test_case.id

                    browser_config = BrowserConfigRepo.create(
                        db,
                        CreateBrowserConfig(
                            test_case_id=test_case_id, browser_config=config["browser_config"]
                        ),
                    )
                    browser_configs.append(browser_config)
                    rich_print(f"✓ Created browser config {i+1}: {config['name']}")
                db.commit()

                # Create 6 Secret Values
                secret_values: List[SecretValue] = []
                secret_data = create_realistic_secrets()
                for i, secret in enumerate(secret_data):
                    # Assign secrets to specific test cases based on the secret type
                    if "IMDB" in secret["secret_name"]:
                        test_case_id = imdb_test_case.id
                    elif "AMAZON" in secret["secret_name"]:
                        test_case_id = amazon_test_case.id
                    elif "NETFLIX" in secret["secret_name"]:
                        test_case_id = netflix_test_case.id
                    elif "GITHUB" in secret["secret_name"]:
                        test_case_id = github_test_case.id
                    else:
                        # Default to first test case if no match
                        test_case_id = test_cases[0].id

                    secret_value = SecretValueRepo.create(
                        db,
                        CreateSecretValue(
                            test_case_id=test_case_id,
                            secret_name=secret["secret_name"],
                            secret_value=secret["secret_value"],
                        ),
                    )
                    secret_values.append(secret_value)
                    rich_print(f"✓ Created secret value {i+1}: {secret_value.secret_name}")

                db.commit()
                rich_print("✓ Committed Phase 2 entities")

                # Create TestCase-BrowserConfig associations
                rich_print("Creating test case - browser config associations...")
                for test_case in test_cases:
                    for browser_config in browser_configs:
                        association = TestCaseBrowserConfig(
                            test_case_id=test_case.id, browser_config_id=browser_config.id
                        )
                        db.add(association)
                        rich_print(f"✓ Linked test case '{test_case.test_name}' to browser config")

                db.commit()
                rich_print("✓ Committed Phase 2 entities")

                # Phase 3: Test Traversals
                rich_print("Creating test traversals...")

                # Create 12 Test Traversals (4×3 cross product)
                traversals: List[TestTraversal] = []
                for i, test_case in enumerate(test_cases):
                    for j, browser_config in enumerate(browser_configs):
                        traversal = TestTraversalRepo.create(
                            db,
                            CreateTestTraversal(
                                test_case_id=test_case.id,
                                browser_config_id=browser_config.id,
                                traversal_name=f"{test_case.test_name} - {browser_config_data[j]['name']}",
                            ),
                        )
                        traversals.append(traversal)
                        rich_print(
                            f"✓ Created traversal {len(traversals)}: {traversal.traversal_name}"
                        )

                db.commit()

                # Link secret values to test cases
                rich_print("Linking secret values to test cases...")
                for test_case in test_cases:
                    # Link relevant secrets based on test case
                    if "IMDB" in test_case.test_name:
                        # Link IMDB API key
                        link = SecretValueTestCase(
                            secret_value_id=secret_values[0].id, test_case_id=test_case.id
                        )
                        db.add(link)
                        rich_print(f"✓ Linked IMDB API key to test case: {test_case.test_name}")
                    elif "Amazon" in test_case.test_name:
                        # Link Amazon credentials
                        for secret in secret_values[1:4]:  # Amazon email, password, payment info
                            link = SecretValueTestCase(
                                secret_value_id=secret.id, test_case_id=test_case.id
                            )
                            db.add(link)
                        rich_print(
                            f"✓ Linked Amazon credentials to test case: {test_case.test_name}"
                        )
                    elif "Netflix" in test_case.test_name:
                        # Link Netflix credentials
                        link = SecretValueTestCase(
                            secret_value_id=secret_values[4].id, test_case_id=test_case.id
                        )
                        db.add(link)
                        rich_print(
                            f"✓ Linked Netflix credentials to test case: {test_case.test_name}"
                        )
                    else:  # GitHub
                        # Link GitHub token
                        link = SecretValueTestCase(
                            secret_value_id=secret_values[5].id, test_case_id=test_case.id
                        )
                        db.add(link)
                        rich_print(f"✓ Linked GitHub token to test case: {test_case.test_name}")

                db.commit()
                rich_print("✓ Committed Phase 3 entities")

                # Phase 4: Brain states and actions
                rich_print("Creating brain states and actions...")

                brain_states: List[BrainState] = []
                actions: List[Action] = []

                for traversal_idx, traversal in enumerate(traversals):
                    # Determine scenario based on test case
                    if "IMDB" in traversal.traversal_name:
                        scenario = "imdb"
                    elif "Amazon" in traversal.traversal_name:
                        scenario = "amazon"
                    elif "Netflix" in traversal.traversal_name:
                        scenario = "netflix"
                    else:  # GitHub
                        scenario = "github"

                    # Get brain states for this scenario
                    if scenario == "imdb":
                        brain_state_data = create_imdb_brain_states()
                    elif scenario == "amazon":
                        brain_state_data = create_amazon_brain_states()
                    elif scenario == "netflix":
                        brain_state_data = create_netflix_brain_states()
                    else:  # github
                        brain_state_data = create_github_brain_states()

                    # Create brain states for this traversal
                    for brain_state_idx, brain_state_info in enumerate(brain_state_data):
                        brain_state = BrainStateRepo.create(
                            db,
                            CreateBrainState(
                                test_traversal_id=traversal.id,
                                idx_in_run=brain_state_idx,
                                valid=True,
                                evaluation_previous_goal=brain_state_info[
                                    "evaluation_previous_goal"
                                ],
                                memory=brain_state_info["memory"],
                                next_goal=brain_state_info["next_goal"],
                            ),
                        )
                        brain_states.append(brain_state)

                        # Create actions for this brain state
                        action_data = create_realistic_actions(brain_state_data, scenario)
                        if brain_state_idx < len(action_data):
                            action_info = action_data[brain_state_idx]

                            # Create action data structure matching the sample JSON format
                            action_dict = {
                                "done": None,
                                "search_google": None,
                                "go_to_url": None,
                                "go_back": None,
                                "wait": None,
                                "click_element_by_index": None,
                                "input_text": None,
                                "save_pdf": None,
                                "switch_tab": None,
                                "open_tab": None,
                                "close_tab": None,
                                "extract_content": None,
                                "get_ax_tree": None,
                                "scroll_down": None,
                                "scroll_up": None,
                                "send_keys": None,
                                "scroll_to_text": None,
                                "get_dropdown_options": None,
                                "select_dropdown_option": None,
                                "drag_drop": None,
                                "third_party_authentication_wait": None,
                            }

                            # Set the appropriate action type with complete data structure
                            if action_info["action_type"] == "go_to_url":
                                action_dict["go_to_url"] = action_info["action_data"]
                            elif action_info["action_type"] == "input_text":
                                action_dict["input_text"] = action_info["action_data"]
                            elif action_info["action_type"] == "click_element_by_index":
                                action_dict["click_element_by_index"] = action_info["action_data"]
                            elif action_info["action_type"] == "done":
                                action_dict["done"] = action_info["action_data"]

                            # Create action with complete DOM element data
                            action = ActionRepo.create(
                                db,
                                CreateAction(
                                    brain_state_id=brain_state.id,
                                    idx_in_brain_state=brain_state_idx,
                                    action=action_dict,
                                    dom_element_data=action_info["dom_element"] or {},
                                    valid=True,
                                ),
                            )
                            actions.append(action)

                    rich_print(
                        f"✓ Created {len(brain_state_data)} brain states and actions for traversal {traversal_idx + 1}"
                    )

                rich_print(
                    f"✓ Created {len(brain_states)} brain states and {len(actions)} actions total"
                )

                db.commit()
                rich_print("✓ Committed Phase 4 entities")

                # Phase 5: Test execution
                rich_print("Creating test execution data...")

                # Generate IDs for test runs and history elements first
                rich_print("Generating unique IDs for test runs and history elements...")

                # Calculate total number of history elements
                total_history_elements = 0
                for traversal in traversals:
                    # Count brain states for this traversal
                    traversal_brain_states = [
                        bs for bs in brain_states if bs.test_traversal_id == traversal.id
                    ]
                    # Each brain state has one action
                    total_history_elements += len(traversal_brain_states)

                # Generate IDs
                test_run_ids = generate_unique_ids(len(traversals))
                history_element_ids = generate_unique_ids(total_history_elements)

                rich_print(
                    f"✓ Generated {len(test_run_ids)} test run IDs and {len(history_element_ids)} history element IDs"
                )

                # Copy images for test runs and history elements
                rich_print("Copying images for test runs and history elements...")
                test_run_gif_mapping = copy_images_for_test_runs(test_run_ids)
                history_element_image_mapping = copy_images_for_history_elements(
                    history_element_ids
                )

                rich_print(
                    f"✓ Copied {len(test_run_gif_mapping)} test run GIFs and {len(history_element_image_mapping)} history element images"
                )

                # Create Test Run for each traversal with varied data
                test_runs: List[TestRun] = []
                varied_run_data = create_varied_run_data()
                for i, traversal in enumerate(traversals):
                    run_data = varied_run_data[i % len(varied_run_data)]
                    test_run_id = test_run_ids[i]
                    gif_path = test_run_gif_mapping.get(
                        test_run_id, f"content/run_gifs/{test_run_id}.gif"
                    )

                    test_run = TestRunRepo.create(
                        db,
                        CreateTestRun(
                            test_traversal_id=traversal.id,
                            browser_config_id=traversal.browser_config_id,
                            run_type=run_data["run_type"],
                            origin=run_data["origin"],
                            repair_was_needed=run_data["repair_was_needed"],
                            current_state=run_data["current_state"],
                            run_gif=gif_path,
                        ),
                    )
                    test_runs.append(test_run)
                    rich_print(
                        f"✓ Created test run: {test_run.id} ({run_data['run_type']}, {run_data['origin']})"
                    )

                db.commit()

                # Create Cost records for each test run with varied data
                varied_cost_data = create_varied_cost_data()
                for i, test_run in enumerate(test_runs):
                    cost_data = varied_cost_data[i % len(varied_cost_data)]
                    cost = CostRepo.create(
                        db,
                        CreateCost(
                            test_run_id=test_run.id,
                            project_id=project.id,
                            model_type=cost_data["model_type"],
                            cost_per_token=cost_data["cost_per_token"],
                            input_token_num=cost_data["input_token_num"],
                            completion_token_num=cost_data["completion_token_num"],
                            cost_in_dollars=cost_data["cost_in_dollars"],
                        ),
                    )
                    rich_print(
                        f"✓ Created cost record: ${cost.cost_in_dollars:.3f} ({cost_data['model_type']})"
                    )

                db.commit()

                # Create History Elements for actions in test runs with varied states
                history_count = 0
                history_element_id_index = 0
                history_states = [
                    HistoryElementState.PASSED,
                    HistoryElementState.FAILED,
                    HistoryElementState.PASSED,
                    HistoryElementState.PASSED,
                    HistoryElementState.FAILED,
                    HistoryElementState.PASSED,
                ]

                for test_run_idx, test_run in enumerate(test_runs):
                    # Get actions for this test run's traversal
                    traversal_actions = [
                        a
                        for a in actions
                        if a.brain_state_id
                        in [
                            bs.id
                            for bs in brain_states
                            if bs.test_traversal_id == test_run.test_traversal_id
                        ]
                    ]

                    for i, action in enumerate(traversal_actions):
                        # Vary the history element state
                        state = history_states[(test_run_idx + i) % len(history_states)]

                        # Get the history element ID and corresponding image path
                        history_element_id = history_element_ids[history_element_id_index]
                        screenshot_path = history_element_image_mapping.get(
                            history_element_id,
                            f"content/run_he_screenshots/{history_element_id}.jpg",
                        )

                        HistoryElementRepo.create(
                            db,
                            CreateHistoryElement(
                                test_run_id=test_run.id,
                                action_id=action.id,
                                history_element_state=state,
                                screenshot=screenshot_path,
                            ),
                        )
                        history_count += 1
                        history_element_id_index += 1

                rich_print(f"✓ Created {history_count} history elements with varied states")

                # Final commit
                db.commit()

                rich_print("\n🎉 Realistic data upload completed successfully!")
                rich_print("📊 Summary:")
                rich_print(f"   • 1 Project: {project.name}")
                rich_print(f"   • 1 Document: {document.name}")
                rich_print("   • 4 Test Cases (IMDB, Amazon, Netflix, GitHub)")
                rich_print("   • 3 Browser Configs (Chrome, Firefox, Safari)")
                rich_print("   • 6 Secret Values (API keys, credentials)")
                rich_print("   • 12 Test Traversals")
                rich_print(f"   • {len(brain_states)} Brain States")
                rich_print(f"   • {len(actions)} Actions")
                rich_print("   • 12 Test Runs")
                rich_print("   • 12 Cost Records")
                rich_print(f"   • {history_count} History Elements")
                rich_print("   • 12 TestCase-BrowserConfig associations")
                rich_print("   • SecretValue-TestCase associations")

            else:
                rich_print(
                    "❌ Error: Database already contains projects. Please clear the database first."
                )
                rich_print(f"   Found {len(existing_projects)} existing project(s):")
                for project in existing_projects:
                    rich_print(f"   • {project.name} (ID: {project.id})")

        except Exception as e:
            rich_print(f"❌ Error during realistic data upload: {e}")
            db.rollback()
            raise


if __name__ == "__main__":
    upload_realistic_data()
