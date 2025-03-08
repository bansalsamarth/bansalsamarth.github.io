#!/usr/bin/env python3
import os
import sys
from pathlib import Path
import subprocess

def create_new_page(title=None, filename=None):
    """Create a new page with the site's base design."""
    root_dir = Path(__file__).parent.resolve()
    pages_dir = root_dir / "pages"
    
    # Ensure pages directory exists
    pages_dir.mkdir(exist_ok=True)
    
    # Get title from command line or prompt
    if not title:
        title = input("Enter page title: ")
    
    # Get filename from command line or prompt or generate from title
    if not filename:
        suggested_filename = title.lower().replace(' ', '-')
        filename = input(f"Enter filename (default: {suggested_filename}.html): ")
        if not filename:
            filename = f"{suggested_filename}.html"
        if not filename.endswith('.html'):
            filename += '.html'
    
    # Full path to the new file
    file_path = pages_dir / filename
    
    # Confirm if file exists
    if file_path.exists():
        confirm = input(f"File {filename} already exists. Overwrite? (y/N): ")
        if confirm.lower() != 'y':
            print("Aborting...")
            return
    
    # Create the HTML content using the base template
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} · Samarth Bansal</title>
    <link rel="stylesheet" href="../css/style.css">
    <meta name="description" content="Personal website of Samarth Bansal">
</head>
<body>
    <div class="container">
        <nav>
            <a href="/">← Home</a>
            <a href="../pages/blog.html">Blog</a>
        </nav>
        
        <h1 class="page-title">{title}</h1>
        
        <div class="page-content">
            <!-- Your content goes here -->
            <p>This is a new page. Replace this with your content.</p>
        </div>
    </div>
</body>
</html>"""
    
    # Write the file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Created new page: {file_path}")
    
    # Open in default editor
    try:
        if sys.platform == 'darwin':  # macOS
            subprocess.run(['open', file_path])
        elif sys.platform == 'win32':  # Windows
            subprocess.run(['start', file_path], shell=True)
        else:  # Linux and others
            subprocess.run(['xdg-open', file_path])
        print("Opened in default editor.")
    except Exception as e:
        print(f"Couldn't open editor: {e}")

if __name__ == "__main__":
    # Get title and optional filename from command line
    title = None
    filename = None
    
    if len(sys.argv) > 1:
        title = ' '.join(sys.argv[1:]) if len(sys.argv) == 2 else sys.argv[1]
        if len(sys.argv) > 2:
            filename = sys.argv[2]
    
    create_new_page(title, filename)