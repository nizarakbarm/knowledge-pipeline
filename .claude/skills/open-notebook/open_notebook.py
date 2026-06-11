#!/usr/bin/env python3
"""
Open Notebook - Production CLI

A secure, user-friendly command-line interface for managing Open Notebook
notebooks, sources, notes, chat sessions, and insights.

Security features:
- Never exposes credentials in logs or output
- SSL verification enabled by default
- Secure defaults for all operations
- Confirmation prompts for destructive actions

Usage examples:
    # Notebooks
    python open_notebook.py notebook create "Research" --description "Cancer Genomics"
    python open_notebook.py notebook list
    python open_notebook.py notebook get <notebook-id>

    # Sources
    python open_notebook.py source add-url <notebook-id> "https://arxiv.org/..." --wait
    python open_notebook.py source upload <notebook-id> /path/to/paper.pdf --wait

    # Chat
    python open_notebook.py chat create <notebook-id> "Discussion"
    python open_notebook.py chat send <session-id> "What are the key findings?"

    # Workflow
    python open_notebook.py workflow complete --name "Research" --url "https://..."

    # JSON output for scripting
    python open_notebook.py --json notebook list
    python open_notebook.py --quiet source status <source-id>
"""

import json
import logging
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

import click
from scripts import (
    notebook_management,
    source_ingestion,
    chat_interaction,
)
from scripts import source_chat as source_chat_mod

# =============================================================================
# CONFIGURATION & LOGGING
# =============================================================================

def setup_logging(verbose: bool, quiet: bool):
    """Configure logging based on verbosity flags."""
    if quiet:
        level = logging.WARNING
    elif verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO

    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )

# =============================================================================
# OUTPUT FORMATTING
# =============================================================================

class OutputFormatter:
    """Handles different output formats (text, json, quiet)."""

    def __init__(self, json_mode: bool, quiet: bool):
        self.json_mode = json_mode
        self.quiet = quiet
        self.data = []

    def _should_print(self):
        return not self.quiet and not self.json_mode

    def echo(self, message: str, err: bool = False, nl: bool = True):
        """Print message unless in quiet or json mode."""
        if self._should_print():
            click.echo(message, err=err, nl=nl)

    def success(self, message: str):
        """Print success message."""
        if self._should_print():
            click.echo(click.style("✓ ", fg="green") + message)

    def error(self, message: str):
        """Print error message (always shown)."""
        if not self.quiet:
            click.echo(click.style("✗ ", fg="red") + message, err=True)

    def warning(self, message: str):
        """Print warning message."""
        if self._should_print():
            click.echo(click.style("⚠ ", fg="yellow") + message)

    def info(self, message: str):
        """Print info message."""
        if self._should_print():
            click.echo(click.style("ℹ ", fg="blue") + message)

    def add_json(self, data: dict):
        """Add data to JSON output buffer."""
        self.data.append(data)

    def flush_json(self):
        """Output all buffered JSON data."""
        if self.json_mode and self.data:
            click.echo(json.dumps(self.data, indent=2, default=str))

output = OutputFormatter(json_mode=False, quiet=False)

# =============================================================================
# CLI CONTEXT
# =============================================================================

@click.group()
@click.option("--json", "json_mode", is_flag=True, help="Output JSON for scripting")
@click.option("--quiet", is_flag=True, help="Suppress non-essential output")
@click.option("--verbose", "-v", is_flag=True, help="Enable debug logging")
@click.pass_context
def cli(ctx, json_mode, quiet, verbose):
    """Open Notebook CLI - Manage notebooks, sources, notes, and insights."""
    # Initialize output formatter
    global output
    output = OutputFormatter(json_mode=json_mode, quiet=quiet)

    # Suppress script-level prints when --json or --quiet
    if json_mode or quiet:
        notebook_management._quiet = True
        source_ingestion._quiet = True
        chat_interaction._quiet = True
        source_chat_mod._quiet = True

    # Setup logging
    setup_logging(verbose, quiet)

    # Log configuration (without exposing credentials)
    logging.debug(f"JSON mode: {json_mode}")
    logging.debug(f"Quiet: {quiet}")
    logging.debug(f"Verbose: {verbose}")

