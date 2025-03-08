#!/usr/bin/env python3
import os
import sys
from datetime import datetime
from pathlib import Path
import re
import string

def create_new_post(title=None):
    """Create a new blog post with pre-filled frontmatter."""
    # Get today's date for filename and frontmatter
    today = datetime.now()
    date_str = today.strftime("%Y-%m-%d")
    date_formatted = today.strftime("%d %B, %Y")
    
    # Get the title from command line or prompt for it
    if not title:
        title = input("Enter post title: ")
    
    # Create a slug from the title
    slug = slugify(title)
    
    # The path where the post will be saved
    published_dir = Path(__file__).parent.resolve() / "SamarthBlog" / "published"
    
    # Make sure directory exists
    if not published_dir.exists():
        published_dir.mkdir(parents=True, exist_ok=True)
    
    # Create the filename with the date prefix
    filename = f"{date_str}-{slug}.md"
    file_path = published_dir / filename
    
    # Check if file already exists
    if file_path.exists():
        confirm = input(f"File {filename} already exists. Overwrite? (y/N): ")
        if confirm.lower() != 'y':
            print("Aborting...")
            return
    
    # Create frontmatter content
    frontmatter = f"""---
title: "{title}"
date_published: "{date_formatted}"
author: "Samarth Bansal"
slug: "{slug}"
tags: []
excerpt: ""
description-meta: ""
---

Write your post content here...
"""
    
    # Write the file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(frontmatter)
    
    print(f"Created new post: {file_path}")
    
    # Automatically open if we're in interactive mode
    try:
        import subprocess
        if sys.platform == 'darwin':  # macOS
            subprocess.run(['open', file_path])
        elif sys.platform == 'win32':  # Windows
            subprocess.run(['start', file_path], shell=True)
        else:  # Linux and others
            subprocess.run(['xdg-open', file_path])
        print("Opened in default editor.")
    except Exception as e:
        print(f"Couldn't open editor: {e}")

def slugify(text):
    """Convert text to a URL-friendly slug."""
    # Convert to lowercase
    text = text.lower()
    
    # Replace spaces with hyphens
    text = text.replace(' ', '-')
    
    # Remove special characters
    text = re.sub(r'[^\w\-]', '', text)
    
    # Remove multiple hyphens
    text = re.sub(r'-+', '-', text)
    
    # Trim hyphens from the start and end
    text = text.strip('-')
    
    return text

if __name__ == "__main__":
    # Get title from command line if provided
    title = None
    if len(sys.argv) > 1:
        title = ' '.join(sys.argv[1:])
    
    create_new_post(title)