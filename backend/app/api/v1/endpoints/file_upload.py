import io
import json
import re
from typing import Any, Dict, List, Optional

import docx2txt
import pandas as pd
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from openai import AzureOpenAI
from pydantic import BaseModel
from sqlmodel import Session

from app.api.v1.endpoints.utils import COMMON_ERROR_RESPONSES, create_success_response
from app.config import settings
from app.db.base import get_db


class ParsedTestCaseData(BaseModel):
    """Parsed test case data from OpenAI."""

    test_name: str
    test_description: str
    test_goal: str
    extra_rules: List[str]
    url_route: str
    allowed_domains: List[str]
    priority: str  # 'low' | 'medium' | 'high' | 'critical'
    category: Optional[str] = None
    viewport: Optional[Dict[str, int]] = {"width": 1920, "height": 1080}

    @classmethod
    def sample_factory_build(cls) -> "ParsedTestCaseData":
        """Create a sample instance for documentation."""
        return cls(
            test_name="Sample Login Test",
            test_description="Test user login functionality with valid credentials",
            test_goal="Verify that users can successfully log in with correct credentials",
            extra_rules=["Use valid email format", "Password must be at least 8 characters"],
            url_route="https://example.com/login",
            allowed_domains=["example.com", "auth.example.com"],
            priority="high",
            category="authentication",
            viewport={"width": 1920, "height": 1080},
        )


class BrowserConfigData(BaseModel):
    """Browser configuration data generated from file upload."""

    channel: str
    user_agent: str
    viewport: Dict[str, int]
    device_scale_factor: float
    color_scheme: str
    accept_downloads: bool
    proxy: Optional[str] = None
    client_certificates: List[str]
    extra_http_headers: Dict[str, str]
    http_credentials: Optional[str] = None
    java_script_enabled: bool
    geolocation: Optional[Dict[str, float]] = None
    timeout: float
    headers: Optional[Dict[str, str]] = None
    allowed_domains: List[str]

    @classmethod
    def sample_factory_build(cls) -> "BrowserConfigData":
        """Generate a sample BrowserConfigData for testing."""
        return cls(
            channel="chrome",
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=1.0,
            color_scheme="light",
            accept_downloads=True,
            client_certificates=[],
            extra_http_headers={},
            java_script_enabled=True,
            timeout=30000.0,
            allowed_domains=["example.com", "auth.example.com"],
        )


class FileUploadResponse(BaseModel):
    """Response from file upload processing."""

    success: bool
    message: str
    parsed_data: Optional[ParsedTestCaseData] = None
    browser_config: Optional[BrowserConfigData] = None
    error: Optional[str] = None

    @classmethod
    def sample_factory_build(cls) -> "FileUploadResponse":
        """Create a sample instance for documentation."""
        return cls(
            success=True,
            message="File processed successfully",
            parsed_data=ParsedTestCaseData.sample_factory_build(),
            browser_config=BrowserConfigData.sample_factory_build(),
        )


file_upload_router = APIRouter(prefix="/file-upload", tags=["File Upload"])


def extract_file_content(file: UploadFile) -> str:
    """Extract text content from various file types.

    Args:
        file: The uploaded file

    Returns:
        str: Extracted text content

    Raises:
        HTTPException: If file type is unsupported or extraction fails
    """
    content = file.file.read()
    file_extension = file.filename.split(".")[-1].lower() if file.filename else ""

    try:
        if file_extension in ["txt", "py", "js", "ts", "toml", "json", "md"]:
            return content.decode("utf-8")
        elif file_extension == "csv":
            df = pd.read_csv(io.BytesIO(content))
            return df.to_string()
        elif file_extension in ["xls", "xlsx"]:
            df = pd.read_excel(io.BytesIO(content))
            return df.to_string()
        elif file_extension in ["doc", "docx"]:
            return docx2txt.process(io.BytesIO(content))
        elif file_extension == "pdf":
            # For PDF, we'd need additional libraries like PyPDF2 or pdfplumber
            # For now, return a placeholder
            return "PDF content extraction not implemented yet. Please convert to text format."
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type: {file_extension}",
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to extract content from file: {str(e)}",
        )