# Register callback to flush JSON after every command
@cli.result_callback()
def flush_json_result(result, **kwargs):
    """Flush JSON output after command completion."""
    output.flush_json()

# =============================================================================
# NOTEBOOK COMMANDS
# =============================================================================

@cli.group()
def notebook():
    """Manage notebooks."""
    pass

@notebook.command()
@click.argument("name")
@click.option("--description", "-d", default="", help="Notebook description")
@click.option("--dry-run", is_flag=True, help="Show what would be created without creating")
def create(name, description, dry_run):
    """Create a new notebook."""
    try:
        if dry_run:
            output.info(f"Would create notebook: {name}")
            return

        result = notebook_management.create_notebook(name, description)
        output.success(f"Created notebook: {result['id']} - {result['name']}")
        output.add_json({"type": "notebook", "action": "create", "data": result})
    except Exception as e:
        output.error(f"Failed to create notebook: {e}")
        sys.exit(1)

@notebook.command()
@click.option("--archived", is_flag=True, help="Show archived notebooks")
def list(archived):
    """List all notebooks."""
    try:
        notebooks = notebook_management.list_notebooks(archived=archived)
        output.add_json({"type": "notebook", "action": "list", "data": notebooks})
    except Exception as e:
        output.error(f"Failed to list notebooks: {e}")
        sys.exit(1)

@notebook.command()
@click.argument("notebook_id")
def get(notebook_id):
    """Get a notebook by ID."""
    try:
        result = notebook_management.get_notebook(notebook_id)
        output.echo(f"Notebook: {result['id']} - {result['name']}")
        output.echo(f"  Description: {result.get('description', 'N/A')}")
        output.echo(f"  Sources: {result.get('source_count', 0)}")
        output.echo(f"  Notes: {result.get('note_count', 0)}")
        output.add_json({"type": "notebook", "action": "get", "data": result})
    except Exception as e:
        output.error(f"Failed to get notebook: {e}")
        sys.exit(1)

@notebook.command()
@click.argument("notebook_id")
@click.option("--name", "-n", help="New name")
@click.option("--description", "-d", help="New description")
@click.option("--archive/--unarchive", default=None, help="Archive status")
def update(notebook_id, name, description, archive):
    """Update a notebook."""
    try:
        result = notebook_management.update_notebook(
            notebook_id, name=name, description=description, archived=archive
        )
        output.success(f"Updated notebook: {result['id']} - {result['name']}")
        output.add_json({"type": "notebook", "action": "update", "data": result})
    except Exception as e:
        output.error(f"Failed to update notebook: {e}")
        sys.exit(1)

@notebook.command()
@click.argument("notebook_id")
@click.option("--delete-sources", is_flag=True, help="Also delete sources")
@click.option("--yes", is_flag=True, help="Skip confirmation prompt")
def delete(notebook_id, delete_sources, yes):
    """Delete a notebook."""
    try:
        if not yes:
            msg = f"Delete notebook {notebook_id}?"
            if delete_sources:
                msg += " (and all sources)"
            if not click.confirm(msg):
                output.info("Cancelled")
                return

        notebook_management.delete_notebook(notebook_id, delete_sources=delete_sources)
        output.success(f"Deleted notebook: {notebook_id}")
    except Exception as e:
        output.error(f"Failed to delete notebook: {e}")
        sys.exit(1)

# =============================================================================
# SOURCE COMMANDS
# =============================================================================

@cli.group()
def source():
    """Manage sources."""
    pass

@source.command()
@click.argument("notebook_id")
@click.argument("url")
@click.option("--wait", "-w", is_flag=True, help="Wait for processing to complete")
@click.option("--poll-interval", default=5, help="Seconds between status checks")
@click.option("--timeout", default=300, help="Maximum seconds to wait")
@click.option("--embed/--no-embed", default=True, help="Embed source for vector search (default: yes)")
def add_url(notebook_id, url, wait, poll_interval, timeout, embed):
    """Add a URL source to a notebook."""
    try:
        result = source_ingestion.add_url_source(notebook_id, url, embed=embed)
        output.success(f"Added URL source: {result['id']}")
        output.add_json({"type": "source", "action": "add_url", "data": result})

        if wait:
            output.info("Waiting for processing...")
            source_ingestion.wait_for_processing(result['id'], poll_interval=poll_interval, timeout=timeout)
            output.success("Processing complete")
    except Exception as e:
        output.error(f"Failed to add URL source: {e}")
        sys.exit(1)

