#!/usr/bin/env python3
"""
Extract reverse engineering knowledge from Open Notebook
Uses the open-notebook skill scripts
"""
import sys
import json

# Add skill path
sys.path.insert(0, '/Users/nizarakbarmeilani/Documents/obsidian_notes/Ideaverse Lite 1.5/.claude/skills/open-notebook')

from scripts.chat_interaction import create_chat_session, send_chat_message
from scripts.notebook_management import list_notebooks

# Verify notebook
print("=== Finding Reverse Engineering Notebook ===")
notebooks = list_notebooks()
rev_eng = [nb for nb in notebooks if 'reverse' in nb['name'].lower() and 'engineering' in nb['name'].lower()]

if len(rev_eng) == 0:
    print("ERROR: No reverse engineering notebook found!")
    sys.exit(1)

if len(rev_eng) > 1:
    print(f"WARNING: Found {len(rev_eng)} notebooks with 'reverse engineering' in name:")
    for nb in rev_eng:
        print(f"  - {nb['id']}: {nb['name']}")
    print("Using the first one.")

notebook = rev_eng[0]
NOTEBOOK_ID = notebook['id']
print(f"Using notebook: {NOTEBOOK_ID} - {notebook['name']}")

# Create chat session
session = create_chat_session(NOTEBOOK_ID, "x86 Knowledge Extraction")
SESSION_ID = session['id']
print(f"Chat session: {SESSION_ID}")

# Query all topics
questions = [
    "What are the two modes of x86 processor and what are the differences between them?",
    "What are the ring levels in x86/x64 architecture and what is the usage of each ring level?",
    "How many general purpose registers (GPR) are there in x86/x64? What are the types based on bit division (8-bit, 16-bit, 32-bit, 64-bit) and what is the purpose of each register?",
    "What is the EFLAGS register and what are its key flags?",
    "What is EIP (Instruction Pointer) and what is its role?",
    "What are CR registers (CR0, CR3, CR4) and how do they relate to paging?",
    "What are MSR (Model Specific Registers) and what are they used for?",
    "What are the common data types in x86/x64 assembly (byte, word, dword, qword)?"
]

results = {}
for i, question in enumerate(questions, 1):
    print(f"\n[{i}/{len(questions)}] {question}")
    try:
        result = send_chat_message(SESSION_ID, question)
        answer = result.get('response', result)
        results[question] = answer
        print(f"Answer: {answer[:300]}...")
    except Exception as e:
        print(f"ERROR: {e}")
        results[question] = None

# Save results
output_path = '/tmp/open_notebook_reverse_eng.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n=== Results saved to {output_path} ===")
print(f"Total questions: {len(questions)}")
print(f"Successful answers: {sum(1 for v in results.values() if v is not None)}")
