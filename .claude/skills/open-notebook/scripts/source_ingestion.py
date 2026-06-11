"""
Open Notebook - Source Ingestion (Production)

Demonstrates ingesting various content types (URLs, files, text) into
Open Notebook and monitoring processing status.
Optimized for production use with authentication and environment configuration.

Prerequisites:
    pip install requests

Configuration:
    export OPEN_NOTEBOOK_URL="https://<your-domain.com>"
    export OPEN_NOTEBOOK_PASSWORD="your-password"

Usage:
    python scripts/source_ingestion.py
"""

import os
import time
from typing import Optional, List, Dict, Any

import requests
from scripts.config import get_config

config = get_config()
BASE_URL = config['api_url']
HEADERS = {
    'Authorization': f"Bearer {config['password']}",
}
VERIFY_SSL = not config['insecure']
REQUEST_TIMEOUT = 50
TRANSFORMATION_TIMEOUT = 60

_quiet = False
_print = print


def _pr(*args, **kwargs):
    if not _quiet:
        _print(*args, **kwargs)


def _check_not_empty(value, field_name):
    if not value or not str(value).strip():
        raise ValueError(f'{field_name} cannot be empty')


def add_url_source(notebook_id, url, process_async=True, embed=True):
    """Add a web URL as a source to a notebook."""
    data = {
        "type": "link",
        "url": url,
        "notebook_id": notebook_id,
        "process_async": str(process_async).lower(),
    }
    if embed:
        data["embed"] = "true"
    response = requests.post(
        f"{BASE_URL}/sources",
        data=data,
        headers=HEADERS,
        verify=VERIFY_SSL,
    )
    response.raise_for_status()
    source = response.json()
    _pr(f"Added URL source: {source['id']} - {url}")
    return source


def add_text_source(notebook_id, title, text, embed=True):
    """Add raw text as a source."""
    data = {
        "type": "text",
        "text": text,
        "notebook_id": notebook_id,
        "process_async": "false",
    }
    if embed:
        data["embed"] = "true"
    response = requests.post(
        f"{BASE_URL}/sources",
        data=data,
        headers=HEADERS,
        verify=VERIFY_SSL,
    )
    response.raise_for_status()
    source = response.json()
    _pr(f"Added text source: {source['id']} - {title}")
    return source


def upload_file_source(notebook_id, file_path, process_async=True, embed=True):
    """Upload a file (PDF, DOCX, audio, video) as a source."""
    filename = os.path.basename(file_path)
    data = {
        "type": "upload",
        "notebook_id": notebook_id,
        "process_async": str(process_async).lower(),
    }
    if embed:
        data["embed"] = "true"
    with open(file_path, "rb") as f:
        response = requests.post(
            f"{BASE_URL}/sources",
            data=data,
            files={"file": (filename, f)},
            headers={'Authorization': f"Bearer {config['password']}"},
            verify=VERIFY_SSL,
        )
    response.raise_for_status()
    source = response.json()
    _pr(f"Uploaded file source: {source['id']} - {filename}")
    return source


def wait_for_processing(source_id, poll_interval=5, timeout=300):
    """Poll source processing status until completion or timeout."""
    elapsed = 0
    while elapsed < timeout:
        response = requests.get(
            f"{BASE_URL}/sources/{source_id}/status",
            headers=HEADERS,
            verify=VERIFY_SSL,
        )
        response.raise_for_status()
        status = response.json()
        current_status = status.get("status", "unknown")
        _pr(f"  Source {source_id}: {current_status}")

        if current_status in ("completed", "failed"):
            return status
        time.sleep(poll_interval)
        elapsed += poll_interval

    _pr(f"  Source {source_id}: timed out after {timeout}s")
    return None


