#!/usr/bin/env python3
import os
import re
from pathlib import Path
from bs4 import BeautifulSoup
import datetime

def html_to_md(html_content):
    """Simple HTML to markdown converter for blog posts."""
    # Convert basic tags
    md_content = html_content
    md_content = re.sub(r'<p>(.*?)</p>', r'\1\n\n', md_content)
    md_content = re.sub(r'<strong>(.*?)</strong>', r'**\1**', md_content)
    md_content = re.sub(r'<em>(.*?)</em>', r'*\1*', md_content)
    md_content = re.sub(r'<h2>(.*?)</h2>', r'## \1\n\n', md_content)
    md_content = re.sub(r'<h3>(.*?)</h3>', r'### \1\n\n', md_content)
    md_content = re.sub(r'<a href="(.*?)">(.*?)</a>', r'[\2](\1)', md_content)
    md_content = re.sub(r'<ul>(.*?)</ul>', r'\1', md_content, flags=re.DOTALL)
    md_content = re.sub(r'<li>(.*?)</li>', r'- \1\n', md_content)
    md_content = re.sub(r'<blockquote>(.*?)</blockquote>', r'> \1\n\n', md_content, flags=re.DOTALL)
    md_content = re.sub(r'<br/?>', r'\n', md_content)
    
    # Remove any remaining HTML tags
    md_content = re.sub(r'<[^>]+>', '', md_content)
    
    # Fix double spacing
    md_content = re.sub(r'\n\s*\n\s*\n', '\n\n', md_content)
    
    return md_content.strip()

def create_missing_md_files():
    """Find blog posts without corresponding markdown files and create them."""
    root_dir = Path(__file__).parent.resolve()
    blog_dir = root_dir / "blog"
    published_dir = root_dir / "SamarthBlog" / "published"
    
    # Ensure the published directory exists
    published_dir.mkdir(exist_ok=True, parents=True)
    
    # Get all HTML files in blog directory
    html_files = list(blog_dir.glob("*.html"))
    
    # Get all existing markdown files
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
    
    # Check each HTML file
    created_count = 0
    for html_file in html_files:
        html_slug = html_file.stem
        
        # Skip if it already has a markdown file
        if html_slug in md_slugs:
            continue
            
        # Skip date-prefixed files if their slug part is in md_slugs
        parts = html_slug.split("-", 3)
        if len(parts) >= 4 and parts[0].isdigit() and parts[1].isdigit() and parts[2].isdigit():
            slug = parts[3]
            if slug in md_slugs:
                continue
        
        print(f"Creating markdown for: {html_file.name}")
        
        # Read HTML content
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract title
        title_elem = soup.select_one('.post-title')
        title = title_elem.get_text().strip() if title_elem else html_slug.replace('-', ' ').title()
        
        # Extract date
        date_elem = soup.select_one('.post-meta')
        date_text = date_elem.get_text().strip() if date_elem else None
        
        if date_text:
            # Try to parse the date
            try:
                # Different date formats to try
                date_formats = [
                    "%d %B, %Y",
                    "%B %d, %Y",
                    "%d %B %Y"
                ]
                
                parsed_date = None
                for date_format in date_formats:
                    try:
                        parsed_date = datetime.datetime.strptime(date_text, date_format)
                        break
                    except ValueError:
                        continue
                
                if parsed_date:
                    date_str = parsed_date.strftime("%d %B, %Y")
                    file_date_prefix = parsed_date.strftime("%Y-%m-%d")
                else:
                    date_str = datetime.datetime.now().strftime("%d %B, %Y")
                    file_date_prefix = datetime.datetime.now().strftime("%Y-%m-%d")
            except Exception:
                date_str = datetime.datetime.now().strftime("%d %B, %Y")
                file_date_prefix = datetime.datetime.now().strftime("%Y-%m-%d")
        else:
            date_str = datetime.datetime.now().strftime("%d %B, %Y")
            file_date_prefix = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # Extract content
        content_elem = soup.select_one('.post-content')
        if content_elem:
            content_html = ''.join(str(tag) for tag in content_elem.contents)
            content = html_to_md(content_html)
        else:
            content = "Original content couldn't be extracted. Please edit this content."
        
        # Create a clean slug from the title if needed
        if not html_slug or html_slug == 'index':
            slug = re.sub(r'[^\w\-]', '', title.lower().replace(' ', '-'))
        else:
            slug = html_slug
        
        # Create frontmatter
        frontmatter = f"""---
title: "{title}"
date_published: "{date_str}"
author: "Samarth Bansal"
slug: "{slug}"
tags: []
---

{content}
"""
        
        # Determine the output filename with date prefix
        output_filename = f"{file_date_prefix}-{slug}.md"
        output_path = published_dir / output_filename
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(frontmatter)
        
        print(f"Created markdown file: {output_path}")
        created_count += 1
    
    print(f"\nCreated {created_count} markdown files for existing blog posts.")

if __name__ == "__main__":
    create_missing_md_files()