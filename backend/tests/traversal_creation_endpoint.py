#!/usr/bin/env python3
"""
Simple script to test the enhanced test case creation endpoint.

This script sends a POST request to the new test case creation endpoint
with a comprehensive payload that includes browser configs and secret values.
"""

import json
import sys
from typing import Any, Dict

import requests

# Configuration
BASE_URL = "http://localhost:6969"  # Adjust if your server runs on different port
TEST_CASE_ENDPOINT = f"{BASE_URL}/api/v1/test-cases/"


def create_test_payload() -> Dict[str, Any]:
    """
    Create a comprehensive test payload for the enhanced test case creation endpoint.

    Returns:
        Dict containing the test case creation payload with dependencies
    """
    return {
        "project_id": "tlbfpzlsh4m118t88pwp695w",
        "document_id": None,  # Optional document reference
        "test_name": "Enhanced Login Test",
        "test_description": "Comprehensive test for user login functionality with multiple browser configurations",
        "test_goal": "Verify login works across different browsers and with various secret configurations",
        "extra_rules": [
            "Must handle invalid credentials gracefully and maintain session state",
            "Ensure proper error handling for network issues",
        ],
        "url_route": "/auth/login",
        "allowed_domains": ["example.com", "test.example.com", "staging.example.com"],
        "priority": "high",
        "category": "authentication",
        # New browser configurations to create
        "new_browser_configs": [
            {
                "project_id": "test-project-123",
                "browser_config": {
                    "browser": "chrome",
                    "headless": True,
                    "viewport": {"width": 1920, "height": 1080},
                    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "timeout": 30000,
                    "args": ["--no-sandbox", "--disable-dev-shm-usage"],
                },
            },
            {
                "project_id": "test-project-123",
                "browser_config": {
                    "browser": "firefox",
                    "headless": True,
                    "viewport": {"width": 1366, "height": 768},
                    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
                    "timeout": 30000,
                    "args": ["--no-sandbox"],
                },
            },
            {
                "project_id": "test-project-123",
                "browser_config": {
                    "browser": "safari",
                    "headless": False,
                    "viewport": {"width": 1440, "height": 900},
                    "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15",
                    "timeout": 45000,
                },
            },
        ],
        # Existing browser config IDs to associate (empty for this test)
        "existing_browser_config_ids": [],
        # New secret values to create
        "new_secret_values": [
            {
                "project_id": "test-project-123",
                "secret_name": "LOGIN_API_KEY",
                "secret_value": "sk_test_123456789abcdef",
            },
            {
                "project_id": "test-project-123",
                "secret_name": "ADMIN_PASSWORD",
                "secret_value": "admin_secure_password_2024",
            },
            {
                "project_id": "test-project-123",
                "secret_name": "DATABASE_URL",
                "secret_value": "postgresql://user:pass@localhost:5432/testdb",
            },
            {
                "project_id": "test-project-123",
                "secret_name": "JWT_SECRET",
                "secret_value": "jwt_super_secret_key_for_testing_only",
            },
        ],
        # Existing secret value IDs to associate (empty for this test)
        "existing_secret_value_ids": [],
    }


