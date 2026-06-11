#!/usr/bin/env python3
"""
Open Notebook - Source-Specific Chat (Production)

Focused chat on a single source (not the whole notebook).
Uses POST-and-wait (synchronous) like general chat.

API Endpoints:
  POST /api/sources/{source_id}/chat/sessions          - Create session
  GET  /api/sources/{source_id}/chat/sessions          - List sessions
  GET  /api/sources/{source_id}/chat/sessions/{id}     - Get session
  PUT  /api/sources/{source_id}/chat/sessions/{id}     - Update session
  DELETE /api/sources/{source_id}/chat/sessions/{id}   - Delete session
  POST /api/sources/{source_id}/chat/sessions/{id}/messages - Send message
"""

import json
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


def create_source_chat_session(source_id, title=None, model_override=None):
    """Create a chat session focused on a single source.
    
    Args:
        source_id: ID of the source to chat about
        title: Optional session title
        model_override: Optional model ID override
    
    Returns:
        Created session object
    """
    payload = {"source_id": source_id}
    if title:
        payload["title"] = title
    if model_override:
        payload["model_override"] = model_override
    
    response = requests.post(
        f"{BASE_URL}/sources/{source_id}/chat/sessions",
        json=payload,
        headers=HEADERS,
        verify=VERIFY_SSL,
    )
    response.raise_for_status()
    session = response.json()
    _pr(f"Created source chat session: {session['id']} - {session.get('title', 'Untitled')}")
    return session


def list_source_chat_sessions(source_id):
    """List all chat sessions for a specific source.
    
    Args:
        source_id: Source ID to list sessions for
    
    Returns:
        List of session objects
    """
    response = requests.get(
        f"{BASE_URL}/sources/{source_id}/chat/sessions",
        headers=HEADERS,
        verify=VERIFY_SSL,
    )
    response.raise_for_status()
    sessions = response.json()
    _pr(f"Found {len(sessions)} source chat session(s) for source {source_id}:")
    for s in sessions:
        _pr(f"  - {s['id']}: {s.get('title', 'Untitled')} "
              f"({s.get('message_count', 0)} messages)")
    return sessions


def get_source_chat_session(source_id, session_id):
    """Get a specific source chat session with its messages.
    
    Args:
        source_id: Source ID
        session_id: Session ID
    
    Returns:
        Session object with messages
    """
    response = requests.get(
        f"{BASE_URL}/sources/{source_id}/chat/sessions/{session_id}",
        headers=HEADERS,
        verify=VERIFY_SSL,
    )
    response.raise_for_status()
    session = response.json()
    messages = session.get("messages", [])
    _pr(f"\n--- Source Chat Session ({len(messages)} messages) ---")
    for msg in messages:
        msg_type = msg.get("type", "unknown")
        role = msg.get("role", msg_type)
        content = msg.get("content", "")
        _pr(f"[{role}]: {content}")
    return session


def update_source_chat_session(source_id, session_id, title=None, model_override=None):
    """Update a source chat session.
    
    Args:
        source_id: Source ID
        session_id: Session ID
        title: New title (optional)
        model_override: New model override (optional)
    
    Returns:
        Updated session object
    """
    payload = {}
    if title is not None:
        payload["title"] = title
    if model_override is not None:
        payload["model_override"] = model_override
    
    response = requests.put(
        f"{BASE_URL}/sources/{source_id}/chat/sessions/{session_id}",
        json=payload,
        headers=HEADERS,
        verify=VERIFY_SSL,
    )
    response.raise_for_status()
    session = response.json()
    _pr(f"Updated source chat session: {session['id']}")
    return session


def delete_source_chat_session(source_id, session_id):
    """Delete a source chat session.
    
    Args:
        source_id: Source ID
        session_id: Session ID
    """
    response = requests.delete(
        f"{BASE_URL}/sources/{source_id}/chat/sessions/{session_id}",
        headers=HEADERS,
        verify=VERIFY_SSL,
    )
    response.raise_for_status()
    _pr(f"Deleted source chat session: {session_id}")


def send_source_chat_message(source_id, session_id, message, model_override=None, stream=True):
    """Send a message to a source chat session.
    
    Args:
        source_id: Source ID
        session_id: Session ID
        message: User message
        model_override: Optional model override
        stream: If True, use SSE streaming (default). If False, return full response.
    
    Returns:
        If stream=False: dict with full response
        If stream=True: string with the full response text
    """
    payload = {"message": message}
    if model_override:
        payload["model_override"] = model_override
    
    headers = {
        'Authorization': f"Bearer {config['password']}",
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream' if stream else 'application/json',
    }
    
    response = requests.post(
        f"{BASE_URL}/sources/{source_id}/chat/sessions/{session_id}/messages",
        json=payload,
        headers=headers,
        verify=VERIFY_SSL,
        stream=stream,
    )
    response.raise_for_status()
    
    if not stream:
        # POST-and-wait mode
        result = response.json()
        _pr(f"\nUser: {message}")
        _pr(f"AI: {result.get('response', result)}")
        return result
    
    # SSE streaming mode
    _pr(f"\nUser: {message}")
    _pr("AI: ", end="", flush=True)
    
    full_response = []
    ai_response_started = False
    for line in response.iter_lines():
        if line:
            decoded = line.decode('utf-8')
            if decoded.startswith('data: '):
                data = decoded[6:]
                if data == '[DONE]':
                    break
                try:
                    chunk = json.loads(data)
                    msg_type = chunk.get('type', '')
                    content = chunk.get('content', '')
                    
                    # Skip user_message and other metadata
                    if msg_type == 'user_message':
                        continue
                    if msg_type == 'context_indicators':
                        continue
                    
                    # Only process ai_message content
                    if content and msg_type in ('ai_message', 'assistant'):
                        if not ai_response_started:
                            ai_response_started = True
                        _pr(content, end="", flush=True)
                        full_response.append(content)
                except json.JSONDecodeError:
                    pass
    
    _pr()  # Newline after streaming
    return ''.join(full_response)
