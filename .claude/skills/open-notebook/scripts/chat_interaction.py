"""
Open Notebook - Chat Interaction (Production)

Demonstrates creating chat sessions, sending messages with context,
and searching across research materials.
Optimized for production use with authentication and environment configuration.

Prerequisites:
    pip install requests

Configuration:
    export OPEN_NOTEBOOK_URL="https://<your-domain.com>"
    export OPEN_NOTEBOOK_PASSWORD="your-password"

Usage:
    python scripts/chat_interaction.py
"""

import requests
from scripts.config import get_config

config = get_config()
BASE_URL = config['api_url']
HEADERS = {
    'Authorization': f"Bearer {config['password']}",
    'Content-Type': 'application/json',
}
VERIFY_SSL = not config['insecure']

_quiet = False
_print = print


def _pr(*args, **kwargs):
    if not _quiet:
        _print(*args, **kwargs)


def create_chat_session(notebook_id, title, model_override=None):
    """Create a new chat session within a notebook."""
    payload = {
        "notebook_id": notebook_id,
        "title": title,
    }
    if model_override:
        payload["model_override"] = model_override
    response = requests.post(
        f"{BASE_URL}/chat/sessions",
        json=payload,
        headers=HEADERS,
        verify=VERIFY_SSL,
    )
    response.raise_for_status()
    session = response.json()
    _pr(f"Created chat session: {session['id']} - {title}")
    return session


def list_chat_sessions(notebook_id):
    """List all chat sessions for a notebook."""
    response = requests.get(
        f"{BASE_URL}/chat/sessions",
        params={"notebook_id": notebook_id},
        headers=HEADERS,
        verify=VERIFY_SSL,
    )
    response.raise_for_status()
    sessions = response.json()
    _pr(f"Found {len(sessions)} chat session(s):")
    for s in sessions:
        _pr(f"  - {s['id']}: {s.get('title', 'Untitled')} "
              f"({s.get('message_count', 0)} messages)")
    return sessions


def send_chat_message(session_id, message, include_sources=True,
                       include_notes=True, model_override=None):
    """Send a message to a chat session with context from sources and notes."""
    payload = {
        "session_id": session_id,
        "message": message,
        "context": {
            "include_sources": include_sources,
            "include_notes": include_notes,
        },
    }
    if model_override:
        payload["model_override"] = model_override
    response = requests.post(
        f"{BASE_URL}/chat/execute",
        json=payload,
        headers=HEADERS,
        verify=VERIFY_SSL,
    )
    response.raise_for_status()
    result = response.json()
    _pr(f"\nUser: {message}")
    _pr(f"AI: {result.get('response', result)}")
    return result


def get_session_history(session_id):
    """Retrieve full message history for a chat session.
    
    Args:
        session_id: Chat session ID
    """
    response = requests.get(
        f"{BASE_URL}/chat/sessions/{session_id}",
        headers=HEADERS,
        verify=VERIFY_SSL,
    )
    response.raise_for_status()
    session = response.json()
    messages = session.get("messages", [])
    _pr(f"\n--- Session History ({len(messages)} messages) ---")
    for msg in messages:
        role = msg.get("role", "unknown")
        content = msg.get("content", "")
        _pr(f"[{role}]: {content}")
    return session


def build_context(notebook_id, source_ids=None, note_ids=None):
    """Build context data from sources and notes for inspection."""
    payload = {"notebook_id": notebook_id}
    if source_ids:
        payload["source_ids"] = source_ids
    if note_ids:
        payload["note_ids"] = note_ids
    response = requests.post(
        f"{BASE_URL}/chat/context",
        json=payload,
        headers=HEADERS,
        verify=VERIFY_SSL,
    )
    response.raise_for_status()
    context = response.json()
    _pr(f"Context built: {context.get('token_count', '?')} tokens, "
          f"{context.get('char_count', '?')} characters")
    return context


def search_knowledge_base(query, search_type="vector", limit=5):
    """Search across all materials in the knowledge base."""
    response = requests.post(
        f"{BASE_URL}/search",
        json={
            "query": query,
            "search_type": search_type,
            "limit": limit,
        },
        headers=HEADERS,
        verify=VERIFY_SSL,
    )
    response.raise_for_status()
    results = response.json()
    _pr(f"\nSearch results for '{query}' ({results.get('total', 0)} hits):")
    for r in results.get("results", []):
        title = r.get("title", "Untitled")
        similarity = r.get("similarity", "N/A")
        _pr(f"  - {title} (similarity: {similarity})")
    return results


def ask_question(query):
    """Ask a question and get an AI-generated answer from the knowledge base."""
    response = requests.post(
        f"{BASE_URL}/search/ask/simple",
        json={"query": query},
        headers=HEADERS,
        verify=VERIFY_SSL,
    )
    response.raise_for_status()
    result = response.json()
    _pr(f"\nQ: {query}")
    _pr(f"A: {result.get('response', result)}")
    return result


def delete_chat_session(session_id):
    """Delete a chat session."""
    response = requests.delete(
        f"{BASE_URL}/chat/sessions/{session_id}",
        headers=HEADERS,
        verify=VERIFY_SSL,
    )
    response.raise_for_status()
    _pr(f"Deleted chat session: {session_id}")


if __name__ == "__main__":
    _pr("=== Chat Interaction Demo ===\n")

    notebook = requests.post(
        f"{BASE_URL}/notebooks",
        json={
            "name": "Chat Demo",
            "description": "Demonstrating chat interactions",
        },
        headers=HEADERS,
        verify=VERIFY_SSL,
    ).json()
    notebook_id = notebook["id"]

    requests.post(
        f"{BASE_URL}/sources",
        data={
            "text": (
                "Immunotherapy has revolutionized cancer treatment. "
                "Checkpoint inhibitors targeting PD-1 and PD-L1 have shown "
                "remarkable efficacy in non-small cell lung cancer, melanoma, "
                "and several other tumor types. Tumor mutational burden (TMB) "
                "has emerged as a key biomarker for predicting response to "
                "immunotherapy. Patients with high TMB tend to generate more "
                "neoantigens, making their tumors more visible to the immune system."
            ),
            "notebook_id": notebook_id,
            "process_async": "false",
        },
        headers={'Authorization': f"Bearer {config['password']}"},
        verify=VERIFY_SSL,
    )

    session = create_chat_session(notebook_id, "Immunotherapy Discussion")

    _pr()
    send_chat_message(
        session["id"],
        "What are the main biomarkers for immunotherapy response?",
    )

    send_chat_message(
        session["id"],
        "How does TMB relate to neoantigen load?",
    )

    get_session_history(session["id"])

    search_knowledge_base("checkpoint inhibitor efficacy")

    ask_question("What is the role of PD-L1 in cancer immunotherapy?")

    _pr()
    delete_chat_session(session["id"])
    requests.delete(
        f"{BASE_URL}/notebooks/{notebook_id}",
        headers=HEADERS,
        verify=VERIFY_SSL,
    )
    _pr("Cleanup complete")
