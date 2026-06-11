"""
Open Notebook - Notebook Management (Production)

Demonstrates creating, listing, updating, and deleting notebooks.
Optimized for production use with authentication and environment configuration.

Prerequisites:
    pip install requests

Configuration (one of):
    1. Environment variables:
       export OPEN_NOTEBOOK_URL="https://<your-domain.com>"
       export OPEN_NOTEBOOK_PASSWORD="your-password"
    
    2. .env file in project root:
       OPEN_NOTEBOOK_URL=https://<your-domain.com>
       OPEN_NOTEBOOK_PASSWORD=your-password

Usage:
    python scripts/notebook_management.py
"""

import os
from typing import Optional, List, Dict, Any

import requests
from scripts.config import get_config

config = get_config()
BASE_URL = config['api_url']
HEADERS = {
    'Authorization': f"Bearer {config['password']}",
    'Content-Type': 'application/json',
}
VERIFY_SSL = not config['insecure']
REQUEST_TIMEOUT = 30

_quiet = False
_print = print


def _pr(*args, **kwargs):
    if not _quiet:
        _print(*args, **kwargs)


def _validate_note(content, title=None, note_type="human", notebook_id=None):
    if not content or not content.strip():
        raise ValueError('Content cannot be empty or whitespace only')
    if note_type not in ("human", "ai"):
        raise ValueError("note_type must be 'human' or 'ai'")
    return {
        "content": content,
        "title": title,
        "note_type": note_type,
        "notebook_id": notebook_id,
    }


def create_notebook(name, description=""):
    """Create a new notebook."""
    response = requests.post(
        f"{BASE_URL}/notebooks",
        json={"name": name, "description": description},
        headers=HEADERS,
        verify=VERIFY_SSL,
    )
    response.raise_for_status()
    notebook = response.json()
    _pr(f"Created notebook: {notebook['id']} - {notebook['name']}")
    return notebook


def list_notebooks(archived=False):
    """List all notebooks, optionally filtering by archived status."""
    response = requests.get(
        f"{BASE_URL}/notebooks",
        params={"archived": archived},
        headers=HEADERS,
        verify=VERIFY_SSL,
    )
    response.raise_for_status()
    notebooks = response.json()
    _pr(f"Found {len(notebooks)} notebook(s):")
    for nb in notebooks:
        _pr(f"  - {nb['id']}: {nb['name']} "
              f"(sources: {nb.get('source_count', 0)}, "
              f"notes: {nb.get('note_count', 0)})")
    return notebooks


def get_notebook(notebook_id):
    """Retrieve a single notebook by ID."""
    response = requests.get(
        f"{BASE_URL}/notebooks/{notebook_id}",
        headers=HEADERS,
        verify=VERIFY_SSL,
    )
    response.raise_for_status()
    return response.json()


def update_notebook(notebook_id, name=None, description=None, archived=None):
    """Update notebook fields."""
    payload = {}
    if name is not None:
        payload["name"] = name
    if description is not None:
        payload["description"] = description
    if archived is not None:
        payload["archived"] = archived
    response = requests.put(
        f"{BASE_URL}/notebooks/{notebook_id}",
        json=payload,
        headers=HEADERS,
        verify=VERIFY_SSL,
    )
    response.raise_for_status()
    updated = response.json()
    _pr(f"Updated notebook: {updated['id']} - {updated['name']}")
    return updated


def delete_notebook(notebook_id, delete_sources=False):
    """Delete a notebook and optionally its exclusive sources."""
    preview = requests.get(
        f"{BASE_URL}/notebooks/{notebook_id}/delete-preview",
        headers=HEADERS,
        verify=VERIFY_SSL,
    ).json()
    _pr(f"Deletion will affect {preview.get('note_count', 0)} notes "
          f"and {preview.get('source_count', 0)} sources")

    response = requests.delete(
        f"{BASE_URL}/notebooks/{notebook_id}",
        params={"delete_sources": delete_sources},
        headers=HEADERS,
        verify=VERIFY_SSL,
    )
    response.raise_for_status()
    _pr(f"Deleted notebook: {notebook_id}")


def link_source_to_notebook(notebook_id, source_id):
    """Associate an existing source with a notebook."""
    response = requests.post(
        f"{BASE_URL}/notebooks/{notebook_id}/sources/{source_id}",
        headers=HEADERS,
        verify=VERIFY_SSL,
    )
    response.raise_for_status()
    _pr(f"Linked source {source_id} to notebook {notebook_id}")


def unlink_source_from_notebook(notebook_id, source_id):
    """Remove the association between a source and a notebook."""
    response = requests.delete(
        f"{BASE_URL}/notebooks/{notebook_id}/sources/{source_id}",
        headers=HEADERS,
        verify=VERIFY_SSL,
    )
    response.raise_for_status()
    _pr(f"Unlinked source {source_id} from notebook {notebook_id}")


