"""
Content processing module for markdown files with YAML frontmatter.

This module handles reading markdown files, parsing YAML frontmatter metadata,
converting markdown to HTML, and creating content objects with all necessary
metadata for template rendering.
"""

import os
import re
import yaml
import mistune
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

from config import Config


@dataclass
class ContentItem:
    """
    Represents a single piece of content (post, essay, or page).
    
    This dataclass holds all metadata and content for a single markdown file,
    including parsed frontmatter, HTML content, and computed properties like
    URL paths and formatted dates.
    
    Attributes:
        title: Content title from frontmatter
        content: Rendered HTML content
        date: Publication date (datetime object)
        slug: URL-friendly version of filename
        url: Full URL path for this content
        content_type: Type of content ('post', 'essay', 'page')
        published: Whether content should be published (default: True)
        external_url: Optional external link (for essays/journalism)
        category: Content category for organization (default: 'uncategorized')
        metadata: All other frontmatter data
        source_file: Original markdown file path
    """
    title: str
    content: str
    date: Optional[datetime] = None
    slug: str = ""
    url: str = ""
    content_type: str = "post"
    published: bool = True
    external_url: Optional[str] = None
    category: str = "uncategorized"
    metadata: Dict[str, Any] = field(default_factory=dict)
    source_file: str = ""
    
    def __post_init__(self):
        """Post-initialization processing to set computed properties."""
        if not self.slug and self.source_file:
            # Generate slug from filename (remove extension, make URL-friendly)
            self.slug = self._generate_slug()
        
        if not self.url:
            # Generate URL path based on content type and slug
            self.url = self._generate_url()
    
    def _generate_slug(self) -> str:
        """
        Generate a URL-friendly slug from the source filename or use custom slug from frontmatter.
        
        Returns:
            str: URL-safe slug (lowercase, hyphens instead of spaces/underscores)
        """
        # Check if a custom slug is provided in metadata (for URL preservation)
        if self.metadata and 'slug' in self.metadata:
            custom_slug = self.metadata['slug']
            # Clean the custom slug (remove .html extension if present)
            return custom_slug.replace('.html', '')
        
        # Generate from filename as fallback
        filename = os.path.basename(self.source_file)
        name = os.path.splitext(filename)[0]  # Remove extension
        # Convert to lowercase and replace non-alphanumeric chars with hyphens
        slug = re.sub(r'[^a-zA-Z0-9]+', '-', name.lower())
        return slug.strip('-')
    
    def _generate_url(self) -> str:
        """
        Generate the full URL path for this content item.
        
        Returns:
            str: URL path (e.g., "/posts/my-post-title/")
        """
        if self.content_type == "page":
            return f"/{self.slug}/"
        else:
            return f"/{self.content_type}/{self.slug}/"
    
    @property
    def formatted_date(self) -> str:
        """
        Get formatted date string for display.
        
        Returns:
            str: Formatted date string using CONFIG.DATE_FORMAT
        """
        if self.date:
            return self.date.strftime(Config.DATE_FORMAT)
        return ""