@source.command()
@click.argument("notebook_id")
@click.argument("title")
@click.argument("text")
@click.option("--embed/--no-embed", default=True, help="Embed source for vector search (default: yes)")
def add_text(notebook_id, title, text, embed):
    """Add a text source to a notebook."""
    try:
        result = source_ingestion.add_text_source(notebook_id, title, text, embed=embed)
        output.success(f"Added text source: {result['id']}")
        output.add_json({"type": "source", "action": "add_text", "data": result})
    except Exception as e:
        output.error(f"Failed to add text source: {e}")
        sys.exit(1)

@source.command()
@click.argument("notebook_id")
@click.argument("file_path", type=click.Path(exists=True, readable=True))
@click.option("--wait", "-w", is_flag=True, help="Wait for processing to complete")
@click.option("--embed/--no-embed", default=True, help="Embed source for vector search (default: yes)")
def upload(notebook_id, file_path, wait, embed):
    """Upload a file as a source."""
    try:
        result = source_ingestion.upload_file_source(notebook_id, file_path, embed=embed)
        output.success(f"Uploaded file source: {result['id']}")
        output.add_json({"type": "source", "action": "upload", "data": result})

        if wait:
            output.info("Waiting for processing...")
            source_ingestion.wait_for_processing(result['id'])
            output.success("Processing complete")
    except Exception as e:
        output.error(f"Failed to upload file: {e}")
        sys.exit(1)

@source.command()
@click.argument("notebook_id", required=False)
@click.option("--limit", "-l", default=20, help="Maximum number of sources")
def list(notebook_id, limit):
    """List sources."""
    try:
        sources = source_ingestion.list_sources(notebook_id=notebook_id, limit=limit)
        output.add_json({"type": "source", "action": "list", "data": sources})
    except Exception as e:
        output.error(f"Failed to list sources: {e}")
        sys.exit(1)

@source.command()
@click.argument("source_id")
def status(source_id):
    """Check source processing status."""
    try:
        result = source_ingestion.wait_for_processing(source_id, poll_interval=0, timeout=0)
        if result:
            output.echo(f"Source {source_id}: {result.get('status', 'unknown')}")
            output.add_json({"type": "source", "action": "status", "data": result})
        else:
            output.warning(f"Source {source_id}: still processing")
    except Exception as e:
        output.error(f"Failed to check status: {e}")
        sys.exit(1)

@source.command()
@click.argument("source_id")
@click.option("--yes", is_flag=True, help="Skip confirmation prompt")
def delete(source_id, yes):
    """Delete a source."""
    try:
        if not yes:
            if not click.confirm(f"Delete source {source_id}?"):
                output.info("Cancelled")
                return

        source_ingestion.delete_source(source_id)
        output.success(f"Deleted source: {source_id}")
    except Exception as e:
        output.error(f"Failed to delete source: {e}")
        sys.exit(1)

@source.command()
@click.argument("source_id")
@click.option("--async", "async_processing", is_flag=True, help="Process asynchronously")
def embed(source_id, async_processing):
    """Embed an existing source for vector search."""
    try:
        result = source_ingestion.embed_source(source_id, async_processing=async_processing)
        output.success(f"Embedding source: {result.get('message', 'Done')}")
        output.add_json({"type": "source", "action": "embed", "data": result})
    except Exception as e:
        output.error(f"Failed to embed source: {e}")
        sys.exit(1)

