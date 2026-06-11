#!/usr/bin/env python3
"""
Open Notebook - Complete Workflow Example

Demonstrates a complete workflow:
1. Create a notebook
2. Add a source
3. Wait for processing
4. Generate insights
5. Save insights as notes
6. Search knowledge base

This is a generic example - replace the IDs with your actual values.
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.notebook_management import create_notebook, list_notebooks
from scripts.source_ingestion import (
    add_url_source,
    wait_for_processing,
    get_source_insights,
    create_source_insight,
    list_transformations,
    save_insight_as_note,
)
from scripts.chat_interaction import search_knowledge_base


def main():
    print("=== Open Notebook Complete Workflow Example ===\n")
    
    # Step 1: Create a notebook
    print("Step 1: Creating notebook...")
    notebook = create_notebook(
        name="Research Example",
        description="Demonstrating complete workflow"
    )
    notebook_id = notebook["id"]
    print(f"Created notebook: {notebook_id}\n")
    
    # Step 2: Add a source
    print("Step 2: Adding source...")
    source = add_url_source(
        notebook_id=notebook_id,
        url="https://arxiv.org/abs/2301.00001"
    )
    source_id = source["id"]
    print(f"Added source: {source_id}\n")
    
    # Step 3: Wait for processing
    print("Step 3: Waiting for source processing...")
    wait_for_processing(source_id)
    print()
    
    # Step 4: List available transformations
    print("Step 4: Available transformations:")
    transformations = list_transformations()
    print()
    
    # Step 5: Generate insights (if transformations exist)
    if transformations:
        print("Step 5: Generating insights...")
        for transformation in transformations[:3]:  # First 3 transformations
            try:
                insight = create_source_insight(
                    source_id=source_id,
                    transformation_id=transformation["id"]
                )
                print(f"  Generated insight: {insight.get('id', 'N/A')}")
            except Exception as e:
                print(f"  Error with transformation {transformation['id']}: {e}")
        print()
    
    # Step 6: Get insights and save as notes
    print("Step 6: Saving insights as notes...")
    insights = get_source_insights(source_id)
    for insight in insights[:3]:  # First 3 insights
        try:
            note = save_insight_as_note(
                insight_id=insight["id"],
                notebook_id=notebook_id
            )
            print(f"  Saved insight as note: {note['id']}")
        except Exception as e:
            print(f"  Error saving insight: {e}")
    print()
    
    # Step 7: Search knowledge base
    print("Step 7: Searching knowledge base...")
    results = search_knowledge_base("machine learning")
    print(f"Found {results.get('total', 0)} results\n")
    
    print("=== Workflow complete ===")
    print(f"Notebook ID: {notebook_id}")
    print(f"Source ID: {source_id}")
    print("\nYou can use these IDs to continue exploring the API.")


if __name__ == "__main__":
    main()