def embed_source(source_id: str, async_processing: bool = False) -> Dict[str, Any]:
    """Embed an existing source for vector search.
    
    Args:
        source_id: ID of the source to embed
        async_processing: Process asynchronously in background
    
    Returns:
        Embed response with success status and command_id
    """
    response = requests.post(
        f"{BASE_URL}/embed",
        json={
            "item_id": source_id,
            "item_type": "source",
            "async_processing": async_processing,
        },
        headers=HEADERS,
        verify=VERIFY_SSL,
    )
    response.raise_for_status()
    result = response.json()
    _pr(f"Embedding source: {result.get('message', 'Done')}")
    return result


def rebuild_embeddings(mode: str = "existing",
                        include_sources: bool = True,
                        include_notes: bool = True,
                        include_insights: bool = True) -> Dict[str, Any]:
    """Rebuild all embeddings in the background.
    
    Args:
        mode: "existing" (re-embed items with embeddings) or "all" (embed everything)
        include_sources: Include sources in rebuild
        include_notes: Include notes in rebuild
        include_insights: Include insights in rebuild
    
    Returns:
        Rebuild response with command_id and estimated item count
    """
    response = requests.post(
        f"{BASE_URL}/embeddings/rebuild",
        json={
            "mode": mode,
            "include_sources": include_sources,
            "include_notes": include_notes,
            "include_insights": include_insights,
        },
        headers=HEADERS,
        verify=VERIFY_SSL,
    )
    response.raise_for_status()
    result = response.json()
    _pr(f"Rebuild started: {result.get('command_id', 'N/A')} — {result.get('estimated_items', 0)} items")
    return result


def get_rebuild_status(command_id: str) -> Dict[str, Any]:
    """Get the status of a rebuild operation.
    
    Args:
        command_id: The command ID from rebuild_embeddings
    
    Returns:
        Rebuild status with progress, stats, and timestamps
    """
    response = requests.get(
        f"{BASE_URL}/embeddings/rebuild/{command_id}/status",
        headers=HEADERS,
        verify=VERIFY_SSL,
    )
    response.raise_for_status()
    return response.json()


def list_sources(notebook_id=None, limit=20):
    """List sources, optionally filtered by notebook."""
    params = {"limit": limit}
    if notebook_id:
        params["notebook_id"] = notebook_id
    response = requests.get(
        f"{BASE_URL}/sources",
        params=params,
        headers=HEADERS,
        verify=VERIFY_SSL,
    )
    response.raise_for_status()
    sources = response.json()
    _pr(f"Found {len(sources)} source(s):")
    for src in sources:
        _pr(f"  - {src['id']}: {src.get('title', 'Untitled')}")
    return sources


def get_source(source_id: str) -> Dict[str, Any]:
    """Get a single source by ID with full details."""
    response = requests.get(
        f"{BASE_URL}/sources/{source_id}",
        headers=HEADERS,
        verify=VERIFY_SSL,
    )
    response.raise_for_status()
    return response.json()


def get_transformation(transformation_id: str) -> Dict[str, Any]:
    """Get a single transformation by ID with full details."""
    response = requests.get(
        f"{BASE_URL}/transformations/{transformation_id}",
        headers=HEADERS,
        verify=VERIFY_SSL,
    )
    response.raise_for_status()
    return response.json()


def get_source_insights(source_id):
    """Retrieve AI-generated insights for a source."""
    response = requests.get(
        f"{BASE_URL}/sources/{source_id}/insights",
        headers=HEADERS,
        verify=VERIFY_SSL,
    )
    response.raise_for_status()
    return response.json()


def get_insight(source_id: str, insight_id: str) -> Dict[str, Any]:
    """Retrieve a single insight by source and insight ID.
    
    Args:
        source_id: Source ID (e.g., source:abc123)
        insight_id: Insight ID (e.g., source_insight:xyz789)
    
    Returns:
        Insight object with full content
    
    Raises:
        ValueError: If insight not found
    """
    # Try direct API first (fast, O(1))
    try:
        response = requests.get(
            f"{BASE_URL}/insights/{insight_id}",
            headers=HEADERS,
            verify=VERIFY_SSL,
        )
        response.raise_for_status()
        return response.json()
    except requests.HTTPError:
        pass
    
    # Fallback: list all and filter (slower, but reliable)
    insights = get_source_insights(source_id)
    for insight in insights:
        if insight.get('id') == insight_id:
            return insight
    
    raise ValueError(f"Insight not found: {insight_id}")