@source.command()
@click.argument("source_id")
def get(source_id):
    """Get a single source with full details."""
    try:
        result = source_ingestion.get_source(source_id)
        output.echo(f"Source: {result['id']}")
        output.echo(f"Title: {result.get('title', 'N/A')}")
        output.echo(f"Status: {result.get('status', 'N/A')}")
        output.echo(f"Insights: {result.get('insights_count', 0)}")
        output.add_json({"type": "source", "action": "get", "data": result})
    except Exception as e:
        output.error(f"Failed to get source: {e}")
        sys.exit(1)

# =============================================================================
# NOTE COMMANDS
# =============================================================================

@cli.group()
def note():
    """Manage notes."""
    pass

@note.command()
@click.argument("notebook_id")
@click.argument("content")
@click.option("--title", "-t", help="Note title")
@click.option("--type", "note_type", default="human", type=click.Choice(["human", "ai"]))
def create(notebook_id, content, title, note_type):
    """Create a note in a notebook."""
    try:
        result = notebook_management.create_note(notebook_id, content, title=title, note_type=note_type)
        output.success(f"Created note: {result['id']}")
        output.add_json({"type": "note", "action": "create", "data": result})
    except Exception as e:
        output.error(f"Failed to create note: {e}")
        sys.exit(1)

@note.command()
@click.argument("notebook_id", required=False)
@click.option("--limit", "-l", default=20, help="Maximum number of notes")
def list(notebook_id, limit):
    """List notes."""
    try:
        notes = notebook_management.list_notes(notebook_id=notebook_id, limit=limit)
        output.add_json({"type": "note", "action": "list", "data": notes})
    except Exception as e:
        output.error(f"Failed to list notes: {e}")
        sys.exit(1)

@note.command()
@click.argument("note_id")
def get(note_id):
    """Get a note by ID."""
    try:
        result = notebook_management.get_note(note_id)
        if result:
            output.echo(f"Note: {result['id']} - {result.get('title', 'Untitled')}")
            output.echo(f"  Type: {result.get('note_type', 'unknown')}")
            output.echo(f"  Content: {result.get('content', '')[:200]}...")
            output.add_json({"type": "note", "action": "get", "data": result})
        else:
            output.warning(f"Note not found: {note_id}")
    except Exception as e:
        output.error(f"Failed to get note: {e}")
        sys.exit(1)

@note.command()
@click.argument("note_id")
@click.option("--title", "-t", help="New title")
@click.option("--content", "-c", help="New content")
@click.option("--type", "note_type", type=click.Choice(["human", "ai"]))
def update(note_id, title, content, note_type):
    """Update a note."""
    try:
        result = notebook_management.update_note(note_id, title=title, content=content, note_type=note_type)
        output.success(f"Updated note: {result['id']}")
        output.add_json({"type": "note", "action": "update", "data": result})
    except Exception as e:
        output.error(f"Failed to update note: {e}")
        sys.exit(1)

@note.command()
@click.argument("note_id")
@click.option("--yes", is_flag=True, help="Skip confirmation prompt")
def delete(note_id, yes):
    """Delete a note."""
    try:
        if not yes:
            if not click.confirm(f"Delete note {note_id}?"):
                output.info("Cancelled")
                return

        notebook_management.delete_note(note_id)
        output.success(f"Deleted note: {note_id}")
    except Exception as e:
        output.error(f"Failed to delete note: {e}")
        sys.exit(1)

# =============================================================================
# CHAT COMMANDS
# =============================================================================

@cli.group()
def chat():
    """Manage chat sessions."""
    pass

@chat.command()
@click.argument("notebook_id")
@click.argument("title")
@click.option("--model", "-m", help="Model override")
def create(notebook_id, title, model):
    """Create a chat session."""
    try:
        result = chat_interaction.create_chat_session(notebook_id, title, model_override=model)
        output.success(f"Created chat session: {result['id']}")
        output.add_json({"type": "chat", "action": "create", "data": result})
    except Exception as e:
        output.error(f"Failed to create chat session: {e}")
        sys.exit(1)