class ContentProcessor:
    """
    Processes markdown files with YAML frontmatter into ContentItem objects.
    
    This class handles the complete pipeline of reading markdown files,
    parsing frontmatter metadata, converting markdown to HTML using Mistune,
    and creating structured ContentItem objects for template rendering.
    """
    
    def __init__(self):
        """Initialize the content processor with markdown renderer."""
        # Create Mistune markdown processor with syntax highlighting
        self.markdown = mistune.create_markdown(
            renderer=mistune.HTMLRenderer(),
            plugins=['strikethrough', 'footnotes', 'table']
        )
    
    def process_file(self, file_path: str, content_type: str) -> Optional[ContentItem]:
        """
        Process a single markdown file into a ContentItem.
        
        Reads the file, parses YAML frontmatter, converts markdown to HTML,
        and creates a ContentItem with all metadata and content.
        
        Args:
            file_path: Path to the markdown file
            content_type: Type of content ('post', 'essay', 'page')
            
        Returns:
            ContentItem object or None if file cannot be processed
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Parse frontmatter and content
            frontmatter, markdown_content = self._parse_frontmatter(content)
            
            # Convert markdown to HTML
            html_content = self.markdown(markdown_content)
            
            # Handle title for micro posts (no title required)
            if content_type == 'micro':
                title = frontmatter.get('title', '')  # Empty title for micro posts
            else:
                title = frontmatter.get('title', 'Untitled')
            
            # Create ContentItem with parsed data
            item = ContentItem(
                title=title,
                content=html_content,
                date=self._parse_date(frontmatter.get('date')),
                content_type=content_type,
                published=frontmatter.get('published', True),
                external_url=frontmatter.get('external_url'),
                category=frontmatter.get('category', 'uncategorized'),
                metadata=frontmatter,
                source_file=file_path
            )
            
            return item
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return None
    
    def _parse_frontmatter(self, content: str) -> tuple[Dict[str, Any], str]:
        """
        Parse YAML frontmatter from markdown content.
        
        Extracts YAML frontmatter (between --- delimiters) and separates
        it from the actual markdown content.
        
        Args:
            content: Raw file content with frontmatter
            
        Returns:
            Tuple of (frontmatter_dict, markdown_content)
        """
        # Pattern to match YAML frontmatter (--- at start and end)
        frontmatter_pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
        match = re.match(frontmatter_pattern, content, re.DOTALL)
        
        if match:
            # Parse YAML frontmatter
            yaml_content = match.group(1)
            markdown_content = match.group(2)
            
            try:
                frontmatter = yaml.safe_load(yaml_content) or {}
            except yaml.YAMLError as e:
                print(f"Error parsing YAML frontmatter: {e}")
                frontmatter = {}
        else:
            # No frontmatter found
            frontmatter = {}
            markdown_content = content
        
        return frontmatter, markdown_content
    
    def _parse_date(self, date_value: Any) -> Optional[datetime]:
        """
        Parse date from frontmatter into datetime object.
        
        Supports multiple date formats and converts to the configured timezone.
        
        Args:
            date_value: Date value from frontmatter (string, datetime, or None)
            
        Returns:
            datetime object in configured timezone or None
        """
        if not date_value:
            return None
        
        if isinstance(date_value, datetime):
            # Already a datetime object
            dt = date_value
        elif isinstance(date_value, str):
            # Parse string date - try multiple formats
            date_formats = [
                '%Y-%m-%d',           # 2024-01-15
                '%Y-%m-%d %H:%M:%S',  # 2024-01-15 10:30:00
                '%Y/%m/%d',           # 2024/01/15
                '%d/%m/%Y',           # 15/01/2024
            ]
            
            dt = None
            for fmt in date_formats:
                try:
                    dt = datetime.strptime(date_value, fmt)
                    break
                except ValueError:
                    continue
            
            if dt is None:
                print(f"Could not parse date: {date_value}")
                return None
        else:
            # Handle date objects from YAML
            import datetime as dt_module
            if hasattr(date_value, 'year'):
                # Convert date object to datetime
                dt = dt_module.datetime.combine(date_value, dt_module.time())
            else:
                return None
        
        # Convert to configured timezone if naive datetime
        if dt.tzinfo is None:
            dt = Config.TIMEZONE.localize(dt)
        
        return dt
    
    def process_directory(self, directory: str, content_type: str) -> List[ContentItem]:
        """
        Process all markdown files in a directory.
        
        Recursively finds all markdown files in the directory and processes
        them into ContentItem objects, filtering out unpublished content.
        
        Args:
            directory: Path to directory containing markdown files
            content_type: Type of content for all files in directory
            
        Returns:
            List of ContentItem objects, sorted by date (newest first)
        """
        items = []
        
        if not os.path.exists(directory):
            return items
        
        # Find all markdown files recursively
        for root, dirs, files in os.walk(directory):
            for file in files:
                if any(file.lower().endswith(ext) for ext in Config.MARKDOWN_EXTENSIONS):
                    file_path = os.path.join(root, file)
                    item = self.process_file(file_path, content_type)
                    
                    # Only include published content
                    if item and item.published:
                        items.append(item)
        
        # Sort by date (newest first), then by title
        items.sort(key=lambda x: (x.date or datetime.min, x.title), reverse=True)
        
        return items