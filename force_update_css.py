#!/usr/bin/env python3
import os
import glob
from pathlib import Path
from bs4 import BeautifulSoup

def update_blog_post_templates():
    """Update all blog posts to use the new template and style.css."""
    print("Starting force update process for all blog posts...")
    blog_dir = Path('blog').resolve()
    
    # Get all HTML files in the blog directory
    html_files = list(blog_dir.glob('*.html'))
    
    if not html_files:
        print("No HTML files found in the blog directory.")
        return
    
    print(f"Found {len(html_files)} HTML files. Processing...")
    
    for html_file in html_files:
        print(f"Processing {html_file.name}")
        
        try:
            # Read the current file
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse the HTML
            soup = BeautifulSoup(content, 'html.parser')
            
            # Update stylesheet link - replace mvp.css with style.css
            css_links = soup.select('link[rel="stylesheet"]')
            for link in css_links:
                if 'mvp.css' in link.get('href', ''):
                    link['href'] = link['href'].replace('mvp.css', 'style.css')
            
            # Update the overall structure to match the new template
            # First, find the main content
            article = soup.find('article')
            if article:
                title = "Untitled Post"
                date = ""
                
                # Extract the title
                h1 = article.find('h1')
                if h1:
                    title = h1.get_text().strip()
                
                # Extract the date
                date_span = article.select_one('.date')
                if date_span:
                    date = date_span.get_text().strip()
                
                # Extract the content
                hr = article.find('hr')
                if hr:
                    content_elements = []
                    for elem in hr.find_next_siblings():
                        content_elements.append(str(elem))
                    body_content = "".join(content_elements)
                else:
                    body_content = str(article)
                
                # Create new structure based on post-template.html
                new_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Samarth Bansal</title>
    <link rel="stylesheet" href="../css/style.css">
    <meta name="author" content="Samarth Bansal">
</head>
<body>
    <div class="container">
        <nav>
            <a href="/">← Home</a>
            <a href="../pages/blog.html">Blog</a>
        </nav>
        
        <article>
            <div class="post-meta">
                {date}
            </div>
            
            <h1 class="post-title">{title}</h1>
            
            <div class="post-content">
                {body_content}
            </div>
        </article>
    </div>
</body>
</html>"""
                
                # Write the updated HTML back to the file
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(new_html)
                
                print(f"  Updated {html_file.name} with new template and style.css")
            else:
                print(f"  Skipped {html_file.name} - couldn't find article section")
            
        except Exception as e:
            print(f"  ERROR with {html_file.name}: {str(e)}")
    
    print("\nAll blog posts have been updated!")

if __name__ == "__main__":
    update_blog_post_templates()