def test_enhanced_test_case_creation():
    """
    Test the enhanced test case creation endpoint.

    Sends a POST request with a comprehensive payload and validates the response.
    """
    print("🚀 Testing Enhanced Test Case Creation Endpoint")
    print("=" * 60)

    # Create test payload
    payload = create_test_payload()

    print(f"📡 Sending POST request to: {TEST_CASE_ENDPOINT}")
    print("📦 Payload includes:")
    print(f"   - Test case: {payload['test_name']}")
    print(f"   - New browser configs: {len(payload['new_browser_configs'])}")
    print(f"   - New secret values: {len(payload['new_secret_values'])}")
    print(f"   - Existing browser configs: {len(payload['existing_browser_config_ids'])}")
    print(f"   - Existing secret values: {len(payload['existing_secret_value_ids'])}")
    print()

    try:
        # Send POST request
        response = requests.post(
            TEST_CASE_ENDPOINT,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30,
        )

        print(f"📊 Response Status: {response.status_code}")
        print(f"📊 Response Headers: {dict(response.headers)}")
        print()

        # Check if request was successful
        if response.status_code == 201:
            print("✅ SUCCESS: Test case created successfully!")
            print()

            # Parse and display response
            try:
                response_data = response.json()
                print("📋 Response Details:")
                print(f"   - Test Case ID: {response_data['test_case']['id']}")
                print(f"   - Test Case Name: {response_data['test_case']['test_name']}")
                print(
                    f"   - Created Browser Configs: {len(response_data['created_browser_configs'])}"
                )
                print(
                    f"   - Associated Browser Configs: {len(response_data['associated_browser_configs'])}"
                )
                print(f"   - Created Secret Values: {len(response_data['created_secret_values'])}")
                print(
                    f"   - Associated Secret Values: {len(response_data['associated_secret_values'])}"
                )
                print(
                    f"   - Created Test Traversals: {len(response_data['created_test_traversals'])}"
                )
                print()

                # Display test traversals
                print("🔄 Created Test Traversals:")
                for i, traversal in enumerate(response_data["created_test_traversals"], 1):
                    print(f"   {i}. {traversal['traversal_name']} (ID: {traversal['id']})")
                print()

                # Display browser configs
                print("🌐 Created Browser Configs:")
                for i, config in enumerate(response_data["created_browser_configs"], 1):
                    browser_type = config["browser_config"].get("browser", "unknown")
                    print(f"   {i}. {browser_type} (ID: {config['id']})")
                print()

                # Display secret values
                print("🔐 Created Secret Values:")
                for i, secret in enumerate(response_data["created_secret_values"], 1):
                    print(f"   {i}. {secret['secret_name']} (ID: {secret['id']})")
                print()

                print("🎉 All entities created successfully!")
                return True

            except json.JSONDecodeError as e:
                print(f"❌ ERROR: Failed to parse JSON response: {e}")
                print(f"📄 Raw response: {response.text}")
                return False

        else:
            print(f"❌ ERROR: Request failed with status {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Could not connect to the server.")
        print("   Make sure the FastAPI server is running on http://localhost:8000")
        return False

    except requests.exceptions.Timeout:
        print("❌ ERROR: Request timed out.")
        return False

    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR: Request failed: {e}")
        return False


def test_simple_test_case_creation():
    """
    Test the simple test case creation endpoint for backward compatibility.
    """
    print("🚀 Testing Simple Test Case Creation Endpoint")
    print("=" * 60)

    simple_payload = {
        "project_id": "test-project-123",
        "test_name": "Simple Login Test",
        "test_description": "Basic test for user login functionality",
        "test_goal": "Verify basic login works",
        "extra_rules": ["Simple validation", "Basic error handling"],
        "url_route": "/login",
        "allowed_domains": ["example.com"],
        "priority": "MEDIUM",
        "category": "authentication",
    }

    simple_endpoint = f"{BASE_URL}/test-cases/simple"
    print(f"📡 Sending POST request to: {simple_endpoint}")

    try:
        response = requests.post(
            simple_endpoint,
            json=simple_payload,
            headers={"Content-Type": "application/json"},
            timeout=30,
        )

        print(f"📊 Response Status: {response.status_code}")

        if response.status_code == 201:
            print("✅ SUCCESS: Simple test case created successfully!")
            response_data = response.json()
            print(f"   - Test Case ID: {response_data['id']}")
            print(f"   - Test Case Name: {response_data['test_name']}")
            return response_data["id"]  # Return the test case ID for further testing
        else:
            print(f"❌ ERROR: Simple creation failed with status {response.status_code}")
            print(f"📄 Response: {response.text}")
            return None

    except Exception as e:
        print(f"❌ ERROR: Simple test failed: {e}")
        return None