def create_openai_prompt(file_content: str, filename: str) -> str:
    """Create a prompt for OpenAI to parse the file content into test case format.

    Args:
        file_content: The extracted content from the file
        filename: Name of the uploaded file

    Returns:
        str: Formatted prompt for OpenAI
    """
    return f"""
You are an expert test case analyst for BugNinja automation platform. I have uploaded a file named "{filename}" with the following content:

---
{file_content}
---

Please analyze this content and extract or generate a comprehensive test case in the BugNinja format. Return your response as a JSON object with the following structure:

FOR NON-TOML FILES:
{{
    "test_name": "Clear, descriptive name for the test case",
    "test_description": "User-facing description explaining what this test validates (for manual testers)",
    "test_goal": "Specific completion condition that determines when the test passes",
    "extra_rules": ["Navigate to [url_route]", "Click login button", "Fill email field", "Verify success message"],
    "url_route": "Starting URL or route for the test (if not provided, suggest a reasonable default)",
    "allowed_domains": ["https://example.com", "https://subdomain.example.com"],
    "priority": "low|medium|high|critical",
    "category": "authentication|banking|payments|security|ui|api",
    "viewport": {{"width": 1920, "height": 1080}}
}}

FOR TOML FILES - EXTRACT EXACTLY AS-IS:
{{
    "test_name": "Use existing 'name' field from TOML",
    "test_description": "Use existing 'description' field from TOML",
    "test_goal": "Generate appropriate goal based on description",
    "extra_rules": "Use existing 'extra_instructions' array from TOML (empty array if empty)",
    "url_route": "Extract from description or suggest based on content",
    "allowed_domains": "Use existing 'allowed_domains' from TOML or extract from description",
    "priority": "medium",
    "category": "ui",
    "viewport": "Extract from run_config.viewport_width/height"
}}

CRITICAL Guidelines for extra_rules:
- ALWAYS start with navigation to the starting URL: "Navigate to [url_route]"
- Use DIRECT navigation to websites - NEVER use search engines or "site:" parameters
- Include ONLY navigation steps and user interactions like:
  • "Navigate to https://example.com/login"
  • "Click on the login button"
  • "Fill in the email field with test@example.com"  
  • "Navigate to the dashboard page"
  • "Verify the success message appears"
  • "Select 'Premium' from the subscription dropdown"

- FORBIDDEN actions in extra_rules:
  • Using Google search or any search engine
  • Using "site:" search parameters
  • Searching instead of direct navigation
  • Browser configuration like viewport sizes, user agents, or browser settings
  • Environment setup or technical configuration
  • Implementation details or code snippets

Other Guidelines:
1. test_description: Clear business purpose for manual testers to understand
2. test_goal: Specific measurable condition like "User successfully logs in and sees dashboard"
3. If content is code: Extract user actions and convert to navigation steps
4. If content is data: Create test scenarios based on data variations
5. If content is documentation: Extract user journeys and interactions
6. CRITICAL: If content is TOML file - FOLLOW THESE INSTRUCTIONS. Extract existing values exactly as they are:
   - Take the description field and add it to the Test Goal field as it is, do not modify it!
   - Generate a new Description field which is shorter for TOML files
   - Use existing extra_instructions array as extra_rules (do not add navigation steps)
   - Use existing name as test_name
   - Extract viewport from run_config section
   - Extract user_agent from run_config section
   - DO NOT add your own navigation steps or modify the original instructions
   - ALWAYS add allowed domains in the proper format!
7. Choose appropriate priority based on business impact
8. Include main domain and expected redirects in allowed_domains using full HTTPS URLs (e.g., "https://ebay.com", "https://www.ebay.com")
9. url_route should be the starting page URL
10. IMPORTANT: The first step in extra_rules must ALWAYS be "Navigate to [url_route]" to ensure the test starts at the correct page (EXCEPT for TOML files - use their existing extra_instructions as-is)
11. This is UI AUTOMATION testing - interact directly with the target website, never use search engines as intermediaries, unless the test case that you are parsing instructs you to do so. Include a rule like this: navigate directly to this website and no intermediaries.

Respond ONLY with the JSON object, no additional text or explanation.
"""


