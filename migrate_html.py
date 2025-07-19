#!/usr/bin/env python3
"""
HTML to Markdown Migration Script

This script converts HTML files to Markdown posts for the static site generator.
It extracts metadata from HTML structure and converts content to clean Markdown.

Usage:
    python migrate_html.py

The script processes all HTML files in the migrate_html/ directory and creates
corresponding Markdown files in content/posts/.
"""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

try:
    from bs4 import BeautifulSoup
    import html2text
except ImportError:
    print("Required packages not installed. Please run:")
    print("pip install beautifulsoup4 html2text")
    exit(1)

from config import Config


class HTMLMigrator:
    """
    Migrates HTML files to Markdown format for the static site generator.
    
    Handles extraction of metadata (title, date, author) and conversion of
    HTML content to clean Markdown while preserving URLs and structure.
    """
    
    def __init__(self):
        """Initialize the HTML migrator with html2text converter settings."""
        self.html_dir = Path('migrate_html')
        self.output_dir = Path(Config.POSTS_DIR)
        
        # Configure html2text for clean conversion
        self.h2t = html2text.HTML2Text()
        self.h2t.ignore_links = False
        self.h2t.ignore_emphasis = False
        self.h2t.ignore_images = False
        self.h2t.body_width = 0  # Don't wrap lines
        self.h2t.unicode_snob = True
        self.h2t.escape_snob = True
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
    
    def extract_metadata(self, soup: BeautifulSoup, filename: str) -> Dict[str, str]:
        """
        Extract metadata from HTML soup.
        
        Args:
            soup: BeautifulSoup object of the HTML file
            filename: Original filename for generating slug
            
        Returns:
            Dictionary with title, date, slug, and category metadata
        """
        metadata = {}
        
        # Extract title from <title> tag or <h1>
        title_tag = soup.find('title')
        h1_tag = soup.find('h1')
        
        if title_tag and title_tag.get_text(strip=True):
            metadata['title'] = title_tag.get_text(strip=True)
        elif h1_tag and h1_tag.get_text(strip=True):
            metadata['title'] = h1_tag.get_text(strip=True)
        else:
            # Fallback to filename
            metadata['title'] = filename.replace('-', ' ').replace('.html', '').title()
        
        # Extract date from span.date
        date_span = soup.find('span', class_='date')
        if date_span:
            date_text = date_span.get_text(strip=True)
            metadata['date'] = self.parse_date(date_text)
        else:
            # Fallback to today's date
            metadata['date'] = datetime.now().strftime('%Y-%m-%d')
            print(f"Warning: No date found in {filename}, using today's date")
        
        # Generate slug from filename (remove .html extension)
        metadata['slug'] = filename.replace('.html', '')
        
        # Auto-categorize based on content/title
        metadata['category'] = self.auto_categorize(metadata['title'])
        
        return metadata
    
    def parse_date(self, date_text: str) -> str:
        """
        Parse date from various formats to YYYY-MM-DD.
        
        Args:
            date_text: Date string from HTML
            
        Returns:
            Date in YYYY-MM-DD format
        """
        # Common formats in your HTML files
        date_formats = [
            '%d %B, %Y',      # "22 June, 2021"
            '%d %B %Y',       # "22 June 2021"
            '%B %d, %Y',      # "June 22, 2021"
            '%Y-%m-%d',       # "2021-06-22"
            '%d/%m/%Y',       # "22/06/2021"
        ]
        
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_text, fmt)
                return parsed_date.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        print(f"Warning: Could not parse date '{date_text}', using today's date")
        return datetime.now().strftime('%Y-%m-%d')
    
    def auto_categorize(self, title: str) -> str:
        """
        Auto-categorize posts based on title content.
        
        Args:
            title: Post title
            
        Returns:
            Category string
        """
        title_lower = title.lower()
        
        # Journalism keywords
        journalism_keywords = [
            'journalism', 'journalist', 'data journalism', 'freelance', 
            'reporting', 'media', 'news', 'investigation'
        ]
        
        # Personal/fitness keywords  
        personal_keywords = [
            'workout', 'fitness', 'personal', 'streak', 'lessons',
            'thoughts', 'observations', 'experience'
        ]
        
        # Tech keywords
        tech_keywords = [
            'data', 'programming', 'technology', 'code', 'development'
        ]
        
        for keyword in journalism_keywords:
            if keyword in title_lower:
                return 'journalism'
        
        for keyword in personal_keywords:
            if keyword in title_lower:
                return 'personal'
                
        for keyword in tech_keywords:
            if keyword in title_lower:
                return 'tech'
        
        return 'uncategorized'
    
    def extract_content(self, soup: BeautifulSoup) -> str:
        """
        Extract and convert HTML content to Markdown.
        
        Args:
            soup: BeautifulSoup object of the HTML file
            
        Returns:
            Clean Markdown content
        """
        # Find the article content
        article = soup.find('article')
        if not article:
            # Fallback to body if no article tag
            article = soup.find('body')
        
        if not article:
            print("Warning: No article or body content found")
            return ""
        
        # Remove navigation elements and metadata
        for element in article.find_all(['span'], class_=['author', 'date']):
            element.decompose()
        
        # Remove navigation links
        for nav_span in article.find_all('span'):
            if nav_span.find('a') and ('Home' in nav_span.get_text() or 'Blog' in nav_span.get_text()):
                nav_span.decompose()
        
        # Remove the title h1 (we'll add it in frontmatter)
        h1 = article.find('h1')
        if h1:
            h1.decompose()
        
        # Remove hr after title
        hr = article.find('hr')
        if hr:
            hr.decompose()
        
        # Convert remaining content to markdown
        content_html = str(article)
        markdown_content = self.h2t.handle(content_html)
        
        # Clean up the markdown
        markdown_content = self.clean_markdown(markdown_content)
        
        return markdown_content
    
    def clean_markdown(self, content: str) -> str:
        """
        Clean up converted Markdown content.
        
        Args:
            content: Raw Markdown content
            
        Returns:
            Cleaned Markdown content
        """
        # Remove excessive newlines
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # Remove any remaining HTML tags
        content = re.sub(r'<[^>]+>', '', content)
        
        # Clean up whitespace
        content = content.strip()
        
        return content
    
    def create_frontmatter(self, metadata: Dict[str, str]) -> str:
        """
        Generate YAML frontmatter from metadata.
        
        Args:
            metadata: Dictionary with post metadata
            
        Returns:
            YAML frontmatter string
        """
        frontmatter = "---\n"
        frontmatter += f'title: "{metadata["title"]}"\n'
        frontmatter += f'date: {metadata["date"]}\n'
        frontmatter += f'slug: {metadata["slug"]}\n'
        frontmatter += f'category: {metadata["category"]}\n'
        frontmatter += 'published: true\n'
        frontmatter += "---\n\n"
        
        return frontmatter
    
    def migrate_file(self, html_file: Path) -> bool:
        """
        Migrate a single HTML file to Markdown.
        
        Args:
            html_file: Path to HTML file
            
        Returns:
            True if migration successful, False otherwise
        """
        try:
            print(f"Migrating: {html_file.name}")
            
            # Read HTML file
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Parse HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract metadata
            metadata = self.extract_metadata(soup, html_file.name)
            
            # Extract content
            content = self.extract_content(soup)
            
            # Generate frontmatter
            frontmatter = self.create_frontmatter(metadata)
            
            # Create markdown file
            markdown_filename = f"{metadata['slug']}.md"
            markdown_path = self.output_dir / markdown_filename
            
            # Check if file already exists
            if markdown_path.exists():
                response = input(f"File {markdown_filename} already exists. Overwrite? (y/N): ")
                if response.lower() != 'y':
                    print(f"Skipped: {html_file.name}")
                    return False
            
            # Write markdown file
            with open(markdown_path, 'w', encoding='utf-8') as f:
                f.write(frontmatter)
                f.write(content)
            
            print(f"Created: {markdown_path}")
            print(f"  Title: {metadata['title']}")
            print(f"  Date: {metadata['date']}")
            print(f"  Category: {metadata['category']}")
            print()
            
            return True
            
        except Exception as e:
            print(f"Error migrating {html_file.name}: {str(e)}")
            return False
    
    def migrate_all(self) -> None:
        """Migrate all HTML files in the migrate_html directory."""
        if not self.html_dir.exists():
            print(f"Error: Directory {self.html_dir} does not exist")
            return
        
        html_files = list(self.html_dir.glob('*.html'))
        
        if not html_files:
            print(f"No HTML files found in {self.html_dir}")
            return
        
        print(f"Found {len(html_files)} HTML files to migrate")
        print()
        
        success_count = 0
        
        for html_file in html_files:
            if self.migrate_file(html_file):
                success_count += 1
        
        print(f"Migration complete: {success_count}/{len(html_files)} files migrated successfully")
        
        if success_count > 0:
            print()
            print("Next steps:")
            print("1. Review the generated markdown files in content/posts/")
            print("2. Make any necessary edits")
            print("3. Run 'python generator.py build' to regenerate the site")


def main():
    """Main entry point for the HTML migration script."""
    print("HTML to Markdown Migration Tool")
    print("=" * 40)
    print()
    
    migrator = HTMLMigrator()
    migrator.migrate_all()


if __name__ == '__main__':
    main()