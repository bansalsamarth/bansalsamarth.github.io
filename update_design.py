#!/usr/bin/env python3
import os
import glob
import re
from bs4 import BeautifulSoup

# Helper function to clean up the blog page
def fix_blog_page():
    with open('pages/blog.html', 'r') as file:
        content = file.read()
    
    # Use BeautifulSoup to fix the HTML structure
    soup = BeautifulSoup(content, 'html.parser')
    
    # Fix the chronological view to use proper h2.post-title format instead of paragraphs
    chrono_view = soup.select_one('#chronological-view')
    if chrono_view:
        post_items = chrono_view.select('.post-item')
        for item in post_items:
            # Find paragraph-based entries (these need to be fixed)
            p_tag = item.find('p')
            if p_tag and p_tag.find('a'):
                a_tag = p_tag.find('a')
                href = a_tag.get('href')
                title_text = a_tag.get_text()
                date_text = ""
                
                # Extract date if available
                date_span = item.select_one('.post-date')
                if date_span:
                    date_span_text = date_span.get_text().strip()
                
                # Create proper structure
                p_tag.decompose()  # Remove the paragraph
                
                # Create new h2.post-title structure
                h2 = soup.new_tag('h2', **{'class': 'post-title'})
                new_a = soup.new_tag('a', href=href)
                new_a.string = title_text
                h2.append(new_a)
                
                # Add the new elements to the list item
                item.append(h2)
    
    # Also fix title div structure if needed
    post_items = soup.select('.post-item')
    for item in post_items:
        title_div = item.select_one('.post-title')
        if title_div:
            # Check for broken structure (paragraph inside the h2)
            p_tag = title_div.find('p')
            if p_tag:
                # Extract href and title text
                a_tag = p_tag.find('a')
                if a_tag:
                    href = a_tag.get('href')
                    title_text = a_tag.get_text()
                    
                    # Clear the h2 content and create a proper structure
                    title_div.clear()
                    new_a = soup.new_tag('a', href=href)
                    new_a.string = title_text
                    title_div.append(new_a)
    
    # Write the fixed content back
    with open('pages/blog.html', 'w') as file:
        file.write(str(soup))
    
    print("Fixed blog page.")

# Main function to update design
def main():
    print("Updating design for all pages...")
    
    # Fix blog page
    fix_blog_page()
    
    print("Design update completed.")

if __name__ == "__main__":
    main()