@chat.command()
@click.argument("session_id")
@click.argument("message")
@click.option("--no-sources", is_flag=True, help="Exclude sources from context")
@click.option("--no-notes", is_flag=True, help="Exclude notes from context")
@click.option("--model", "-m", help="Model override")
def send(session_id, message, no_sources, no_notes, model):
    """Send a message to a chat session."""
    try:
        result = chat_interaction.send_chat_message(
            session_id, message,
            include_sources=not no_sources,
            include_notes=not no_notes,
            model_override=model
        )
        output.echo(f"\nAI: {result.get('response', result)}")
        output.add_json({"type": "chat", "action": "send", "data": result})
    except Exception as e:
        output.error(f"Failed to send message: {e}")
        sys.exit(1)

@chat.command()
@click.argument("notebook_id")
def list(notebook_id):
    """List chat sessions for a notebook."""
    try:
        sessions = chat_interaction.list_chat_sessions(notebook_id)
        output.add_json({"type": "chat", "action": "list", "data": sessions})
    except Exception as e:
        output.error(f"Failed to list chat sessions: {e}")
        sys.exit(1)

@chat.command()
@click.argument("session_id")
def history(session_id):
    """Get chat session history."""
    try:
        session = chat_interaction.get_session_history(session_id)
        output.add_json({"type": "chat", "action": "history", "data": session})
    except Exception as e:
        output.error(f"Failed to get chat history: {e}")
        sys.exit(1)

@chat.command()
@click.argument("session_id")
def get(session_id):
    """Get chat session with full messages."""
    try:
        session = chat_interaction.get_session_history(session_id)
        output.add_json({"type": "chat", "action": "get", "data": session})
    except Exception as e:
        output.error(f"Failed to get chat session: {e}")
        sys.exit(1)

@chat.command()
@click.argument("session_id")
@click.option("--yes", is_flag=True, help="Skip confirmation prompt")
def delete(session_id, yes):
    """Delete a chat session."""
    try:
        if not yes:
            if not click.confirm(f"Delete chat session {session_id}?"):
                output.info("Cancelled")
                return

        chat_interaction.delete_chat_session(session_id)
        output.success(f"Deleted chat session: {session_id}")
    except Exception as e:
        output.error(f"Failed to delete chat session: {e}")
        sys.exit(1)

@chat.command()
@click.argument("query")
def ask(query):
    """Ask a question to the knowledge base."""
    try:
        result = chat_interaction.ask_question(query)
        output.add_json({"type": "chat", "action": "ask", "data": result})
    except Exception as e:
        output.error(f"Failed to ask question: {e}")
        sys.exit(1)

# =============================================================================
# SOURCE CHAT COMMANDS
# =============================================================================

@cli.group()
def source_chat():
    """Source-specific chat - focused conversation on a single source."""
    pass

@source_chat.command()
@click.argument("source_id")
@click.argument("title", required=False)
@click.option("--model", "-m", help="Model override")
def create(source_id, title, model):
    """Create a chat session focused on a single source."""
    try:
        result = source_chat_mod.create_source_chat_session(source_id, title=title, model_override=model)
        output.success(f"Created source chat session: {result['id']}")
        output.add_json({"type": "source_chat", "action": "create", "data": result})
    except Exception as e:
        output.error(f"Failed to create source chat session: {e}")
        sys.exit(1)

@source_chat.command()
@click.argument("source_id")
def list(source_id):
    """List source chat sessions."""
    try:
        # lazy import removed — source_chat now imported at module level
        sessions = source_chat_mod.list_source_chat_sessions(source_id)
        output.add_json({"type": "source_chat", "action": "list", "data": sessions})
    except Exception as e:
        output.error(f"Failed to list source chat sessions: {e}")
        sys.exit(1)

@source_chat.command()
@click.argument("source_id")
@click.argument("session_id")
def history(source_id, session_id):
    """Get source chat session history."""
    try:
        session = source_chat_mod.get_source_chat_session(source_id, session_id)
        output.add_json({"type": "source_chat", "action": "history", "data": session})
    except Exception as e:
        output.error(f"Failed to get source chat history: {e}")
        sys.exit(1)

@source_chat.command()
@click.argument("source_id")
@click.argument("session_id")
def get(source_id, session_id):
    """Get source chat session with full messages."""
    try:
        session = source_chat_mod.get_source_chat_session(source_id, session_id)
        output.add_json({"type": "source_chat", "action": "get", "data": session})
    except Exception as e:
        output.error(f"Failed to get source chat session: {e}")
        sys.exit(1)