# =============================================================================
# NOTE MANAGEMENT
# =============================================================================

def create_note(notebook_id: str, content: str, title: Optional[str] = None,
                note_type: str = "human") -> Dict[str, Any]:
    """Create a new note in a notebook.
    
    Args:
        notebook_id: ID of the notebook to add the note to
        content: Note content (required, must be non-empty)
        title: Optional note title (max 255 chars)
        note_type: Either "human" or "ai" (default: "human")
    
    Returns:
        Created note object with id, title, content, etc.
    """
    payload = _validate_note(content, title=title, note_type=note_type, notebook_id=notebook_id)
    
    response = requests.post(
        f"{BASE_URL}/notes",
        json=payload,
        headers=HEADERS,
        verify=VERIFY_SSL,
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    note = response.json()
    _pr(f"Created note: {note['id']} - {note.get('title', 'Untitled')}")
    return note


def list_notes(notebook_id: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
    """List notes, optionally filtered by notebook.
    
    Args:
        notebook_id: Optional notebook ID to filter by
        limit: Maximum number of notes to return (default: 20)
    
    Returns:
        List of note objects
    """
    params = {"limit": limit}
    if notebook_id:
        params["notebook_id"] = notebook_id
    
    response = requests.get(
        f"{BASE_URL}/notes",
        params=params,
        headers=HEADERS,
        verify=VERIFY_SSL,
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    notes = response.json()
    _pr(f"Found {len(notes)} note(s):")
    for note in notes:
        _pr(f"  - {note['id']}: {note.get('title', 'Untitled')} "
              f"({note.get('note_type', 'unknown')})")
    return notes


def get_note(note_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve a single note by ID.
    
    Args:
        note_id: Note ID to retrieve
    
    Returns:
        Note object or None if not found
    """
    if not note_id or not isinstance(note_id, str):
        raise ValueError("note_id must be a non-empty string")
    
    response = requests.get(
        f"{BASE_URL}/notes/{note_id}",
        headers=HEADERS,
        verify=VERIFY_SSL,
        timeout=REQUEST_TIMEOUT,
    )
    if response.status_code == 404:
        _pr(f"Note not found: {note_id}")
        return None
    response.raise_for_status()
    return response.json()


def update_note(note_id: str, title: Optional[str] = None,
                content: Optional[str] = None,
                note_type: Optional[str] = None) -> Dict[str, Any]:
    """Update a note's fields.
    
    Args:
        note_id: Note ID to update
        title: New title (optional, max 255 chars)
        content: New content (optional, must be non-empty)
        note_type: Either "human" or "ai" (optional)
    
    Returns:
        Updated note object
    """
    if not note_id or not isinstance(note_id, str):
        raise ValueError("note_id must be a non-empty string")
    
    if content is not None and (not content or not content.strip()):
        raise ValueError('Content cannot be empty or whitespace only')
    if note_type is not None and note_type not in ("human", "ai"):
        raise ValueError("note_type must be 'human' or 'ai'")
    
    payload = {}
    if title is not None:
        payload["title"] = title
    if content is not None:
        payload["content"] = content
    if note_type is not None:
        payload["note_type"] = note_type
    if not payload:
        raise ValueError("At least one field must be provided for update")
    
    response = requests.put(
        f"{BASE_URL}/notes/{note_id}",
        json=payload,
        headers=HEADERS,
        verify=VERIFY_SSL,
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    note = response.json()
    _pr(f"Updated note: {note['id']} - {note.get('title', 'Untitled')}")
    return note


def delete_note(note_id: str) -> None:
    """Delete a note.
    
    Args:
        note_id: Note ID to delete
    """
    if not note_id or not isinstance(note_id, str):
        raise ValueError("note_id must be a non-empty string")
    
    response = requests.delete(
        f"{BASE_URL}/notes/{note_id}",
        headers=HEADERS,
        verify=VERIFY_SSL,
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    _pr(f"Deleted note: {note_id}")


if __name__ == "__main__":
    _pr("=== Notebook Management Demo ===\n")

    nb1 = create_notebook(
        "Protein Folding Research",
        "Literature review on AlphaFold and related methods"
    )
    nb2 = create_notebook(
        "CRISPR Gene Editing",
        "Survey of CRISPR-Cas9 applications in therapeutics"
    )

    _pr()
    list_notebooks()

    _pr()
    update_notebook(nb1["id"], description="Updated: Including ESMFold comparisons")

    _pr()
    update_notebook(nb2["id"], archived=True)
    _pr("\nActive notebooks:")
    list_notebooks(archived=False)

    _pr("\nArchived notebooks:")
    list_notebooks(archived=True)

    _pr()
    delete_notebook(nb1["id"])
    delete_notebook(nb2["id"])
