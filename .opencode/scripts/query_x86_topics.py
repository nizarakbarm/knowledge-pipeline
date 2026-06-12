#!/usr/bin/env python3
"""
Query Open Notebook for detailed x86 architecture information.
Uses the open-notebook skill scripts with proper path handling.
"""

import sys
import os
import requests
import json

# Add scripts directory to path
sys.path.insert(0, '/Users/nizarakbarmeilani/Documents/obsidian_notes/Ideaverse Lite 1.5/.opencode/skills/open-notebook/scripts')

from config import get_config

config = get_config()
BASE_URL = config['api_url']
HEADERS = {
    'Authorization': f"Bearer {config['password']}",
    'Content-Type': 'application/json',
}
VERIFY_SSL = not config['insecure']
NOTEBOOK_ID = 'notebook:pbx3yl88rsd97fads8bq'

def create_chat_session(title):
    """Create a new chat session within the notebook."""
    response = requests.post(
        f"{BASE_URL}/chat/sessions",
        json={"notebook_id": NOTEBOOK_ID, "title": title},
        headers=HEADERS,
        verify=VERIFY_SSL,
    )
    response.raise_for_status()
    return response.json()

def send_chat_message(session_id, message):
    """Send a message and get response."""
    payload = {
        "session_id": session_id,
        "message": message,
        "context": {
            "include_sources": True,
            "include_notes": True,
        },
    }
    response = requests.post(
        f"{BASE_URL}/chat/execute",
        json=payload,
        headers=HEADERS,
        verify=VERIFY_SSL,
    )
    response.raise_for_status()
    return response.json()

def get_session_history(session_id):
    """Retrieve full message history."""
    response = requests.get(
        f"{BASE_URL}/chat/sessions/{session_id}",
        headers=HEADERS,
        verify=VERIFY_SSL,
    )
    response.raise_for_status()
    return response.json()

# Query topics
queries = [
    "What are the two modes of x86 processor (real mode and protected mode)? Explain the differences between them.",
    "What are the ring levels in x86 architecture (ring 0, 1, 2, 3)? What is the purpose of each ring level and how are they used in modern operating systems?",
    "What are the general purpose registers (GPR) in x86? How many are there, what are their bit divisions (8-bit, 16-bit, 32-bit), and what is the purpose of each register (EAX, EBX, ECX, EDX, ESI, EDI, EBP, ESP)?",
    "What is the EFLAGS register in x86? What is its purpose and what flags does it contain?",
    "What is the EIP register in x86? What is its purpose and how does it work?",
    "What are the control registers (CR0, CR2, CR3, CR4) used for paging in x86? Explain each one.",
    "What are Model Specific Registers (MSR) in x86? How are they accessed and what are they used for?",
    "What are the differences between x86 and x64 architecture? What are the new registers in x64 and how do they differ from x86?",
    "What are the data types in x86 architecture (byte, word, doubleword, quadword)? How many bits is each?"
]

print("=== Querying Open Notebook for x86 Architecture Details ===\n")

# Create a single session
session = create_chat_session("x86 Architecture Deep Dive")
session_id = session["id"]
print(f"Created session: {session_id}\n")

results = {}

for i, query in enumerate(queries, 1):
    print(f"Query {i}/9: {query[:80]}...")
    try:
        result = send_chat_message(session_id, query)
        # Get the full history to capture the response
        history = get_session_history(session_id)
        messages = history.get("messages", [])
        
        # Find the AI response to this query
        ai_response = None
        for msg in messages:
            if msg.get("type") == "ai" and msg.get("content", "").startswith("I'll search") == False:
                ai_response = msg.get("content", "")
        
        if ai_response:
            results[f"topic_{i}"] = {
                "query": query,
                "response": ai_response[:500]  # First 500 chars for preview
            }
            print(f"  ✓ Got response: {ai_response[:200]}...")
        else:
            print(f"  ⚠ No response found in history")
            
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")

# Save results
output_path = "/Users/nizarakbarmeilani/Documents/obsidian_notes/Ideaverse Lite 1.5/.opencode/open_notebook_x86_results.json"
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n=== Results saved to {output_path} ===")
print(f"Total topics queried: {len(results)}")