def create_browser_config_from_parsed_data(parsed_data: ParsedTestCaseData) -> BrowserConfigData:
    """Create browser configuration from parsed test case data.

    Args:
        parsed_data: Parsed test case data from OpenAI

    Returns:
        BrowserConfigData: Browser configuration with appropriate defaults
    """
    # Use browser configuration template with data from parsed content
    return BrowserConfigData(
        channel="Chromium",  # Default to Chromium (case-sensitive)
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        viewport=parsed_data.viewport
        or {"width": 1920, "height": 1080},  # Use viewport from parsed data
        device_scale_factor=1.0,
        color_scheme="light",
        accept_downloads=True,
        client_certificates=[],
        extra_http_headers={},
        java_script_enabled=True,
        timeout=30000.0,
        allowed_domains=parsed_data.allowed_domains,  # Use domains from parsed data
    )


async def process_with_openai(file_content: str, filename: str) -> ParsedTestCaseData:
    """Process file content with OpenAI to extract test case data.

    Args:
        file_content: The extracted content from the file
        filename: Name of the uploaded file

    Returns:
        ParsedTestCaseData: Parsed test case data

    Raises:
        HTTPException: If OpenAI processing fails
    """
    if not settings.AZURE_OPENAI_ENDPOINT or not settings.AZURE_OPENAI_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Azure OpenAI configuration is missing",
        )

    try:
        client = AzureOpenAI(
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            api_key=settings.AZURE_OPENAI_KEY,
            api_version="2024-02-01",
        )

        prompt = create_openai_prompt(file_content, filename)

        response = client.chat.completions.create(
            model="gpt-4",  # Adjust model name based on your Azure deployment
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert test case analyst. Always respond with valid JSON only.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0,
            max_tokens=2000,
        )

        response_content = response.choices[0].message.content.strip()

        # Clean up the response to ensure it's valid JSON
        json_match = re.search(r"\{.*\}", response_content, re.DOTALL)
        if json_match:
            json_str = json_match.group()
        else:
            json_str = response_content

        try:
            parsed_json = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to parse OpenAI response as JSON: {str(e)}",
            )

        # Validate and create ParsedTestCaseData
        return ParsedTestCaseData(**parsed_json)

    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OpenAI processing failed: {str(e)}",
        )


@file_upload_router.post(
    "/parse-test-case",
    response_model=FileUploadResponse,
    summary="Parse Test Case File",
    description="Upload a file and parse it into BugNinja test case format using OpenAI",
    status_code=status.HTTP_200_OK,
    responses={
        200: create_success_response("File processed successfully", FileUploadResponse),
        **COMMON_ERROR_RESPONSES,
    },
)
async def parse_test_case_file(
    file: UploadFile = File(..., description="Test case file to parse"),
    project_id: str = Form(..., description="Project ID for the test case"),
    db_session: Session = Depends(get_db),
) -> FileUploadResponse:
    """Parse an uploaded file into BugNinja test case format using OpenAI.

    This endpoint accepts various file types (CSV, Excel, text files, Python/JS code, etc.)
    and uses OpenAI to intelligently parse the content into a structured test case format
    that can be used to populate the test creation form.

    Supported file types:
    - Text files: .txt, .md
    - Code files: .py, .js, .ts
    - Configuration: .toml, .json
    - Spreadsheets: .csv, .xls, .xlsx
    - Documents: .doc, .docx
    - PDFs: .pdf (limited support)

    Args:
        file: The uploaded file containing test case information
        project_id: ID of the project this test case belongs to
        db_session: Database session dependency

    Returns:
        FileUploadResponse: Response containing parsed test case data or error information

    Raises:
        HTTPException: If file processing fails or OpenAI is unavailable
    """
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No filename provided",
            )

        # Extract content from file
        file_content = extract_file_content(file)

        if not file_content.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File appears to be empty",
            )

        # Process with OpenAI
        parsed_data = await process_with_openai(file_content, file.filename)

        # Create browser configuration from parsed data
        browser_config = create_browser_config_from_parsed_data(parsed_data)

        return FileUploadResponse(
            success=True,
            message="File processed successfully",
            parsed_data=parsed_data,
            browser_config=browser_config,
        )

    except HTTPException:
        raise
    except Exception as e:
        return FileUploadResponse(
            success=False,
            message="Failed to process file",
            error=str(e),
        )
