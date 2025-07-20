#!/usr/bin/env python3

import csv
import os
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

def parse_date(date_str):
    """Parse date string and return formatted date."""
    if not date_str or date_str.strip() == '':
        return ''
    
    try:
        # Try to parse the date
        date_obj = datetime.strptime(date_str, '%B %d, %Y')
        return date_obj.strftime('%b %Y')
    except ValueError:
        # If parsing fails, return the original string
        return date_str

def load_journalism_data(csv_path):
    """Load journalism articles from CSV file."""
    articles = []
    
    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Skip empty rows
            if not row.get('title', '').strip():
                continue
                
            article = {
                'title': (row.get('title') or '').strip(),
                'publication': (row.get('publication') or '').strip(),
                'date': parse_date((row.get('date') or '').strip()),
                'original_url': (row.get('original_url') or '').strip(),
                'excerpt': (row.get('excerpt') or '').strip(),
                'category': (row.get('category') or '').strip(),
                'priority': (row.get('priority') or '').strip()
            }
            
            # Only add articles with title and URL
            if article['title'] and article['original_url']:
                articles.append(article)
    
    # Sort by date (newest first) - for now just reverse the order
    # since CSV appears to be in reverse chronological order
    return articles

def generate_journalism_page():
    """Generate the journalism page from CSV data."""
    
    # Paths
    csv_path = '/Users/samarth/personal_website/samarth-blog/journalism_links.csv'
    template_path = '/Users/samarth/personal_website/samarth-blog/templates'
    output_dir = '/Users/samarth/personal_website/samarth-blog/output'
    
    # Load data
    print("Loading journalism data...")
    articles = load_journalism_data(csv_path)
    print(f"Loaded {len(articles)} articles")
    
    # Setup Jinja2
    env = Environment(loader=FileSystemLoader(template_path))
    template = env.get_template('journalism.html')
    
    # Render template
    html_content = template.render(
        journalism=articles,
        site_name="Samarth's Blog",
        description="Selected journalism work by Samarth Bansal"
    )
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Write output file
    output_path = os.path.join(output_dir, 'journalism', 'index.html')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Generated journalism page: {output_path}")
    print(f"Preview: file://{output_path}")

if __name__ == '__main__':
    generate_journalism_page()