@source_chat.command()
@click.argument("source_id")
@click.argument("session_id")
@click.argument("message")
@click.option("--model", "-m", help="Model override")
def send(source_id, session_id, message, model):
    """Send a message to a source chat session."""
    try:
        result = source_chat_mod.send_source_chat_message(source_id, session_id, message, model_override=model)
        output.add_json({"type": "source_chat", "action": "send", "data": result})
    except Exception as e:
        output.error(f"Failed to send message: {e}")
        sys.exit(1)

@source_chat.command()
@click.argument("source_id")
@click.argument("session_id")
@click.option("--yes", is_flag=True, help="Skip confirmation prompt")
def delete(source_id, session_id, yes):
    """Delete a source chat session."""
    try:
        if not yes:
            if not click.confirm(f"Delete source chat session {session_id}?"):
                output.info("Cancelled")
                return

        # lazy import removed — source_chat now imported at module level
        source_chat_mod.delete_source_chat_session(source_id, session_id)
        output.success(f"Deleted source chat session: {session_id}")
    except Exception as e:
        output.error(f"Failed to delete source chat session: {e}")
        sys.exit(1)

# =============================================================================
# TRANSFORMATION COMMANDS
# =============================================================================

@cli.group()
def transformation():
    """Manage transformations."""
    pass

@transformation.command()
def list():
    """List all transformations."""
    try:
        transformations = source_ingestion.list_transformations()
        output.add_json({"type": "transformation", "action": "list", "data": transformations})
    except Exception as e:
        output.error(f"Failed to list transformations: {e}")
        sys.exit(1)

@transformation.command()
@click.argument("transformation_id")
def get(transformation_id):
    """Get a single transformation with full details."""
    try:
        result = source_ingestion.get_transformation(transformation_id)
        output.echo(f"Transformation: {result['id']}")
        output.echo(f"Name: {result.get('name', 'N/A')}")
        output.echo(f"Prompt: {result.get('prompt', 'N/A')}")
        output.add_json({"type": "transformation", "action": "get", "data": result})
    except Exception as e:
        output.error(f"Failed to get transformation: {e}")
        sys.exit(1)

@transformation.command()
@click.argument("name")
@click.argument("title")
@click.argument("description")
@click.argument("prompt")
@click.option("--apply-default", is_flag=True, help="Apply by default")
def create(name, title, description, prompt, apply_default):
    """Create a transformation."""
    try:
        result = source_ingestion.create_transformation(name, title, description, prompt, apply_default)
        output.success(f"Created transformation: {result['id']}")
        output.add_json({"type": "transformation", "action": "create", "data": result})
    except Exception as e:
        output.error(f"Failed to create transformation: {e}")
        sys.exit(1)

@transformation.command()
@click.argument("transformation_id")
@click.argument("input_text")
@click.option("--model", "-m", required=True, help="Model ID")
def execute(transformation_id, input_text, model):
    """Execute a transformation on text."""
    try:
        result = source_ingestion.execute_transformation(transformation_id, input_text, model)
        output.echo(f"Result:\n{result.get('output', result)}")
        output.add_json({"type": "transformation", "action": "execute", "data": result})
    except Exception as e:
        output.error(f"Failed to execute transformation: {e}")
        sys.exit(1)

# =============================================================================
# INSIGHT COMMANDS
# =============================================================================

@cli.group()
def insight():
    """Manage insights."""
    pass

@insight.command()
@click.argument("source_id")
def list(source_id):
    """List insights for a source."""
    try:
        insights = source_ingestion.get_source_insights(source_id)
        output.echo(f"Found {len(insights)} insight(s):")
        for insight in insights:
            output.echo(f"  - {insight['id']}: {insight.get('title', 'Untitled')}")
        output.add_json({"type": "insight", "action": "list", "data": insights})
    except Exception as e:
        output.error(f"Failed to list insights: {e}")
        sys.exit(1)