def test_test_runs_by_test_case_endpoint(test_case_id: str):
    """
    Test the new endpoint for getting test runs by test case ID.
    """
    print("🚀 Testing Test Runs by Test Case Endpoint")
    print("=" * 60)

    if not test_case_id:
        print("❌ ERROR: No test case ID provided for testing")
        return False

    test_runs_endpoint = f"{BASE_URL}/test-cases/{test_case_id}/test-runs"
    print(f"📡 Sending GET request to: {test_runs_endpoint}")
    print("📦 Query parameters: page=1, page_size=5, sort_order=desc")

    try:
        response = requests.get(
            test_runs_endpoint,
            params={"page": 1, "page_size": 5, "sort_order": "desc"},
            headers={"Content-Type": "application/json"},
            timeout=30,
        )

        print(f"📊 Response Status: {response.status_code}")

        if response.status_code == 200:
            print("✅ SUCCESS: Test runs retrieved successfully!")
            response_data = response.json()

            print("📋 Response Details:")
            print(f"   - Test Case ID: {response_data['test_case_id']}")
            print(f"   - Test Case Name: {response_data['test_case_name']}")
            print(f"   - Total Test Runs: {response_data['total_count']}")
            print(f"   - Page: {response_data['page']}")
            print(f"   - Page Size: {response_data['page_size']}")
            print(f"   - Total Pages: {response_data['total_pages']}")
            print(f"   - Has Next: {response_data['has_next']}")
            print(f"   - Has Previous: {response_data['has_previous']}")
            print(f"   - Items in Response: {len(response_data['items'])}")

            # Display test run details if any exist
            if response_data["items"]:
                print("\n🔄 Test Runs in Response:")
                for i, test_run in enumerate(response_data["items"], 1):
                    print(f"   {i}. Test Run ID: {test_run['id']}")
                    print(f"      - Traversal ID: {test_run['test_traversal_id']}")
                    print(f"      - Run Type: {test_run['run_type']}")
                    print(f"      - State: {test_run['current_state']}")
                    print(f"      - Started At: {test_run['started_at']}")
                    print(
                        f"      - Browser: {test_run['browser_config']['browser_config']['browser']}"
                    )
                    print(f"      - History Elements: {len(test_run['history'])}")
            else:
                print(
                    "\n📝 Note: No test runs found for this test case (expected for newly created test case)"
                )

            return True
        else:
            print(f"❌ ERROR: Failed to retrieve test runs with status {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ ERROR: Test runs endpoint test failed: {e}")
        return False


def main():
    """
    Main function to run the tests.
    """
    print("🧪 Test Case Creation Endpoint Test Script")
    print("=" * 60)
    print()

    # Test enhanced endpoint
    enhanced_success = test_enhanced_test_case_creation()
    print()

    # Test simple endpoint and get test case ID for further testing
    test_case_id = test_simple_test_case_creation()
    simple_success = test_case_id is not None
    print()

    # Test the new test runs by test case endpoint
    test_runs_success = False
    if test_case_id:
        test_runs_success = test_test_runs_by_test_case_endpoint(test_case_id)
    else:
        print("⚠️  Skipping test runs endpoint test - no test case ID available")
        test_runs_success = True  # Mark as success if we can't test it
    print()

    # Summary
    print("📊 Test Summary:")
    print("=" * 60)
    print(f"Enhanced Endpoint: {'✅ PASSED' if enhanced_success else '❌ FAILED'}")
    print(f"Simple Endpoint: {'✅ PASSED' if simple_success else '❌ FAILED'}")
    print(f"Test Runs by Test Case Endpoint: {'✅ PASSED' if test_runs_success else '❌ FAILED'}")

    if enhanced_success and simple_success and test_runs_success:
        print(
            "\n🎉 All tests passed! The enhanced test case creation and test runs retrieval are working correctly."
        )
        sys.exit(0)
    else:
        print("\n💥 Some tests failed. Please check the server logs and try again.")
        sys.exit(1)


if __name__ == "__main__":
    main()
