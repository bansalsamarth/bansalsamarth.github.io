#!/usr/bin/env python3
import os
from pathlib import Path
import sys

def sync_posts():
    """Sync blog posts by deleting HTML files that don't have corresponding markdown files."""
    root_dir = Path(__file__).parent.resolve()
    blog_dir = root_dir / "blog"
    published_dir = root_dir / "SamarthBlog" / "published"
    
    print("Syncing blog posts...")
    print("Checking for HTML files without corresponding markdown files...")
    
    # Get all markdown files in published directory
    md_files = list(published_dir.glob("*.md"))
    md_slugs = set()
    
    # Extract slugs from markdown filenames
    for md_file in md_files:
        # Handle files with date prefix (YYYY-MM-DD-slug.md)
        parts = md_file.stem.split("-", 3)
        if len(parts) >= 4 and parts[0].isdigit() and parts[1].isdigit() and parts[2].isdigit():
            slug = parts[3]
        else:
            slug = md_file.stem
        md_slugs.add(slug)
    
    # Get all HTML files in blog directory
    html_files = list(blog_dir.glob("*.html"))
    deleted_count = 0
    
    # Check each HTML file
    for html_file in html_files:
        html_slug = html_file.stem
        
        # Skip files that have a corresponding markdown file
        if html_slug in md_slugs:
            continue
        
        # Skip files with a date prefix that have their slug part in md_slugs
        parts = html_slug.split("-", 3)
        if len(parts) >= 4 and parts[0].isdigit() and parts[1].isdigit() and parts[2].isdigit():
            slug = parts[3]
            if slug in md_slugs:
                continue
        
        # Confirm deletion
        if "--force" not in sys.argv:
            confirm = input(f"Delete {html_file.name}? (y/N): ")
            if confirm.lower() != 'y':
                print(f"Skipping {html_file.name}")
                continue
        
        # Delete the file
        try:
            html_file.unlink()
            print(f"Deleted: {html_file.name}")
            deleted_count += 1
        except Exception as e:
            print(f"Error deleting {html_file.name}: {str(e)}")
    
    print(f"\nSync complete. Deleted {deleted_count} HTML files.")

if __name__ == "__main__":
    sync_posts()