@insight.command()
@click.argument("source_id")
@click.argument("insight_id")
def get(source_id, insight_id):
    """Get a single insight with full content."""
    try:
        insight = source_ingestion.get_insight(source_id, insight_id)
        output.echo(f"Insight: {insight['id']}")
        output.echo(f"Type: {insight.get('insight_type', 'N/A')}")
        output.echo(f"Content: {insight.get('content', 'N/A')}")
        output.add_json({"type": "insight", "action": "get", "data": insight})
    except Exception as e:
        output.error(f"Failed to get insight: {e}")
        sys.exit(1)

@insight.command()
@click.argument("source_id")
@click.argument("transformation_id")
@click.option("--model", "-m", help="Model ID")
@click.option("--wait", "-w", is_flag=True, help="Wait for completion")
@click.option("--poll-interval", default=5, help="Seconds between status checks")
@click.option("--timeout", default=300, help="Maximum seconds to wait")
def create(source_id, transformation_id, model, wait, poll_interval, timeout):
    """Create an insight for a source."""
    try:
        result = source_ingestion.create_source_insight(
            source_id, transformation_id,
            model_id=model,
            poll_interval=poll_interval if wait else 0,
            timeout=timeout if wait else 0
        )
        output.success(f"Created insight: {result.get('id', 'N/A')}")
        output.add_json({"type": "insight", "action": "create", "data": result})
    except Exception as e:
        output.error(f"Failed to create insight: {e}")
        sys.exit(1)

@insight.command()
@click.argument("insight_id")
@click.argument("notebook_id")
def save(insight_id, notebook_id):
    """Save an insight as a note."""
    try:
        result = source_ingestion.save_insight_as_note(insight_id, notebook_id)
        output.success(f"Saved insight as note: {result['id']}")
        output.add_json({"type": "insight", "action": "save", "data": result})
    except Exception as e:
        output.error(f"Failed to save insight: {e}")
        sys.exit(1)

# =============================================================================
# EMBEDDINGS COMMANDS
# =============================================================================

@cli.group()
def embeddings():
    """Manage embeddings for vector search."""
    pass

@embeddings.command()
@click.option("--mode", "-m", default="existing", type=click.Choice(["existing", "all"]), help="Rebuild scope")
@click.option("--include-sources/--no-sources", default=True, help="Include sources")
@click.option("--include-notes/--no-notes", default=True, help="Include notes")
@click.option("--include-insights/--no-insights", default=True, help="Include insights")
def rebuild(mode, include_sources, include_notes, include_insights):
    """Rebuild all embeddings in the background."""
    try:
        result = source_ingestion.rebuild_embeddings(
            mode=mode,
            include_sources=include_sources,
            include_notes=include_notes,
            include_insights=include_insights,
        )
        output.success(f"Rebuild started: {result.get('command_id', 'N/A')}")
        output.add_json({"type": "embeddings", "action": "rebuild", "data": result})
    except Exception as e:
        output.error(f"Failed to rebuild embeddings: {e}")
        sys.exit(1)

@embeddings.command()
@click.argument("command_id")
def status(command_id):
    """Check the status of a rebuild operation."""
    try:
        result = source_ingestion.get_rebuild_status(command_id)
        output.echo(f"Status: {result.get('status', 'unknown')}")
        progress = result.get('progress', {})
        output.echo(f"Progress: {progress.get('processed', 0)} / {progress.get('total', 0)} ({progress.get('percentage', 0):.1f}%)")
        output.add_json({"type": "embeddings", "action": "status", "data": result})
    except Exception as e:
        output.error(f"Failed to get rebuild status: {e}")
        sys.exit(1)

# =============================================================================
# SEARCH COMMANDS
# =============================================================================

@cli.group()
def search():
    """Search the knowledge base."""
    pass