def retry_failed_source(source_id):
    """Retry processing for a failed source."""
    response = requests.post(
        f"{BASE_URL}/sources/{source_id}/retry",
        headers=HEADERS,
        verify=VERIFY_SSL,
    )
    response.raise_for_status()
    _pr(f"Retrying source: {source_id}")
    return response.json()


def delete_source(source_id):
    """Delete a source."""
    response = requests.delete(
        f"{BASE_URL}/sources/{source_id}",
        headers=HEADERS,
        verify=VERIFY_SSL,
    )
    response.raise_for_status()
    _pr(f"Deleted source: {source_id}")


# =============================================================================
# INSIGHT MANAGEMENT
# =============================================================================

def create_source_insight(source_id: str, transformation_id: str,
                          model_id: Optional[str] = None,
                          poll_interval: int = 5, timeout: int = 300) -> Dict[str, Any]:
    """Generate an AI insight for a source using a transformation.
    
    This creates an insight by applying a transformation to the source content.
    The insight generation is async and this function polls until completion.
    
    Args:
        source_id: ID of the source to analyze
        transformation_id: ID of the transformation to apply
        model_id: Optional model ID (uses default if not provided)
        poll_interval: Seconds between status checks (default: 5)
        timeout: Maximum seconds to wait (default: 300)
    
    Returns:
        Insight object or status dict
    """
    _check_not_empty(source_id, 'source_id')
    _check_not_empty(transformation_id, 'transformation_id')
    
    response = requests.post(
        f"{BASE_URL}/sources/{source_id}/insights",
        json={
            "transformation_id": transformation_id,
            "model_id": model_id,
        },
        headers=HEADERS,
        verify=VERIFY_SSL,
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    result = response.json()
    _pr(f"Insight generation started: {result.get('command_id', 'N/A')}")
    
    # Poll for completion
    if result.get("status") == "pending":
        return wait_for_insight(source_id, poll_interval, timeout)
    
    return result


def wait_for_insight(source_id: str, poll_interval: int = 5,
                     timeout: int = 300) -> Optional[Dict[str, Any]]:
    """Poll for insight generation completion.
    
    Args:
        source_id: Source ID to check
        poll_interval: Seconds between checks
        timeout: Maximum seconds to wait
    
    Returns:
        First insight dict or None if timed out
    """
    elapsed = 0
    while elapsed < timeout:
        insights = get_source_insights(source_id)
        if insights:
            _pr(f"  Insights generated for {source_id}: {len(insights)} insight(s)")
            return insights[0]
        time.sleep(poll_interval)
        elapsed += poll_interval
    
    _pr(f"  Insight generation timed out after {timeout}s for {source_id}")
    return None


def list_transformations() -> List[Dict[str, Any]]:
    """List all available transformations.
    
    Returns:
        List of transformation objects
    """
    response = requests.get(
        f"{BASE_URL}/transformations",
        headers=HEADERS,
        verify=VERIFY_SSL,
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    transformations = response.json()
    _pr(f"Found {len(transformations)} transformation(s):")
    for t in transformations:
        _pr(f"  - {t['id']}: {t.get('title', 'Untitled')}")
    return transformations


def create_transformation(name: str, title: str, description: str,
                          prompt: str, apply_default: bool = False) -> Dict[str, Any]:
    """Create a new AI transformation.
    
    Args:
        name: Unique identifier name (e.g. "extract_methods")
        title: Display title (e.g. "Extract Methods")
        description: What this transformation does
        prompt: The AI prompt template
        apply_default: Whether to apply automatically (default: False)
    
    Returns:
        Created transformation object
    """
    _check_not_empty(name, 'name')
    _check_not_empty(title, 'title')
    _check_not_empty(description, 'description')
    _check_not_empty(prompt, 'prompt')
    if len(name) > 255:
        raise ValueError('name exceeds 255 characters')
    if len(title) > 255:
        raise ValueError('title exceeds 255 characters')
    if len(description) > 1000:
        raise ValueError('description exceeds 1000 characters')
    if len(prompt) > 10000:
        raise ValueError('prompt exceeds 10000 characters')
    
    response = requests.post(
        f"{BASE_URL}/transformations",
        json={
            "name": name,
            "title": title,
            "description": description,
            "prompt": prompt,
            "apply_default": apply_default,
        },
        headers=HEADERS,
        verify=VERIFY_SSL,
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    transformation = response.json()
    _pr(f"Created transformation: {transformation['id']} - {transformation['title']}")
    return transformation


def execute_transformation(transformation_id: str, input_text: str,
                           model_id: str) -> Dict[str, Any]:
    """Execute a transformation on input text.
    
    Args:
        transformation_id: ID of the transformation to execute
        input_text: Text to transform
        model_id: Model ID to use for the transformation
    
    Returns:
        Result with 'output' field containing transformed text
    """
    _check_not_empty(transformation_id, 'transformation_id')
    _check_not_empty(input_text, 'input_text')
    _check_not_empty(model_id, 'model_id')
    
    response = requests.post(
        f"{BASE_URL}/transformations/execute",
        json={
            "transformation_id": transformation_id,
            "input_text": input_text,
            "model_id": model_id,
        },
        headers=HEADERS,
        verify=VERIFY_SSL,
        timeout=TRANSFORMATION_TIMEOUT,
    )
    response.raise_for_status()
    result = response.json()
    _pr(f"Transformation executed: {result.get('transformation_id', 'N/A')}")
    return result


def save_insight_as_note(insight_id: str, notebook_id: str) -> Dict[str, Any]:
    """Save an insight as a note in a notebook.
    
    Args:
        insight_id: ID of the insight to save
        notebook_id: ID of the notebook to add the note to
    
    Returns:
        Created note object
    """
    if not insight_id or not isinstance(insight_id, str):
        raise ValueError("insight_id must be a non-empty string")
    if not notebook_id or not isinstance(notebook_id, str):
        raise ValueError("notebook_id must be a non-empty string")
    
    response = requests.post(
        f"{BASE_URL}/insights/{insight_id}/save-as-note",
        json={"notebook_id": notebook_id},
        headers=HEADERS,
        verify=VERIFY_SSL,
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    note = response.json()
    _pr(f"Saved insight as note: {note['id']}")
    return note


if __name__ == "__main__":
    _pr("=== Source Ingestion Demo ===\n")

    notebook = requests.post(
        f"{BASE_URL}/notebooks",
        json={
            "name": "Source Ingestion Demo",
            "description": "Testing various source types",
        },
        headers={'Authorization': f"Bearer {config['password']}",
                 'Content-Type': 'application/json'},
        verify=VERIFY_SSL,
    ).json()
    notebook_id = notebook["id"]
    _pr(f"Created notebook: {notebook_id}\n")

    url_source = add_url_source(
        notebook_id,
        "https://en.wikipedia.org/wiki/CRISPR_gene_editing",
    )

    text_source = add_text_source(
        notebook_id,
        "Research Notes",
        "CRISPR-Cas9 is a genome editing tool that allows researchers to "
        "alter DNA sequences and modify gene function. It has transformed "
        "biological research and offers potential for treating genetic diseases.",
    )

    _pr("\nWaiting for processing...")
    wait_for_processing(url_source["id"])

    _pr()
    list_sources(notebook_id)

    _pr()
    delete_source(url_source["id"])
    delete_source(text_source["id"])
    requests.delete(
        f"{BASE_URL}/notebooks/{notebook_id}",
        headers=HEADERS,
        verify=VERIFY_SSL,
    )
    _pr("Cleanup complete")