@search.command()
@click.argument("query")
@click.option("--type", "-t", default="vector", type=click.Choice(["vector", "fulltext"]), help="Search type")
@click.option("--limit", "-l", default=5, help="Maximum results")
def query(query, type, limit):
    """Search the knowledge base."""
    try:
        result = chat_interaction.search_knowledge_base(query, search_type=type, limit=limit)
        output.echo(f"Found {result.get('total', 0)} result(s):")
        for r in result.get("results", []):
            output.echo(f"  - {r.get('title', 'Untitled')} (similarity: {r.get('similarity', 'N/A')})")
        output.add_json({"type": "search", "action": "query", "data": result})
    except Exception as e:
        output.error(f"Failed to search: {e}")
        sys.exit(1)

@search.command()
@click.argument("query")
def ask(query):
    """Ask a question and get an answer."""
    try:
        result = chat_interaction.ask_question(query)
        output.add_json({"type": "search", "action": "ask", "data": result})
    except Exception as e:
        output.error(f"Failed to ask question: {e}")
        sys.exit(1)

# =============================================================================
# WORKFLOW COMMAND
# =============================================================================

@cli.group()
def workflow():
    """Run complete workflows."""
    pass

@workflow.command()
@click.option("--name", "-n", required=True, help="Notebook name")
@click.option("--description", "-d", default="", help="Notebook description")
@click.option("--url", "-u", help="URL to add as source")
@click.option("--file", "-f", type=click.Path(exists=True, readable=True), help="File to upload")
@click.option("--text-title", "-t", help="Text source title")
@click.option("--text-content", "-c", help="Text source content")
@click.option("--wait", "-w", is_flag=True, help="Wait for processing")
@click.option("--poll-interval", default=5, help="Seconds between status checks")
@click.option("--timeout", default=300, help="Maximum seconds to wait")
@click.option("--insight", "-i", is_flag=True, help="Generate insights")
@click.option("--search", "-s", help="Search query after workflow")
@click.option("--dry-run", is_flag=True, help="Show what would be done without doing it")
def complete(name, description, url, file, text_title, text_content, wait, poll_interval, timeout, insight, search, dry_run):
    """Run a complete workflow: create notebook, add sources, optionally generate insights."""
    try:
        if dry_run:
            output.info("Dry run mode - no changes will be made")
            output.info(f"Would create notebook: {name}")
            if url: output.info(f"Would add URL: {url}")
            if file: output.info(f"Would upload file: {file}")
            if text_title: output.info(f"Would add text: {text_title}")
            return

        # Create notebook
        notebook = notebook_management.create_notebook(name, description)
        notebook_id = notebook["id"]
        output.success(f"Created notebook: {notebook_id}")

        sources = []

        # Add URL
        if url:
            source = source_ingestion.add_url_source(notebook_id, url)
            sources.append(source["id"])
            output.success(f"Added URL source: {source['id']}")

        # Upload file
        if file:
            source = source_ingestion.upload_file_source(notebook_id, file)
            sources.append(source["id"])
            output.success(f"Uploaded file source: {source['id']}")

        # Add text
        if text_title and text_content:
            source = source_ingestion.add_text_source(notebook_id, text_title, text_content)
            sources.append(source["id"])
            output.success(f"Added text source: {source['id']}")

        # Wait for processing
        if wait and sources:
            output.info("Waiting for processing...")
            for source_id in sources:
                source_ingestion.wait_for_processing(source_id, poll_interval=poll_interval, timeout=timeout)
            output.success("All sources processed")

        # Generate insights
        if insight:
            output.info("Generating insights...")
            transformations = source_ingestion.list_transformations()
            if transformations:
                for source_id in sources:
                    for transformation in transformations[:3]:
                        try:
                            result = source_ingestion.create_source_insight(source_id, transformation["id"])
                            output.success(f"Generated insight: {result.get('id', 'N/A')}")
                        except Exception as e:
                            output.warning(f"Error with transformation {transformation['id']}: {e}")

        # Search
        if search:
            output.info(f"Searching: {search}")
            result = chat_interaction.search_knowledge_base(search)
            output.echo(f"Found {result.get('total', 0)} results")

        output.success(f"Workflow complete! Notebook ID: {notebook_id}")
        output.add_json({"type": "workflow", "action": "complete", "notebook_id": notebook_id})

    except Exception as e:
        output.error(f"Workflow failed: {e}")
        sys.exit(1)

# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    cli()
